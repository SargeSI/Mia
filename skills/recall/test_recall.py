#!/usr/bin/env python3
"""Самодостаточный тест recall-скилла. Запускается на сервере без аргументов."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recall import load_config, EmbeddingClient, PgVectorStore, RecallEngine

config = load_config()
store = PgVectorStore(config["postgresql"])
embedder = EmbeddingClient(config["ollama"]["url"], config["ollama"]["model"])

def step(label):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")

# ── очистка ──
step("Очистка таблицы")
with store.conn.cursor() as cur:
    cur.execute("DELETE FROM recall_sessions")
store.conn.commit()
print("OK: таблица очищена")

# ── создание сессий ──
step("Создание сессии 1: Кулинария")
engine1 = RecallEngine(config, store, embedder)
engine1.save_session("sess-cooking", "Кулинария", "Ищу рецепт яблочного пирога с корицей")
print("OK: sess-cooking сохранена")

step("Создание сессии 2: Форки агентов")
engine2 = RecallEngine(config, store, embedder)
engine2.save_session("sess-forks", "Форки агентов", "Сравнение архитектуры Hermes и OpenClaw")
print("OK: sess-forks сохранена")

# ── список ──
step("Список сессий")
sessions = store.list_active_sessions()
for s in sessions:
    print(f"  {s['session_id']}: {s['topic']} (msgs: {s['message_count']})")

# ── поиск ──
step("Поиск: 'Сколько ещё пирогу осталось в духовке?'")
query_emb = embedder.embed("Сколько ещё пирогу осталось в духовке?")
results = store.search_nearest(query_emb, 0.3, limit=3)
if results:
    for r in results:
        print(f"  {r['session_id']}: {r['topic']} (sim={r['similarity']:.4f})")
else:
    print("  Нет совпадений (странно — симилярность < 0.3)")

# пробуем ниже
results2 = store.search_nearest(query_emb, 0.0, limit=3)
print(f"\n  Порог 0.0 (все сессии по убыванию sim):")
for r in results2:
    print(f"    {r['session_id']}: {r['topic']} (sim={r['similarity']:.4f})")

# ── обновление embedding ──
step("Обновление embedding: 'Добавил в пирог яблоки и корицу'")
r1 = engine1.update_session_embedding("sess-cooking", "Добавил в пирог яблоки и корицу")
print(f"OK: message_count={r1['message_count']}")

step("Обновление embedding: 'Духовка 180 градусов, проверю через 20 минут'")
r2 = engine1.update_session_embedding("sess-cooking", "Духовка 180 градусов, проверю через 20 минут")
print(f"OK: message_count={r2['message_count']}")

# ── повторный поиск ──
step("Проверка поиска после обновления embedding")
results3 = store.search_nearest(query_emb, 0.0, limit=3)
for r in results3:
    print(f"  {r['session_id']}: {r['topic']} (sim={r['similarity']:.4f})")

# ── merge ──
step("Soft merge: sess-forks -> sess-cooking")
ok = engine1.soft_merge("sess-forks", "sess-cooking")
print(f"OK: merged={ok}")

step("Финальный список (должна остаться только sess-cooking)")
sessions2 = store.list_active_sessions()
for s in sessions2:
    print(f"  {s['session_id']}: {s['topic']} (msgs: {s['message_count']})")

store.close()
print(f"\n{'='*60}")
print("  ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
print(f"{'='*60}")
