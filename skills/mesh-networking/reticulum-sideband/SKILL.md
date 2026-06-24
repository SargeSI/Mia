---
name: reticulum-sideband
description: Настройка и диагностика Reticulum Network Stack и Sideband-мессенджера на Windows/Linux. Публичные транспортные ноды, bootstrap-подключение, конфигурация, устранение проблем.
---

# Reticulum & Sideband — настройка и диагностика

Reticulum — криптографический сетевой стек для построения суверенных mesh-сетей поверх LoRa, WiFi, Packet Radio, I2P, TCP/UDP.
Sideband — LXMF-мессенджер (чат, голос, ситуационная осведомлённость) поверх Reticulum.

## Установка

### Windows
Sideband устанавливается через exe-установщик с [unsigned.io](https://unsigned.io/software/Sideband.html),
но **НЕ подтягивает `rns` и `lxmf` автоматически**. После установки Sideband ОБЯЗАТЕЛЬНО:

```powershell
pip install rns lxmf
```

Проверить:
```powershell
pip show rns    # должно быть ≥1.3.5
```

### Linux / macOS
```bash
pip install sbapp       # подтягивает rns и lxmf автоматически
# или раздельно:
pip install rns lxmf
```

## Конфигурация

Конфиг Reticulum на Windows: `%USERPROFILE%\.reticulum\config` (обычно `C:\Users\ИМЯ\.reticulum\config`)

### КРИТИЧНО: синтаксис отступов

Reticulum использует INI-подобный формат. Параметры под-секций `[[Interface Name]]` ДОЛЖНЫ иметь отступ:

```ini
[interfaces]

  [[Default Interface]]
    type = AutoInterface
    enabled = Yes

  [[RNS Testnet Dublin]]
    type = TCPClientInterface
    enabled = yes
    target_host = dublin.connect.reticulum.network
    target_port = 4965
```

Без отступов парсер не может сопоставить `type = TCPClientInterface` с под-секцией `[[RNS Testnet Dublin]]`, возникает конфликт дублирования ключа `type`, и приложение падает при запуске.

### Публичные транспортные ноды (июнь 2026)

```
# Dublin Hub (официальный testnet)
[[RNS Testnet Dublin]]
  type = TCPClientInterface
  enabled = yes
  target_host = dublin.connect.reticulum.network
  target_port = 4965

# BetweenTheBorders (волонтёрский, может быть недоступен)
[[RNS Testnet BetweenTheBorders]]
  type = TCPClientInterface
  enabled = yes
  target_host = betweentheborders.com
  target_port = 4242

# I2P Hub (если TCP заблокирован)
[[RNS Testnet I2P Hub A]]
  type = I2PInterface
  enabled = yes
  peers = mrwqlsioq4hoo2lmeeud7dkfscnm7yxak7dmiyvsrnpfag3z5tsq.b32.i2p
```

Каталоги нод:
- [directory.rns.recipes](https://directory.rns.recipes/)
- [rmap.world](https://rmap.world/)

### Bootstrap-философия
Bootstrap-ноды — временные точки входа. После обнаружения целевого пира Reticulum строит прямые линки, и bootstrap-нода становится не нужна. Трафик всегда end-to-end зашифрован — транспортные ноды видят только шифртекст.

## Диагностика

### Статус интерфейсов
```powershell
# Windows (если rnstatus не в PATH):
python -m RNS.Utilities.rnstatus
```

Показывает: интерфейсы, статус (up/down/connecting), количество пиров.

### Проверка TCP-связности до хаба
```powershell
# Windows PowerShell:
Test-NetConnection dublin.connect.reticulum.network -Port 4965
Test-NetConnection betweentheborders.com -Port 4242
```
```bash
# Linux:
nc -zv dublin.connect.reticulum.network 4965
```

### Типовые проблемы

| Симптом | Причина | Решение |
|---------|---------|---------|
| Sideband вылетает при запуске | Конфиг: параметры без отступов под `[[Interface]]` | Добавить отступы |
| Анонс-поток пуст при активных TCP-интерфейсах | `rns` не установлен или хаб недоступен | `pip install rns lxmf`, проверить `Test-NetConnection` |
| DNS не резолвит хаб | Временный косяк DNS или хаба | Попробовать другой хаб, проверить позже |
| Хаб отвечает TCP, но анонсов нет | Пиров в testnet может не быть прямо сейчас | Подождать, проверить `rnstatus`, попробовать оба хаба |

## Обмен контактами

1. Sideband → Settings → Identity → Export (QR или текст)
2. Передать другу любым способом
3. Друг импортирует → вы видите друг друга в анонс-потоке → можно писать

## Публичный testnet

Официальная страница: https://reticulum.network/connect.html
Зеркало testnet: https://reticulum.betweentheborders.com/connect.html

Testnet — не production: ноды могут лежать, обновляться на экспериментальные версии. Использовать для тестов и обучения.

## Ссылки

- Сайт: https://reticulum.network
- GitHub: https://github.com/markqvist/Reticulum
- Sideband: https://unsigned.io/software/Sideband.html
- Ручная документация: https://reticulum.network/manual/
