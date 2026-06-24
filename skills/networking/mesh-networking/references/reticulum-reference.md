# Reticulum: практический референс

## Установка Sideband (июнь 2026)

### Windows
```powershell
# 1. Скачать и установить Sideband с unsigned.io (exe-установщик)
# 2. ДОустановить зависимости — установщик их НЕ тянет:
pip install rns lxmf
# 3. Проверить:
pip show rns
# rns 1.3.5, lxmf 1.0.1
```

### Linux
```bash
pip install sbapp  # подтягивает rns и lxmf автоматически
```

## Конфигурационные файлы

### Windows
`%USERPROFILE%\.reticulum\config` (обычно `C:\Users\ИМЯ\.reticulum\config`)

### Linux
`~/.reticulum/config`

## Рабочий конфиг для подключения к публичному testnet

**Важно:** на июнь 2026 оба публичных хаба не отвечают. Конфиг приведён как эталонный образец для будущих рабочих нод.

```ini
[reticulum]
  enable_transport = False
  share_instance = Yes

[logging]
  loglevel = 4

[interfaces]
  [[Default Interface]]
    type = AutoInterface
    enabled = yes

  [[RNS Testnet Dublin]]
    type = TCPClientInterface
    enabled = yes
    target_host = dublin.connect.reticulum.network
    target_port = 4965

  [[RNS Testnet BetweenTheBorders]]
    type = TCPClientInterface
    enabled = yes
    target_host = betweentheborders.com
    target_port = 4242
```

## Состояние публичных хабов (22 июня 2026)

| Хаб | Статус | Диагностика |
|-----|--------|-------------|
| Dublin Hub (dublin.connect.reticulum.network:4965) | Мёртв | DNS не резолвится |
| BetweenTheBorders (betweentheborders.com:4242) | Мёртв | Пинг OK (468ms, 23.87.212.54), TCP порт 4242 закрыт |
| directory.rns.recipes | Пуст | 0 User Submitted, 0 Discovered, 37 Show Offline |

## Диагностика (Windows PowerShell)

```powershell
# Доступность хоста и порта:
Test-NetConnection betweentheborders.com -Port 4242
# PingSucceeded: True, TcpTestSucceeded: False → порт закрыт

# Статус Reticulum (Sideband должен быть запущен):
python -m RNS.Utilities.rnstatus
```

## Ключевые pitfall'ы

1. **Отступы в INI-конфиге:** параметры `[[интерфейса]]` должны быть с отступом. Без отступа парсер относит их к `[interfaces]` → конфликт `type` → краш.

2. **rns не установлен:** Windows-установщик Sideband не ставит `rns` как зависимость. Sideband запускается, но анонс-поток пуст навсегда.

3. **Кириллица в комментариях:** Блокнот Windows портит кодировку. Править в VS Code / Notepad++.

4. **rnstatus на Windows:** может просто вывести "Python" если стек не запущен. Запустить Sideband, потом проверять.

## Архитектурные выводы (из дискуссии с Сергеем)

- Для двух друзей за NAT через интернет — Reticulum через одну транспортную ноду архитектурно не отличается от self-hosted Jabber/Matrix
- Транспортная нода end-to-end не читает сообщения (в отличие от Jabber-сервера, который видит метаданные: кто кому пишет, roster, presence)
- Но: если нода одна — это точка отказа. Mesh требует МНОЖЕСТВА узлов
- Reticulum раскрывается в сценариях без интернета (radio), с враждебным интернетом (I2P), с гетерогенными транспортами, БПЛА/полевая связь
- Проект в переходном периоде (Python→Rust, FOSDEM 2026): Metrum, Columba, Beechat, RetiNet

## Альтернативы для простого чата через интернет
- Self-hosted Matrix (Synapse/Dendrite)
- Self-hosted XMPP (Prosody/Ejabberd)
- SimpleX Chat (P2P, не требует публичного IP через relay-серверы)
