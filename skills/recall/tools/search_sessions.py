#!/usr/bin/env python3
"""
Поиск ближайших сессий по pgvector.

Использование:
  python search_sessions.py "текст запроса" --threshold 0.5 --limit 3 [--current-session SID]

Вывод: JSON-массив кандидатов [{session_id, topic, similarity, message_count, updated_at}, ...]
"""

import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from recall import load_config, EmbeddingClient, PgVectorStore, RecallEngine


def main():
    parser = argparse.ArgumentParser(description="Поиск ближайших сессий по pgvector")
    parser.add_argument("query", help="Текст запроса")
    parser.add_argument("--threshold", type=float, default=0.5, help="Минимальный порог cosine similarity (default: 0.5)")
    parser.add_argument("--limit", type=int, default=3, help="Максимум кандидатов (default: 3)")
    parser.add_argument("--current-session", dest="current_session", default=None, help="ID текущей сессии")
    args = parser.parse_args()

    config = load_config()
    embedder = EmbeddingClient(config["ollama"]["url"], config["ollama"]["model"])
    store = PgVectorStore(config["postgresql"])
    engine = RecallEngine(config, store, embedder)

    result = engine.analyze(args.query, args.current_session)

    # фильтруем candidates: убираем текущую сессию из кандидатов
    candidates = result.get("candidates", [])
    if args.current_session:
        candidates = [c for c in candidates if c["session_id"] != args.current_session]

    print(json.dumps(candidates, ensure_ascii=False, indent=2))

    store.close()


if __name__ == "__main__":
    main()
