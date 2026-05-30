# Баги инкрементального чанкера — раунд 3 (30.05.2026, не исправлены)

## Статус

После фикса close-няшкой (01:15) проведён второй тест-драйв. Чанкер сработал, но:

- Создан **1 кластер** вместо 2-3 (cold start слепил все 10 текстов)
- `message_range_start/end` = NULL
- Title = "1. Как работает CONTEXT COMPACTION ?" (сырой текст, DeepSeek API упал)

## Баг 2 (продолжение): msg_indices не передаются из main

`chunk_session.py` строка 276:
```python
incremental_chunk(args.session_id, texts, store, embedder)
```
Нет передачи `msg_indices`. Сигнатура принимает, код внутри корректный, но main не передаёт.

**Fix:** `incremental_chunk(..., msg_indices=list(range(len(texts))))`

## Баг 4 (новый): Cold start = 1 кластер

Строки 104-119: если `existing` пуст → создаётся ОДИН кластер со средним эмбеддингом всех текстов.

10 разнородных сообщений должны дать 2-3 кластера.

**Fix:** вызвать `compute_boundaries()` для разбивки (уже есть в коде для full mode).

## Баг 3 (продолжение): DeepSeek API падает

`_annotate_incremental_cluster()` → fallback `texts[0][:80]`. Причины:
- Захардкоженный ключ (строка 51) может быть неактуален
- Thinking не отключён: нужно `"thinking": {"type": "disabled"}`
- Или v4-flash недоступен на этом ключе

## Новая архитектура: single-message очередь (отказ от batch=10)

Нагрузка на Ollama от batch=10 — низкая. Batch не оправдан.

**Решение:** заменить batch-очередь на single-message очередь:
- Каждое новое сообщение → очередь
- Воркер разбирает по одному с паузами
- Нет проблемы cold start (первый текст = первый кластер, дальше centroid matching)
- `_feed_chunk_queue` → `_feed_single_queue`
- `CHUNK_BATCH_SIZE = 1`

**Файлы:** gateway/run.py, chunk_session.py
