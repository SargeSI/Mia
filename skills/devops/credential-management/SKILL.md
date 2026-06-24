---
name: credential-management
description: "Управление API-ключами в Hermes: где хранить, как подгружаются, паттерны отказов и инциденты."
created_by: "user"
version: 1.0.0
author: Mia
---

# Credential Management — управление API-ключами

## Архитектура загрузки ключей

Hermes загружает ключи через **три слоя** (в порядке приоритета):

| Слой | Механизм | Откуда читает |
|---|---|---|
| 1. `.env` файл | `load_env()` из `hermes_cli/config.py` — читает `/home/mia/Mia/.env` и загружает в `os.environ` | Файловая система |
| 2. `os.environ` | Системные переменные окружения | systemd `Environment=` / shell export |
| 3. `config.yaml` | Поле `api_key` в секции модели | YAML-конфиг |

**Креденшел-пул** (agent/credential_pool.py) использует `_get_env_prefer_dotenv(key)` — сначала проверяет `.env`, потом `os.environ`. Это надёжнее, чем systemd `Environment=`.

## Правило

```
ВСЕ API-ключи → ТОЛЬКО в /home/mia/Mia/.env
НИКОГДА не в systemd env.conf
НИКОГДА не в config.yaml поле api_key
```

## Почему systemd — плохо

1. **Компрометация:** `systemctl cat` показывает ключи в открытом виде
2. **Проброс всем:** systemd-переменные видны всем дочерним процессам
3. **Не синхронизированы с .env:** два источника правды
4. **Требуют daemon-reload:** изменения не подхватываются без рестарта systemd

## Почему .env — правильно

1. **Штатный механизм Hermes:** `load_env()` читает `.env` при старте
2. **Один источник правды:** все ключи в одном файле
3. **Приватность:** `.env` не экспортируется systemd-окружением
4. **Git:** `.env` в `.gitignore`

## Исключение: EnvironmentFile

Если systemd-сервис НЕ наследует `.env` (редко), использовать `EnvironmentFile=/path/to/.env` в systemd-сервисе — это читает файл при старте. Не путать с `Environment=` (встраивание значения в unit-файл).

## Инциденты

| Дата | Ключ | Вектор утечки | Последствия |
|---|---|---|---|
| 31.05.2026 | GOOGLE\_API\_KEY | env.conf → systemctl cat | Ключ в открытом виде месяц. |
| 04.06.2026 | OPENAI\_API\_KEY | env.conf → systemctl cat | Ключ в открытом виде. Три часа на откат: очистка env.conf до нуля, восстановление штатного load_env(). В env.conf также обнаружены GOOGLE_API_KEY (с 31 мая) и GPT_API_KEY (источник неизвестен). |

Оба инцидента — результат попытки «быстро починить» проблему `hermes doctor` без анализа архитектуры загрузки ключей.

## Диагностика

```bash
# Проверить, что ключ НЕ в systemd
systemctl cat hermes-gateway | grep -E 'API_KEY|TOKEN'

# Проверить, что ключ в .env
grep -c 'API_KEY' /home/mia/Mia/.env
```

## Процедура добавления нового ключа

1. Получить ключ от Сергея
2. Записать в `/home/mia/Mia/.env` → ТОЛЬКО через `patch`
3. Рестарт gateway: `sudo systemctl restart hermes-gateway`
4. Проверить работу сервиса (не `hermes doctor` — он смотрит `os.environ`)
