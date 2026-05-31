"""
Независимый recall-роутер с трёхслойной защитой на основе русской грамматики.

Используется gateway/run.py через _recall_route(), в будущем — CLI.

Слои защиты (в порядке быстродействия):
  Слой 0: синтаксический — < 3 слов без имени собственного → skip (бесплатно)
  Слой 1: грамматический — стоп-словарь по классам слов (междометия,
          односложные ответы, фатические фразы) → skip (O(1) словарь, ~16KB)
  Слой 2: дисперсия эмбеддинга — адаптивный порог по длине сообщения,
          дополнительная проверка top1_sim < 0.4 → skip (быстрый search_clusters)
  Слой 3: штатный recall — пороги 0.7 auto_switch, 0.5 clarify (pgvector, дорогой)

Все слои кроме третьего работают без LLM. Курация стоп-словаря — cron раз в неделю
через дешёвую LLM (DeepSeek v4-flash, без thinking).
"""

import json
import os
import re
from typing import List, Literal, Optional, Tuple

Decision = Literal["auto_switch", "clarify", "continue", "skip"]

# ── Paths ──────────────────────────────────────────────────────────────────

RECALL_BASE = os.path.join(
    os.environ.get("HERMES_HOME", "/home/mia/.hermes"),
    "skills", "recall",
)

# ── Helpers ────────────────────────────────────────────────────────────────

_CYRILLIC_LATIN_DIGIT = re.compile(r"[а-яёa-z0-9]+")


def msg_words(msg: str) -> int:
    """Количество слов в сообщении (кириллица + латиница + цифры)."""
    return len(_CYRILLIC_LATIN_DIGIT.findall(msg.lower()))


def has_proper_noun(msg: str, whitelist: List[str]) -> bool:
    """Содержит ли сообщение имя собственное из белого списка."""
    low = msg.lower()
    return any(noun in low for noun in whitelist)


def load_stop_words() -> dict:
    """Загрузить стоп-словарь. Кешируется вызывающей стороной."""
    path = os.path.join(RECALL_BASE, "stop_words.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ── Layer 0: syntactic length ─────────────────────────────────────────────


def is_too_short(msg: str, whitelist: List[str]) -> bool:
    """Слой 0: < 3 слов без имени собственного — сообщение не несёт темы.

    В русском невозможно выразить тему в 1-2 словах, кроме случаев
    когда одно из этих слов — имя собственное из белого списка.
    Примеры:
        «давай» — 1 слово, skip (слой 0)
        «чиним bmw» — 2 слова, но bmw в whitelist → pass (слой 0 пропускает)
        «люфт в рулевом» — 3 слова → pass
    """
    return msg_words(msg) < 3 and not has_proper_noun(msg, whitelist)


# ── Layer 1: grammatical stop-words ───────────────────────────────────────


def is_stop_word(msg: str) -> bool:
    """Слой 1: грамматический стоп-словарь — три класса слов.

    Проверяет: междометия (ага, угу), односложные ответы (да, нет, ок),
    фатические фразы (как дела, доброе утро).

    Если сообщение содержит тематический текст помимо стоп-слова
    (ок, давай чинить BMW) — не фильтруем на этом слое, пропускаем дальше.
    """
    sw = load_stop_words()
    clean = msg.strip().lower().rstrip("?!.,;:()/\\")

    # Междометия — точное совпадение
    if clean in sw.get("interjections", []):
        return True

    # Односложные ответы — точное совпадение
    if clean in sw.get("single_word_responses", []):
        return True

    # Если сообщение многословное — стоп-фильтр не применяем
    # (даже если начинается с "ок" — дальше идёт тематический текст)
    # НО: фатические фразы проверяем ДО этого — они по определению многословные
    for phrase in sw.get("phatic_phrases", []):
        if phrase in clean:
            return True

    if msg_words(msg) > 2:
        return False

    return False


# ── Layer 2: adaptive dispersion ──────────────────────────────────────────


def is_diffuse(embedding, store, msg: str, threshold: float = 0.3, limit: int = 5) -> bool:
    """Слой 2: адаптивная проверка дисперсии эмбеддинга.

    Математический критерий: если разница между первым и вторым кандидатом
    слишком мала — сообщение «размазано» по темам, явного лидера нет.
    Порог адаптивен к длине сообщения.

    Дополнительно: если даже лучший кандидат имеет sim < 0.4,
    сообщение признаётся размытым независимо от разрыва.
    """
    clusters = store.search_clusters(embedding, threshold=threshold, limit=limit)

    if len(clusters) < 2:
        return False  # мало кандидатов — возможно, реальный сигнал

    top1_sim = clusters[0]["similarity"]
    top2_sim = clusters[1]["similarity"]
    diff = top1_sim - top2_sim

    # Если лучший кандидат очень слабый (< 0.45) — темы просто нет в БД,
    # это не размытость. Пропускаем в слой 3, который скажет continue.
    if top1_sim < 0.45:
        return False

    # Если лучший кандидат имеет sim > 0.5 — тема определена,
    # не считаем размытым даже при маленьком разрыве
    if top1_sim > 0.5:
        return False

    # Адаптивный порог по длине сообщения
    length = len(msg)

    if length < 30:
        # Короткие сообщения — жёстче: нужен явный лидер
        return diff < 0.25
    elif length <= 100:
        # Средние — базовый порог
        return diff < 0.15
    else:
        # Длинные — мягче: больше текста = больше сигнала
        return diff < 0.10


# ── Decision tree ──────────────────────────────────────────────────────────


def decide(
    user_message: str,
    embedding,
    store,
    current_session_id: str,
) -> Tuple[Decision, Optional[dict]]:
    """Принимает решение о переключении сессии.

    Returns:
        (decision, context_or_None)
          - "skip" — остаться в текущей сессии (слои 0-2 отсекли)
          - "auto_switch" — автоматически переключиться (sim > 0.7)
          - "clarify" — уточнить у пользователя (0.5 < sim <= 0.7)
          - "continue" — продолжить в текущей (нет кандидатов или sim < 0.5)
    """
    sw = load_stop_words()
    whitelist = sw.get("proper_nouns_whitelist", [])

    # Слой 0: синтаксическая проверка (бесплатно)
    if is_too_short(user_message, whitelist):
        return ("skip", None)

    # Слой 1: стоп-словарь (O(1), не дёргает pgvector)
    if is_stop_word(user_message):
        return ("skip", None)

    # Слой 2: дисперсия эмбеддинга (лёгкий search_clusters с низким порогом)
    if is_diffuse(embedding, store, user_message):
        return ("skip", None)

    # Слой 3: штатный recall (полный search_clusters)
    clusters = store.search_clusters(embedding, threshold=0.5, limit=10)
    candidates = [c for c in clusters if c["session_id"] != current_session_id]

    if not candidates:
        return ("continue", None)

    top = candidates[0]
    sim = top["similarity"]

    if sim >= 0.7:
        return ("auto_switch", top)
    elif sim >= 0.5:
        return ("clarify", top)
    else:
        return ("continue", None)
