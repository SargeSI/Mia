# Recall Testing Procedure

## Quick smoke test

```bash
cd /home/mia/.hermes/skills/recall
VENV=/home/mia/.hermes/hermes-agent/venv/bin/python3

# 1. Save current session
$VENV tools/save_session.py --session-id "Born_Mia" --topic "Test Topic" --text "Description of what this session is about"

# 2. Search for related topic (different words)
$VENV tools/search_sessions.py "semantically related query in different words" --threshold 0.3

# 3. Search for unrelated topic (should find other session, not this one)
$VENV tools/search_sessions.py "completely different topic" --threshold 0.3

# 4. Update embedding with new context
$VENV tools/update_embedding.py --session-id "Born_Mia" --text "new context to shift the embedding"

# 5. Verify sim improved after update
$VENV tools/search_sessions.py "original query" --threshold 0.3
```

## Test results (2026-05-29)

| Test | Query | Expected | Result |
|------|-------|----------|--------|
| Same topic, diff words | "как настроить режим размышлений у ассистента" | Born_Mia | ✅ sim 0.67 |
| Different topic | "сколько ещё пирогу осталось" | Кулинария (not Born_Mia) | ✅ sim 0.57 |
| After embedding update | "как модель думает над сложными вопросами" | Born_Mia still #1 | ✅ sim 0.63 |

Key takeaway: recall correctly distinguishes topics. "Thinking mode" query finds reasoning session, "pie" query finds cooking session. No crossover.

## What worked

- Embedding update (sliding average) improved sim from 0.43 → 0.52 in test_recall.py
- Search correctly ranks sessions by semantic similarity
- Thresholds: 0.5-0.7 clarify zone, >0.7 auto-switch, <0.5 new topic
- Soft merge: deletes new session from pgvector, updates old embedding

## Infrastructure verified

- PostgreSQL 15 + pgvector 0.7.4 on localhost:5432
- Database: hermes_recall, user: mia
- Table: recall_sessions (session_id, topic, embedding vector(1024))
- Ollama: 192.168.51.17:11434, model qwen3-embedding:0.6b
- Venv: /home/mia/.hermes/hermes-agent/venv/bin/python3
- Dependencies: psycopg2-binary, numpy, requests (installed)
