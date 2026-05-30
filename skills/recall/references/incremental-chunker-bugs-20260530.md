# Баги инкрементального чанкера — обнаружены и частично исправлены 30.05.2026

> **⚠️ Устарело: второй тест-драйв показал неполный фикс. Актуальные баги — `references/incremental-chunker-bugs-round3.md`**

## Хронология

| Время | Событие |
|---|---|
| 00:25 | Gateway перезапущен после фикса CLI mismatch |
| 00:49 | Очередь набрала 10 сообщений, чанкер отработал — 12 кластеров |
| 00:55 | Обнаружено: кластеры — мусор (reasoning-блоки, нет range, сырой текст) |
| 01:00 | Handoff `incremental-chunker-3-bugs.md` написан Мией |
| 01:15 | Handoff `handoff_20260530_3bugs_fixed.md` — близняшка всё починила |

## Данные из БД (до фикса)

```sql
SELECT id, cluster_title, message_range_start, message_range_end 
FROM session_clusters WHERE session_id = '20260527_012044_81b255ae';
```

| id | cluster_title | range |
|----|--------------|-------|
| 10 | 💭 **Reasoning:** ... Сергей начинает новый тест-драйв... | NULL |
| 11 | 💭 **Reasoning:** ... Второе тестовое сообщение... | NULL |
| 12 | 💭 **Reasoning:** ... Третье тестовое сообщение... | NULL |
| 13 | Нет, мотоциклов в сессиях нет... | NULL |
| 14 | 💭 **Reasoning:** ... Нашёлся! Два совпадения в LightRAG... | NULL |
| 15 | 200 тысяч на одном мотоцикле — это не просто пробег... | NULL |

Все 12 кластеров — отдельные сообщения (не группы), reasoning-блоки как заголовки, range — NULL.

## Корень проблем

1. `_feed_chunk_queue(session_id, last_response[:1000])` — только ответы ассистента, включая 💭 reasoning
2. `insert_cluster()` в incremental mode без msg_start/msg_end
3. `texts[i][:80]` вместо LLM-заголовка

## Что исправлено (close-няшка)

### gateway/run.py
- Строки 17283-17289: user-сообщение → `_feed_chunk_queue(sid, f"user: {text[:500]}")` перед run_conversation
- Строки 17293-17297: assistant-ответ → `_feed_chunk_queue(sid, f"assistant: {clean_text[:500]}")` после, reasoning вырезан regex'ом
- Дублирующий вызов из `_bg_update_embedding_async` убран

### chunk_session.py
- `incremental_chunk()` принимает `msg_indices: list[int]`
- `_annotate_incremental_cluster(texts)` — DeepSeek v4-flash для title/summary
- Cold start: `msg_start=indices[0], msg_end=indices[-1]`
- Merge: `msg_end` обновляется у существующего кластера
- Fallback на `texts[i][:80]` при сбое API
