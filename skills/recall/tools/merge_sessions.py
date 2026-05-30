#!/usr/bin/env python3
"""
Soft merge двух сессий:
  - Удалить from-сессию из pgvector
  - Обновить embedding to-сессии средним по обеим

Использование:
  python merge_sessions.py --from-sid NEW_SID --to-sid OLD_SID

Вывод: JSON {"status": "merged", "from": "NEW_SID", "to": "OLD_SID"}
"""

import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from recall import load_config, EmbeddingClient, PgVectorStore, RecallEngine


def main():
    parser = argparse.ArgumentParser(description="Soft merge двух сессий")
    parser.add_argument("--from-sid", required=True, help="ID сессии для удаления")
    parser.add_argument("--to-sid", required=True, help="ID сессии для обновления")
    args = parser.parse_args()

    config = load_config()
    embedder = EmbeddingClient(config["ollama"]["url"], config["ollama"]["model"])
    store = PgVectorStore(config["postgresql"])
    engine = RecallEngine(config, store, embedder)

    ok = engine.soft_merge(args.from_sid, args.to_sid)

    if not ok:
        print(json.dumps({"status": "error", "reason": "both_sessions_not_found"}, ensure_ascii=False))
        store.close()
        sys.exit(1)

    print(json.dumps({"status": "merged", "from": args.from_sid, "to": args.to_sid}, ensure_ascii=False))

    store.close()


if __name__ == "__main__":
    main()
