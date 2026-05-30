#!/usr/bin/env python3
"""
Список всех активных сессий в pgvector.

Использование:
  python list_sessions.py

Вывод: JSON-массив [{session_id, topic, message_count, created_at, updated_at}, ...]
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from recall import load_config, PgVectorStore


def main():
    config = load_config()
    store = PgVectorStore(config["postgresql"])

    sessions = store.list_active_sessions()

    print(json.dumps(sessions, ensure_ascii=False, indent=2))

    store.close()


if __name__ == "__main__":
    main()
