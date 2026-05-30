#!/usr/bin/env python3
"""
Сохранить embedding новой сессии в pgvector.

Использование:
  python save_session.py --session-id SID --topic "Тема" --text "Текст для векторизации"

Вывод: JSON {"status": "saved", "session_id": "..."}
"""

import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from recall import load_config, EmbeddingClient, PgVectorStore, RecallEngine


def main():
    parser = argparse.ArgumentParser(description="Сохранить embedding новой сессии")
    parser.add_argument("--session-id", required=True, help="ID сессии Hermes")
    parser.add_argument("--topic", required=True, help="Название темы")
    parser.add_argument("--text", required=True, help="Текст для векторизации (первое сообщение)")
    args = parser.parse_args()

    config = load_config()
    embedder = EmbeddingClient(config["ollama"]["url"], config["ollama"]["model"])
    store = PgVectorStore(config["postgresql"])
    engine = RecallEngine(config, store, embedder)

    engine.save_session(args.session_id, args.topic, args.text)

    print(json.dumps({"status": "saved", "session_id": args.session_id, "topic": args.topic}, ensure_ascii=False))

    store.close()


if __name__ == "__main__":
    main()
