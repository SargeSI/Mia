# Single-message чанкер — итоги реализации

**Дата:** 30.05.2026
**Реализовано:** близняшкой (Cursor-Мия)
**Handoff:** `Mia/handoff/handoff_20260530_single_msg.md`

## Архитектура

```
_feed_chunk_queue(sid, text, msg_index) → deque.append((sid, text, idx))
_start_chunk_worker() — daemon-поток
    ↓ pop-left из deque
_bg_chunk_single(sid, text, msg_index)
    ↓ subprocess --single --text "..." --msg-index N
chunk_session.py --single
    ↓ batch_embed([text]) → centroid matching
```

## Что заменило

- `_chunk_queue: dict[str, list[str]]` → `collections.deque`
- `_bg_chunk_async_incremental` (batch) → `_bg_chunk_single` (single)
- `_CHUNK_BATCH_SIZE = 10` → удалён
- `--texts-stdin` → `--single --text "..." --msg-index N`

## Решённые проблемы

1. Cold start больше не склеивает 10 текстов в один кластер
2. msg_index передаётся из gateway (глобальный счётчик `_chunk_msg_counter`)
3. Title/summary через DeepSeek работает (JSON-промпт исправлен)

## Инцидент: UnboundLocalError

Две итерации исправления: `global _chunk_msg_counter` нужен в ОБЕИХ `run_sync()` — и в `_run_agent_via_proxy`, и в `_run_agent`. Урок: grep'ать все точки использования модульных переменных перед деплоем.
