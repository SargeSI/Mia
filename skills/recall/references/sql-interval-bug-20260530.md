# SQL-баг INTERVAL в search_clusters

**Дата:** 30 мая 2026
**Файл:** `recall.py`, метод `PgVectorStore.search_clusters()`, строка 290
**Найдено:** Hermes-Мия в ходе дебага cross-session recall

## Симптомы

- `search_clusters()` всегда падает с синтаксической ошибкой при `max_age_days is not None`
- `_bg_chunk_single` в gateway/run.py глушил ошибку через `except Exception: pass` (строка 239)
- Cross-session recall **никогда не работал**: все запросы уходили в fallback на текущую сессию
- Кластеры BMW и Honda не смерживались только потому что реально разные (sim=0.45 < 0.5)

## Корневая причина

Строка 290:
```python
age_sql = f"AND updated_at > NOW() - INTERVAL '%s days'"
```

`'%s'` внутри SQL-строкового литерала — psycopg2 интерпретирует `%s` как плейсхолдер и подставляет значение параметра. Но значение подставляется **внутри SQL-строки**, создавая двойные кавычки:

```sql
AND updated_at > NOW() - INTERVAL ''10' days'
                                    ^^^^  ← синтаксическая ошибка
```

Дополнительно, `params.insert(-1, str(max_age_days))` добавлял **пятый** параметр в массив из четырёх плейсхолдеров. Пятый параметр подставлялся в `'%s'` внутри строки, а не в настоящий плейсхолдер.

## Исправление

```python
# Было:
age_sql = f"AND updated_at > NOW() - INTERVAL '%s days'"
params.insert(-1, str(max_age_days))

# Стало:
age_sql = f"AND updated_at > NOW() - INTERVAL '{max_age_days} days'"
# params.insert() удалена
```

Значение `max_age_days` — `int` из конфига, безопасно от SQL-инъекции. Вставка напрямую в f-строку.

## Воспроизведение

```python
from recall import PgVectorStore, load_config, EmbeddingClient
config = load_config()
store = PgVectorStore(config["postgresql"])
embedder = EmbeddingClient(config["ollama"]["url"], config["ollama"]["model"])
emb = embedder.embed("любой текст")
# До фикса:
store.search_clusters(emb, threshold=0.5, limit=3, max_age_days=10)
# Ошибка: psycopg2.errors.SyntaxError: ОШИБКА: ошибка синтаксиса (примерное положение: "10")
# После фикса: возвращает результаты
```

## Урок

- Никогда не использовать `'%s'` внутри SQL-строковых литералов в psycopg2 — подстановка сломает кавычки
- Integer-значения безопасно вставлять напрямую в f-строку SQL (нет риска инъекции)
- `except: pass` в daemon-потоках — гарантированный способ скрыть баги на месяцы
