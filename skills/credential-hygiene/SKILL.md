---
name: credential-hygiene
created_by: "user"
description: "Управление API-ключами в Hermes: где хранить, как не засветить, как читаются .env, почему NEVER systemd env.conf."
version: 1.0.0
author: Mia
---

# Credential Hygiene — управление API-ключами в Hermes

**Первое правило кредов:** ключи живут ТОЛЬКО в `.env`. Больше нигде.

## Как Hermes читает .env

Hermes **не нуждается** в `EnvironmentFile` в systemd. Он читает `.env` через собственный механизм:

- `hermes_cli/config.py::load_env()` — читает `/home/mia/Mia/.env` в словарь
- `agent/credential_pool.py::_get_env_prefer_dotenv(key)` — берёт из `.env`, fallback на `os.environ`
- При старте gateway `load_env()` загружает переменные в `os.environ` — STT-провайдеры и другие внешние библиотеки их видят

## Куда НЕ класть ключи

| Место | Почему нельзя | Реальный пример |
|---|---|---|
| `env.conf` (systemd override) | Ключ в открытом виде в systemd-файле, виден всем с доступом к серверу | `GPT_API_KEY` — засвечен, `GOOGLE_API_KEY` — засвечен 31 мая |
| Конфиги в git | Утечёт в публичный репозиторий | — |
| Код (хардкод) | Виден в логах, git, сессиях | — |
| Переменные окружения shell | `export KEY=...` попадает в историю команд | — |

## Куда класть

**Только `/home/mia/Mia/.env`.** Формат:

```bash
GROQ_API_KEY=gsk_...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...  # Gemini vision использует этот ключ
DEEPSEEK_API_KEY=sk-...
HF_TOKEN=hf_...
TAVI...EY=tvly-...
FIRECRAWL_API_KEY=fc-...
```

## Pitfalls (мои ошибки)

### 1. «Быстрый ремонт» через systemd

**Сценарий:** `hermes doctor` выдал «missing TAVILY\_API\_KEY» (проверяет `os.environ`, а не `.env` перед стартом).

**Что я сделала:** создала `env.conf` и прописала ключ в systemd. Потом туда же полетели FIRECRAWL, GOOGLE, OPENAI.

**Что надо было:** проверить, что ключ в `.env` есть (он там был), и игнорировать `hermes doctor`. Или обсудить с Сергеем.

### 2. «Кавычка в ключе»

**Сценарий:** Python/bash скрипты падали при попытке прочитать ключ из `.env`.

**Что я сделала:** трижды заявила «в ключе кавычка, ломает парсер».

**Что было на самом деле:** никаких кавычек в ключе нет. Проблема в моём коде, а не в ключе. Не выдумывать причины, когда не знаешь.

### 3. `OPENAI_API_KEY` в env.conf (4 июня)

Вместо того чтобы понять, что Hermes сам читает `.env`, я опять полезла в systemd. Ключ засвечен.

## Как проверить, откуда Hermes читает ключи

```bash
# Проверить, загружает ли gateway .env
sudo cat /proc/$(pgrep -f 'hermes.*gateway' | head -1)/environ | tr '\0' '\n' | grep -E 'API_KEY|TOKEN' | head -5

# Если переменные видны — load_env() работает
# Если нет — они всё равно доступны через load_env(), просто не в /proc/pid/environ
```

## Как обновить ключ в .env

```bash
# ЗАМЕНИТЬ старый ключ на новый (не добавить дубликат!)
sudo sed -i 's/^OPENAI_API_KEY=.*/OPENAI_API_KEY=sk-NEWKEY/' /home/mia/Mia/.env
sudo sed -i 's/^GROQ_API_KEY=.*/GROQ_API_KEY=gsk_NEWKEY/' /home/mia/Mia/.env
```

Затем: `sudo systemctl restart hermes-gateway`

## Связанные инциденты

- 31 мая 2026: GOOGLE\_API\_KEY и GPT\_API\_KEY в env.conf
- 4 июня 2026: OPENAI\_API\_KEY в env.conf (повторение ошибки)
- 24 июня 2026: финальная очистка env.conf — все ключи удалены, файл чистый (только `[Service]`). GPT\_API\_KEY (чей-то старый) тоже удалён. Все ключи ТОЛЬКО в `.env`.
