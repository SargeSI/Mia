# Auxiliary LLM Configuration — Hermes

**Дата:** 30 мая 2026  
**Контекст:** настройка вспомогательных моделей Hermes для продакшена

## Проблема

По умолчанию большинство auxiliary-тасков Hermes используют `provider: auto`. Система сама выбирает из openrouter, nous, deepseek, google. Но когда доступен только **один** LLM-провайдер (DeepSeek) + Ollama для embedding'ов, `auto` не имеет смысла и создаёт warning'и в логах:

```
WARNING agent.auxiliary_client: OPENAI_BASE_URL is set but model.provider is 'deepseek'.
Auxiliary clients may route to the wrong endpoint.
```

## Решение: явно прописать все auxiliary-таски

В `config.yaml`, секция `auxiliary`:

```yaml
auxiliary:
  compression:
    provider: deepseek
    model: deepseek-v4-flash
    extra_body:
      thinking:
        type: disabled

  title_generation:
    provider: deepseek
    model: deepseek-v4-flash
    extra_body:
      thinking:
        type: disabled

  skills_hub:
    provider: deepseek
    model: deepseek-v4-flash
    extra_body:
      thinking:
        type: disabled

  # Даже те, что не используются сейчас — для консистентности
  approval:
    provider: deepseek
    model: deepseek-v4-flash
    extra_body:
      thinking:
        type: disabled

  curator:
    provider: deepseek
    model: deepseek-v4-flash
    extra_body:
      thinking:
        type: disabled

  # ... и остальные (web_extract и mcp оставить auto — они не LLM)
```

## Что оставить на auto

- **web_extract** — не LLM (Tavily парсинг HTML)
- **mcp** — не LLM (протокол, транспорт)
- **vision** — google gemini-flash (нужен API ключ)

## Почему важно

- `auto`-режим создаёт неопределённость: какая модель используется?
- Warning'и забивают логи
- Явная конфигурация = явный контроль над расходами и задержками
- При добавлении новых провайдеров — легко переключить точечно
