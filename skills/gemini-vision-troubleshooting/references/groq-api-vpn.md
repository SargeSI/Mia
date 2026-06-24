# Groq API — VPN Routing

**Проблема:** Groq API (`api.groq.com`) таймаутит — трафик не идёт через VPN.

**Причина:** Тот же паттерн, что с Gemini. Groq API хостится на Cloudflare (104.18.0.0/20), который не добавлен в AllowedIPs AmneziaWG.

**Решение:** добавить `104.18.0.0/20` в `/etc/wireguard/tg-dubai.conf` → `AllowedIPs`:

```bash
# Добавить диапазон
sudo sed -i 's/AllowedIPs = /AllowedIPs = 104.18.0.0\/20, /' /etc/wireguard/tg-dubai.conf

# Перезапустить туннель
sudo awg-quick down /etc/wireguard/tg-dubai.conf
sudo awg-quick up /etc/wireguard/tg-dubai.conf

# Проверить handshake
sudo awg show | grep handshake
```

**Проверка API:**
```bash
# Т.к. ключ содержит спецсимволы, использовать awk + xargs:
sudo awk -F= '/^GROQ_API_KEY/{print $2}' /home/mia/Mia/.env | head -1 | xargs -I {} curl -s --max-time 10 -H 'Authorization: Bearer *** 'https://api.groq.com/openai/v1/models'
```

**Диагностика по кодам ошибок:** 
| Код | Причина | Действие |
|---|---|---|
| 200 | Всё работает | — |
| `Forbidden` (403) | Ключ невалидный, аккаунт не активирован, или Cloudflare WAF | Проверить статус ключа в console.groq.com/keys |
| `403 error code: 1010` | Cloudflare WAF блокирует IP VPN-сервера | IP в бане — нужен другой VPN-сервер |
| Таймаут | Диапазон Cloudflare не в VPN | Добавить `104.18.0.0/20` в AllowedIPs |

**Если 403 даже с валидным ключом** (и через VPN, и без):
- Проверить аккаунт Groq: подтверждён ли email, активен ли бесплатный тир
- Возможно, Groq заблокировал регион (РФ) или требует верификации карты для бесплатного API
- Проверить в https://console.groq.com/keys: зелёный индикатор «Active» или красный? Есть ли баннер «Verify your email»?

**Альтернативы при недоступности Groq:**
- Не предлагать faster-whisper без проверки ресурсов сервера (CPU, RAM, GPU)
- На 2 ядрах Xeon 2011 года без GPU локальные модели нежизнеспособны
- Vosk tiny — игрушка, точность на русском неприемлемая

**Ключи со спецсимволами (кавычки, апострофы):** такие ключи ломают Python и bash при любом прямом использовании. Техники обхода:
1. Python: `bytes.find()` вместо строкового `startswith()`
2. Bash: `awk` вместо `grep` (не интерполирует)
3. `base64` кодирование ключа из `.env` → передача в скрипт

**Дата:** 4 июня 2026
