# Cron Sync Workflow — MEMORY.md / USER.md / SOUL.md

Проверенный паттерн для cron-синхронизации личности Мии в LightRAG.

## Алгоритм (bash/python версия)

```
1. new_hash=$(md5sum /home/mia/Mia/memories/MEMORY.md | cut -d' ' -f1)
2. old_hash=$(cat /tmp/memory_hash.txt 2>/dev/null || echo "")
3. if [ "$new_hash" = "$old_hash" ]; then → No changes
4. else →
   a. content=$(cat /home/mia/Mia/memories/MEMORY.md)
   b. upload_text(text=content, filename="MEMORY-<date>.md")
   c. echo "$new_hash" > /tmp/memory_hash.txt
   d. Done
```

## Ключевые нюансы

### 1. upload_text с повторным filename → duplicated
При повторном использовании `filename="MEMORY.md"` LightRAG возвращает `duplicated` и НЕ обновляет индекс. Всегда используйте уникальное имя: `MEMORY-2025-06-15.md`.

### 2. upload_file НЕ работает с локальными путями
`upload_file(file_path="/home/mia/Mia/memories/MEMORY.md")` возвращает `❌ Файл не найден`, даже если файл существует на диске. Причина: MCP сервер LightRAG работает в изолированном контексте (возможно, Docker/разный workdir).

**Единственный надёжный путь:** прочитать файл через `read_file`, передать содержимое в `upload_text` с уникальным filename.

### 3. Раздельные файлы хешей
Каждый файл личности (MEMORY.md, USER.md, SOUL.md) должен иметь свой файл хеша:
- `/tmp/memory_hash.txt` — для MEMORY.md
- `/tmp/user_hash.txt` — для USER.md
- `/tmp/soul_hash.txt` — для SOUL.md

### 4. Проверка после загрузки
После `upload_text` → `success`:
- Проверить через `rag_system_status` (processing: 0)
- Сделать `rag_query` с ключевыми словами из загруженного текста

## История багов

| Дата | Баг | Статус |
|------|-----|--------|
| ~03.06 | upload_file не находит файлы по абсолютному пути | Подтверждён |
| ~03.06 | upload_text с повторным filename → duplicated, контент не индексируется | Подтверждён, workaround есть |
