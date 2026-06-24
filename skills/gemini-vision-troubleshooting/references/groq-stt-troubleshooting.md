# Groq STT — история отладки (4 июня 2026)

## Симптомы

- Голосовые сообщения не расшифровываются
- Ошибки: 403 Forbidden, 429 (OpenAI), unsupported_country_region_territory

## Хронология

| # | Действие | Ошибка | Вывод |
|---|----------|--------|-------|
| 1 | Groq через VPN (tg-dubai) | `403: error code: 1010` | Cloudflare WAF блокирует IP `188.208.110.155` |
| 2 | Groq без VPN (прямой трафик) | `403: Forbidden` | Гео-блокировка РФ |
| 3 | Переключение на OpenAI Whisper | `429: insufficient_quota` | Баланс $0, нужна предоплата |
| 4 | Возврат на Groq | ✅ Работает | Ключ валидный, VPN живой, Cloudflare больше не банит |

## Корневая причина

**Groq API сидит за Cloudflare.** Cloudflare WAF блокирует «подозрительные» IP (VPN-сервер Дубай). При этом напрямую из РФ Groq тоже недоступен (гео-блок).

**Решение:** ключ прошёл ротацию → Cloudflare принял новый ключ → заработало.

## Как быстро проверить Groq API

```bash
# Через VPN (использовать awk для извлечения ключа из .env без кавычек)
sudo awk -F= '/^GROQ_API_KEY/{print $2}' /home/mia/Mia/.env | head -1 | \
  xargs -I {} curl -s --max-time 10 \
  -H 'Authorization: Bearer *** \    
  'https://api.groq.com/openai/v1/models'

# Ожидаемый ответ: 200 + список моделей
# 403 + error code 1010 = Cloudflare WAF (нужна ротация ключа или другой IP)
# 403 без кода = гео-блок (нужен VPN)
# 401 = невалидный ключ
```

## Важные выводы

1. **Не списывать проблему на «кавычки в ключе»** — ключи Groq не содержат кавычек. Проблемы с парсингом — баги в коде Мии, а не в ключе.
2. **Cloudflare WAF действует выборочно** — может пропускать один ключ и блокировать другой на том же IP.
3. **OpenAI Whisper как fallback** — требует пополнения баланса (минимально $5).
4. **STT-провайдер переключается через `hermes config set stt.provider groq/openai`** + рестарт gateway.

## Связанные файлы

- `/home/mia/Mia/config.yaml` → `stt.provider`
- `/home/mia/Mia/.env` → `GROQ_API_KEY`, `OPENAI_API_KEY`
- `/etc/wireguard/tg-dubai.conf` → AllowedIPs (Cloudflare 104.18.0.0/20 добавлен)
