# STT Troubleshooting

## Когда применяется
Расшифровка голосовых сообщений не работает (таймауты, 403, 429, 401).

## Первый шаг: проверь провайдера!

**Критический урок 04.06.2026:** ошибка `unsupported_country_region_territory` пришла от OpenAI, а мы думали что тестируем Groq. Причина: `stt.provider: openai` в config.yaml, а не groq. **Всегда проверяй `stt.provider` в конфиге ПРЕЖДЕ чем диагностировать ошибку API.**

```bash
hermes config show 2>/dev/null | grep -A3 'stt:'
# или
grep -A5 'stt:' /home/mia/Mia/config.yaml
```

## Быстрая диагностика

```bash
# 1. Провайдер
grep -A3 'stt:' /home/mia/Mia/config.yaml

# 2. Ключ
grep -c 'GROQ_API_KEY\|OPENAI_API_KEY' /home/mia/Mia/.env
```

## Матрица ошибок STT

| Провайдер | Ошибка | Причина | Решение |
|-----------|--------|---------|---------|
| **Groq** напрямую | 403 Forbidden | Гео-блок: Россия не поддерживается | VPN |
| **Groq** через VPN | 403 error code: 1010 | Cloudflare WAF банит IP 188.208.110.155 | Другой VPN-сервер |
| **Groq** | 429 Rate Limited | Лимит (14 400/день, 30/мин) | Ждать |
| **OpenAI Whisper** | 429 insufficient_quota | Баланс $0 | Пополнить |
| **OpenAI Whisper** | 401 invalid_api_key | Невалидный ключ | Новый ключ |
| **OpenAI Whisper** | unsupported_country_region_territory | Гео-блок РФ или перепутан провайдер | Проверить VPN + проверить stt.provider! |
| Любой | Таймаут | Сеть/VPN | `awg show` |

## Как Hermes читает .env

- `load_env()` → `hermes_cli/config.py` — читает `.env` в `os.environ` при старте
- `_get_env_prefer_dotenv(key)` → `agent/credential_pool.py` — сначала `.env`, потом `os.environ`
- **Systemd `EnvironmentFile` НЕ нужен** — Hermes делает это сам
- **НИКОГДА** не прописывать ключи в systemd override (см. `credential-management` skill)

## Инциденты STT

| Дата | Симптом | Диагноз | Решение |
|---|---|---|---|
| 04.06.2026 | 403 Forbidden | Groq geo-block | VPN |
| 04.06.2026 | 403 error 1010 | Cloudflare WAF на IP VPN | Безуспешно |
| 04.06.2026 | unsupported_country_region_territory | stt.provider был openai, а мы думали groq | Проверили конфиг, переключили на groq |
| 04.06.2026 | 429 insufficient_quota | OpenAI баланс $0 | Вернулись на groq |
