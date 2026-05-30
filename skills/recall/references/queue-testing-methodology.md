# Методика тестирования очереди инкрементального чанкера

**Дата:** 2026-05-30
**Сессия:** Born_Mia (20260527_012044_81b255ae)

## Контекст

Инкрементальный чанкер работает через `_feed_chunk_queue()` в gateway/run.py. Очередь накапливает тексты (ответы агента) и каждые 10 запускает daemon-поток. Тест нужен чтобы проверить, что кластеры реально создаются в `session_clusters`.

## Процедура

1. **Очистить таблицу** (опционально, для чистоты):
   ```sql
   DELETE FROM session_clusters;
   ```

2. **Написать 10 осмысленных сообщений** боту в Telegram. Не «привет как дела», а реальные вопросы из разных доменов:
   - BMW E39 (тормоза, VANOS)
   - DevOps (Docker, Proxmox)
   - AI (reasoning, recall)
   - Кулинария
   - Фильмы
   - и т.д.

3. **НЕ использовать /new, /reset, перезапуски gateway.** Просто живой диалог.

4. **После 10-го сообщения** — проверить pgvector:
   ```bash
   sudo -u postgres psql -d hermes_recall -c "SELECT id, cluster_title, message_range_start, message_range_end FROM session_clusters ORDER BY id;"
   ```

5. **Ожидаемый результат:** 1+ кластеров с заполненными `message_range_start/end`.

6. **Если 0 кластеров или пустые message_range** — баг. Проверить логи gateway: `grep chunk /home/mia/.hermes/logs/gateway.log`.

## Результаты (30.05.2026)

- 10 сообщений написано (темы: BMW, фичи Мии, конкуренты, recall, железо, память Hermes, фильмы, тулзы, .env)
- `session_clusters`: только 1 кластер (автосохранение при первом сообщении, message_range пустой)
- Логи gateway: пусто (ни одной строки с "chunk")
- **Диагноз:** `_bg_chunk_async_incremental` вызывает `chunk_session.py` с флагами `--mode incremental --texts`, которых нет в argparse скрипта. Скрипт падает, `except Exception: pass` глотает.
- **Исправление:** handoff `chunker-cli-mismatch.md` — добавить `--mode incremental --texts` в `chunk_session.py`.
