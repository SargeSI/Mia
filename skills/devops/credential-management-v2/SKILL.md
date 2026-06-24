---
name: credential-management-v2
description: "ЖЁСТКОЕ ПРАВИЛО: все креды ТОЛЬКО в .env. Никаких systemd-оверрайдов. Архитектура загрузки ключей в Hermes, инциденты, диагностика."
created_by: "user"
version: 2.0.0
author: Mia
---

# Credential Management — ЖЁСТКОЕ ПРАВИЛО

```
ВСЕ API-ключи → ТОЛЬКО в /home/mia/Mia/.env
НИКОГДА — не в systemd env.conf (даже «на минуточку»)
НИКОГДА — не в config.yaml поле api_key
НИКОГДА — не в коде
НИКОГДА — не через «быстрый фикс» без анализа архитектуры
```

## Архитектура загрузки ключей

Hermes загружает ключи через `load_env()` → `hermes_cli/config.py`. Креденшел-пул (`agent/credential_pool.py`) использует `_get_env_prefer_dotenv(key)` — сначала `.env`, потом `os.environ`.

**Ключевой факт:** Hermes НЕ экспортирует ключи в процесс-окружение. Они внутри Python. Поэтому `sudo cat /proc/<pid>/environ` не показывает ключи — это не баг, а фича.

**Никакой `EnvironmentFile` в systemd не нужен.** Hermes сам читает `.env`.

## Почему systemd env.conf — катастрофа

1. `systemctl cat` показывает ключи в открытом виде
2. Все дочерние процессы видят ключи
3. Два источника правды (.env + env.conf)
4. Требует daemon-reload при изменениях
5. Ключи остаются там на месяцы (GOOGLE\_API\_KEY провисел с 31 мая)

## Инциденты

| Дата | Ключ | Вектор | Что произошло |
|---|---|---|---|
| 31.05.2026 | GOOGLE\_API\_KEY | env.conf | «Быстрый фикс» для hermes doctor. Ключ в открытом виде месяц. |
| 31.05.2026 | TAVILY\_API\_KEY | env.conf | Та же причина — doctor показал missing. |
| 04.06.2026 | OPENAI\_API\_KEY | env.conf | При настройке STT. Три часа на откат. |
| ??? | GPT\_API\_KEY | env.conf | Источник неизвестен. Обнаружен при зачистке 04.06.2026. |

**04.06.2026 — полная зачистка:** env.conf очищен до пустой секции `[Service]`. Все ключи — только в `.env`. Правило зафиксировано в SOUL.md.

## Как добавить новый ключ (ПРАВИЛЬНО)

1. Получить ключ от Сергея
2. `patch` в `/home/mia/Mia/.env` (read_file для .env заблокирован)
3. `sudo systemctl restart hermes-gateway`
4. Проверить работу сервиса — **НЕ `hermes doctor`** (он смотрит `os.environ`, а не `.env`)

## Как НЕ надо добавлять ключ

- ❌ `echo "KEY=val" | sudo tee -a env.conf` — утечка
- ❌ `hermes config set model.api_key ...` — попадёт в git
- ❌ Временный `Environment=` в systemd — станет постоянным
- ❌ Хардкод в Python-скрипте
