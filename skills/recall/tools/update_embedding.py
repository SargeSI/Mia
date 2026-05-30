#!/usr/bin/env python3
"""
Обновить embedding сессии скользящим средним по новому сообщению.

Использование:
  python update_embedding.py --session-id SID --text "Текст нового сообщения"

Вывод: JSON {"status": "updated", "session_id": "...", "message_count": 5}
"""

import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from recall import load_config, EmbeddingClient, PgVectorStore, RecallEngine


def main():
    parser = argparse.ArgumentParser(description="Обновить embedding сессии")
    parser.add_argument("--session-id", required=True, help="ID сессии Hermes")
    parser.add_argument("--text", required=True, help="Текст нового сообщения")
    args = parser.parse_args()

    config = load_config()
    embedder = EmbeddingClient(config["ollama"]["url"], config["ollama"]["model"])
    store = PgVectorStore(config["postgresql"])
    engine = RecallEngine(config, store, embedder)

    result = engine.update_session_embedding(args.session_id, args.text)

    if result is None:
        print(json.dumps({"status": "error", "reason": "session_not_found", "session_id": args.session_id}, ensure_ascii=False))
        store.close()
        sys.exit(1)

    print(json.dumps({"status": "updated", "session_id": args.session_id, "message_count": result["message_count"]}, ensure_ascii=False))

    store.close()


if __name__ == "__main__":
    main()
