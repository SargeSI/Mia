
"""
Recall — кросс-сессионный контекстный движок для Hermes Agent.

Три компонента:
  - EmbeddingClient: HTTP-запросы к Ollama embedding API (qwen3-embedding:0.6b, 1024 dim)
  - PgVectorStore: PostgreSQL + pgvector — поиск, вставка, обновление, удаление сессий
  - RecallEngine: дерево решений (пороги >0.7 / 0.5-0.7 / <0.5), холодный старт, временное окно

Все параметры — из recall_config.json в той же директории.
"""

import json
import os
from datetime import datetime, timezone
from typing import Optional

import numpy as np
import psycopg2
import requests

# ── config ──────────────────────────────────────────────────────────────────

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recall_config.json")


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ── EmbeddingClient ─────────────────────────────────────────────────────────


class EmbeddingClient:
    """Векторизация текста через Ollama API."""

    def __init__(self, url: str, model: str, timeout: int = None, batch_timeout: int = None):
        self.url = url
        self.model = model
        self.timeout = timeout or 30
        self.batch_timeout = batch_timeout or 120


    def batch_embed(self, texts: list[str]) -> list[list[float]]:
        """Векторизовать несколько текстов одним запросом (Ollama /api/embed)."""
        batch_url = self.url.replace("/api/embeddings", "/api/embed")
        resp = requests.post(
            batch_url,
            json={"model": self.model, "input": texts},
            timeout=self.batch_timeout,
        )
        resp.raise_for_status()
        return resp.json()["embeddings"]


    def embed(self, text: str) -> list[float]:
        """Получить embedding текста. Возвращает список float размерности vector_dim."""
        payload = {"model": self.model, "prompt": text}
        resp = requests.post(self.url, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()["embedding"]


# ── PgVectorStore ───────────────────────────────────────────────────────────


class PgVectorStore:
    """Работа с PostgreSQL + pgvector: таблица recall_sessions.
    Все запросы — параметризованные (psycopg2 %s), без строковой интерполяции.
    """

    def __init__(self, pg_config: dict):
        self.table = pg_config.get("table", "recall_sessions")
        self.conn = psycopg2.connect(
            host=pg_config["host"],
            port=pg_config["port"],
            dbname=pg_config["database"],
            user=pg_config["user"],
            password=pg_config["password"],
        )
        self.conn.autocommit = False

    @staticmethod
    def _emb_str(embedding: list[float]) -> str:
        """Форматирует вектор как pgvector-литерал: '[0.1, 0.2, ...]'."""
        return "[" + ",".join(f"{v:.8f}" for v in embedding) + "]"

    @staticmethod
    def _parse_vector(raw) -> list[float] | None:
        """Парсит pgvector-строку '[1.0, 2.0, ...]' или None в list[float]."""
        if raw is None:
            return None
        if isinstance(raw, (list, tuple)):
            return list(raw)
        # psycopg2 без адаптера возвращает строку
        s = str(raw).strip()
        if s.startswith("[") and s.endswith("]"):
            inner = s[1:-1]
            if not inner:
                return None
            return [float(x.strip()) for x in inner.split(",")]
        return None

    def search_nearest(
        self, embedding: list[float], threshold: float, limit: int = 3
    ) -> list[dict]:
        """Найти топ-N ближайших сессий по cosine similarity."""
        emb_str = self._emb_str(embedding)
        sql = f"""
            SELECT session_id, topic, message_count, updated_at,
                   1 - (embedding <=> %s::vector) AS similarity
            FROM {self.table}
            WHERE 1 - (embedding <=> %s::vector) > %s
            ORDER BY similarity DESC
            LIMIT %s
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, (emb_str, emb_str, threshold, limit))
                rows = cur.fetchall()
            return [
                {
                    "session_id": r[0],
                    "topic": r[1],
                    "message_count": r[2],
                    "updated_at": r[3].isoformat() if r[3] else None,
                    "similarity": round(float(r[4]), 4),
                }
                for r in rows
            ]
        except Exception:
            self.conn.rollback()
            raise

    def insert_session(self, session_id: str, topic: str, embedding: list[float]) -> None:
        """Вставить новую сессию (upsert: если session_id уже есть — пропускаем)."""
        emb_str = self._emb_str(embedding)
        sql = f"""
            INSERT INTO {self.table} (session_id, topic, embedding)
            VALUES (%s, %s, %s::vector)
            ON CONFLICT (session_id) DO NOTHING
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, (session_id, topic, emb_str))
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def update_embedding(
        self, session_id: str, embedding: list[float]
    ) -> dict | None:
        """
        Обновить embedding сессии скользящим средним.
        Возвращает dict с новыми значениями или None, если сессия не найдена.
        """
        with self.conn.cursor() as cur:
            cur.execute(
                f"SELECT embedding, message_count FROM {self.table} WHERE session_id = %s",
                (session_id,),
            )
            row = cur.fetchone()
            if not row:
                return None

            old_emb_raw = self._parse_vector(row[0])
            old_emb = np.array(old_emb_raw, dtype=np.float32) if old_emb_raw else np.zeros(0)
            count = row[1] or 1

        new_emb = np.array(embedding, dtype=np.float32)

        if old_emb.size > 0:
            avg_emb = (old_emb * count + new_emb) / (count + 1)
        else:
            avg_emb = new_emb

        new_count = count + 1
        emb_str = self._emb_str(avg_emb.tolist())

        sql = f"""
            UPDATE {self.table}
            SET embedding = %s::vector,
                message_count = %s,
                updated_at = now()
            WHERE session_id = %s
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, (emb_str, new_count, session_id))
            self.conn.commit()
            return {"message_count": new_count, "updated_at": datetime.now(timezone.utc).isoformat()}
        except Exception:
            self.conn.rollback()
            raise

    def delete_session(self, session_id: str) -> None:
        """Удалить сессию из таблицы (для soft merge)."""
        sql = f"DELETE FROM {self.table} WHERE session_id = %s"
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, (session_id,))
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def list_active_sessions(self) -> list[dict]:
        """Все активные сессии, отсортированные по updated_at."""
        sql = f"""
            SELECT session_id, topic, message_count, created_at, updated_at
            FROM {self.table}
            ORDER BY updated_at DESC
        """
        with self.conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
        return [
            {
                "session_id": r[0],
                "topic": r[1],
                "message_count": r[2],
                "created_at": r[3].isoformat() if r[3] else None,
                "updated_at": r[4].isoformat() if r[4] else None,
            }
            for r in rows
        ]

    def get_session(self, session_id: str) -> dict | None:
        """Получить одну сессию по ID."""
        sql = f"""
            SELECT session_id, topic, message_count, created_at, updated_at
            FROM {self.table}
            WHERE session_id = %s
        """
        with self.conn.cursor() as cur:
            cur.execute(sql, (session_id,))
            row = cur.fetchone()
            if not row:
                return None
        return {
            "session_id": row[0],
            "topic": row[1],
            "message_count": row[2],
            "created_at": row[3].isoformat() if row[3] else None,
            "updated_at": row[4].isoformat() if row[4] else None,
        }

    def session_count(self) -> int:
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {self.table}")
            return cur.fetchone()[0]

    def get_embedding(self, session_id: str) -> list[float] | None:
        with self.conn.cursor() as cur:
            cur.execute(
                f"SELECT embedding FROM {self.table} WHERE session_id = %s",
                (session_id,),
            )
            row = cur.fetchone()
            if not row or row[0] is None:
                return None
            return self._parse_vector(row[0])

    def set_embedding_raw(self, session_id: str, embedding: list[float]) -> None:
        """Установить embedding напрямую (без скользящего среднего). Для soft merge."""
        emb_str = self._emb_str(embedding)
        sql = f"""
            UPDATE {self.table}
            SET embedding = %s::vector, updated_at = now()
            WHERE session_id = %s
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, (emb_str, session_id))
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise


    # ── session_clusters methods ────────────────────────────────────────

    def search_clusters(self, embedding: list[float], threshold: float,
                        limit: int = 10, max_age_days: int = None) -> list[dict]:
        """Поиск по session_clusters с опциональным фильтром по возрасту."""
        emb_str = self._emb_str(embedding)
        age_sql = ""
        params = [emb_str, emb_str, threshold, limit]
        if max_age_days is not None:
            age_sql = f"AND updated_at > NOW() - INTERVAL '{max_age_days} days'"
        sql = f"""
            SELECT id, session_id, cluster_title, cluster_summary,
                   message_range_start, message_range_end, updated_at,
                   1 - (embedding <=> %s::vector) AS similarity
            FROM session_clusters
            WHERE 1 - (embedding <=> %s::vector) > %s
            {age_sql}
            ORDER BY similarity DESC
            LIMIT %s
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
            return [
                {
                    "id": r[0],
                    "session_id": r[1],
                    "cluster_title": r[2],
                    "cluster_summary": r[3],
                    "msg_start": r[4],
                    "msg_end": r[5],
                    "updated_at": r[6].isoformat() if r[6] else None,
                    "similarity": round(float(r[7]), 4),
                }
                for r in rows
            ]
        except Exception:
            self.conn.rollback()
            raise

    def insert_cluster(self, session_id: str, title: str, summary: str,
                       embedding: list[float], msg_start: int = None,
                       msg_end: int = None) -> None:
        """Добавить один кластер в session_clusters."""
        emb_str = self._emb_str(embedding)
        sql = """
            INSERT INTO session_clusters
                (session_id, cluster_title, cluster_summary, embedding,
                 message_range_start, message_range_end)
            VALUES (%s, %s, %s, %s::vector, %s, %s)
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, (session_id, title, summary, emb_str, msg_start, msg_end))
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def clear_session_clusters(self, session_id: str) -> None:
        """Удалить все кластеры для сессии."""
        sql = "DELETE FROM session_clusters WHERE session_id = %s"
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, (session_id,))
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def has_session_clusters(self, session_id: str) -> bool:
        """Проверить, есть ли кластеры для сессии."""
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM session_clusters WHERE session_id = %s LIMIT 1",
                (session_id,),
            )
            return cur.fetchone() is not None

    def cluster_count(self) -> int:
        """Количество кластеров в БД."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM session_clusters")
            return cur.fetchone()[0]



    def get_clusters_with_embeddings(self, session_id: str) -> list[dict]:
        """Get all clusters for a session with their embeddings (for centroid matching)."""
        sql = """
            SELECT id, cluster_title, cluster_summary, embedding,
                   message_range_start, message_range_end, updated_at
            FROM session_clusters
            WHERE session_id = %s
            ORDER BY id
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, (session_id,))
                rows = cur.fetchall()
            result = []
            for r in rows:
                emb_raw = self._parse_vector(r[3])
                result.append({
                    "id": r[0],
                    "cluster_title": r[1],
                    "cluster_summary": r[2],
                    "embedding": emb_raw,
                    "msg_start": r[4],
                    "msg_end": r[5],
                    "updated_at": r[6].isoformat() if r[6] else None,
                })
            return result
        except Exception:
            self.conn.rollback()
            raise

    def update_cluster_embedding(
        self, cluster_id: int, embedding: list[float],
        msg_end: int = None, title: str = None, summary: str = None
    ) -> None:
        """Update cluster embedding and optionally other fields."""
        emb_str = self._emb_str(embedding)
        sets = ["embedding = %s::vector", "updated_at = now()"]
        params = [emb_str]
        if msg_end is not None:
            sets.append("message_range_end = %s")
            params.append(msg_end)
        if title is not None:
            sets.append("cluster_title = %s")
            params.append(title)
        if summary is not None:
            sets.append("cluster_summary = %s")
            params.append(summary)
        params.append(cluster_id)
        sql = f"UPDATE session_clusters SET {', '.join(sets)} WHERE id = %s"
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, params)
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise



    def log_decision(self, session_id: str, text: str, cluster_title: str,
                     sim: float, decision: str) -> None:
        """Log chunker decision to recall_decisions table."""
        sql = """
            INSERT INTO recall_decisions
                (session_id, text, cluster_title, sim, decision)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, (session_id, text, cluster_title, sim, decision))
            self.conn.commit()
        except Exception:
            self.conn.rollback()


    def close(self):
        self.conn.close()


# ── RecallEngine ────────────────────────────────────────────────────────────


class RecallEngine:
    """
    Дерево решений кросс-сессионного recall.

    Пороги:
      sim > auto_switch        → автоматическое переключение на сессию
      clarify_low < sim <= clarify_high → уточнение у пользователя
      sim <= clarify_low        → новая тема / продолжить в текущей
    """

    def __init__(self, config: dict, store: PgVectorStore, embedder: EmbeddingClient):
        self.config = config
        self.store = store
        self.embedder = embedder
        self.thresholds = config["thresholds"]
        self._last_manual_switch: dict[str, float] = {}

    def analyze(self, query_text: str, current_session_id: str | None = None) -> dict:
        """Проанализировать запрос и вернуть решение."""
        count = self.store.session_count()
        if count == 0:
            return {
                "action": "new",
                "candidates": [],
                "target_session": None,
                "reason": "cold_start",
                "dry": True,
            }

        if current_session_id and current_session_id in self._last_manual_switch:
            elapsed = datetime.now(timezone.utc).timestamp() - self._last_manual_switch[current_session_id]
            window = self.thresholds.get("manual_switch_window_seconds", 300)
            if elapsed < window:
                return {
                    "action": "continue",
                    "candidates": [],
                    "target_session": self.store.get_session(current_session_id),
                    "reason": f"manual_switch_window ({int(elapsed)}s < {window}s)",
                    "dry": False,
                }

        threshold = self.thresholds["auto_switch"]
        if count > self.thresholds.get("adaptive_session_count", 50):
            threshold = self.thresholds.get("adaptive_high_sessions", 0.85)

        query_emb = self.embedder.embed(query_text)
        candidates_raw = self.store.search_clusters(
            query_emb, self.thresholds["clarify_low"], limit=3, max_age_days=10
        )
        candidates = [
            {
                "session_id": c["session_id"],
                "topic": c["cluster_title"],
                "cluster_title": c["cluster_title"],
                "similarity": c["similarity"],
            }
            for c in candidates_raw
        ]

        if not candidates:
            return {
                "action": "new",
                "candidates": [],
                "target_session": None,
                "reason": f"no_matches_above_{self.thresholds['clarify_low']}",
                "dry": False,
            }

        top = candidates[0]
        sim = top["similarity"]

        if sim > threshold:
            return {
                "action": "switch",
                "candidates": candidates[:3],
                "target_session": top,
                "reason": f"auto_switch sim={sim:.4f} > {threshold}",
                "dry": False,
            }

        if sim <= self.thresholds["clarify_high"]:
            return {
                "action": "clarify",
                "candidates": candidates[:3],
                "target_session": None,
                "reason": f"clarify sim={sim:.4f} in ({self.thresholds['clarify_low']}, {self.thresholds['clarify_high']}]",
                "dry": False,
            }

        return {
            "action": "new",
            "candidates": [],
            "target_session": None,
            "reason": "fallback",
            "dry": False,
        }

    def register_manual_switch(self, session_id: str):
        self._last_manual_switch[session_id] = datetime.now(timezone.utc).timestamp()

    def save_session(self, session_id: str, topic: str, text: str):
        emb = self.embedder.embed(text)
        self.store.insert_session(session_id, topic, emb)

    def update_session_embedding(self, session_id: str, message_text: str) -> dict | None:
        emb = self.embedder.embed(message_text)
        return self.store.update_embedding(session_id, emb)

    def soft_merge(self, from_session_id: str, to_session_id: str) -> bool:
        from_emb = self.store.get_embedding(from_session_id)
        to_emb = self.store.get_embedding(to_session_id)

        if from_emb is None and to_emb is None:
            return False

        if from_emb is not None and to_emb is not None:
            avg = [((a + b) / 2.0) for a, b in zip(from_emb, to_emb)]
            self.store.set_embedding_raw(to_session_id, avg)
        elif from_emb is not None and to_emb is None:
            self.store.set_embedding_raw(to_session_id, from_emb)

        self.store.delete_session(from_session_id)
        return True
