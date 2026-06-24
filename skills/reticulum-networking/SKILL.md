---
name: reticulum-networking
description: Reticulum Network Stack — установка, настройка, поиск нод, архитектурные ограничения. Использовать при работе с Reticulum, Sideband, mesh-сетями на RNS.
---

# Reticulum Network Stack

## Что такое Reticulum

Криптографический сетевой стек для построения локальных и глобальных mesh-сетей. Может работать поверх LoRa, WiFi, Packet Radio, I2P, TCP/IP — как с интернетом, так и без.

**Ключевое:** Reticulum не конкурирует с Matrix/Jabber для интернет-чатов. Его сильная сторона — off-grid (радио) и гетерогенные сети (radio+internet+I2P в одной сети). Для простого чата с другом через интернет self-hosted Matrix даёт тот же результат с меньшим оверхедом.

## Установка на Windows

Sideband НЕ подтягивает `rns` автоматически. После установки Sideband нужно:

```powershell
pip install rns lxmf
pip show rns  # проверить — должно быть 1.3.x+
```

Без этого Sideband запускается, но не работает с сетью (анонс-поток пуст).

## Конфигурация

Конфиг: `%USERPROFILE%\.reticulum\config` (Windows) или `~/.reticulum/config` (Linux).

### Критично: отступы

Параметры внутри `[[интерфейс]]` ДОЛЖНЫ иметь отступы. Без отступов парсер не понимает, к какой под-секции они относятся, и Sideband падает при запуске.

**Правильно:**
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

**Неправильно (краш):**
```ini
  [[RNS Testnet Dublin]]
  type = TCPClientInterface
  enabled = yes
```

### Проверка статуса

```powershell
python -m RNS.Utilities.rnstatus
```

Должна запускаться при работающем Sideband (стек должен быть жив).

## Bootstrap — как войти в сеть

Reticulum — не сервис, а тулкит. Чтобы войти в сеть, нужно знать хотя бы один узел.

### Публичный testnet (июнь 2026)

Официальные хабы **мертвы**:
- `dublin.connect.reticulum.network:4965` — DNS не резолвится
- `betweentheborders.com:4242` — TCP-порт закрыт

### Живые community-ноды

См. `references/community-node-list.md` — актуальный список из GitHub Community Node List.

### Каталоги нод

- [rmap.world](https://rmap.world) — карта нод
- [directory.rns.recipes](https://directory.rns.recipes/) — каталог интерфейсов (SPA, требует браузер)
- [GitHub Community Node List](https://github.com/markqvist/Reticulum/wiki/Community-Node-List)

## Архитектурные ограничения

### NAT traversal — отсутствует

Reticulum НЕ делает hole-punching/DHT/uTP как BitTorrent. Узел за NAT может только **подключаться** к узлам с белым IP. Два узла за NAT не могут соединиться напрямую.

### Белый IP нужен

Для интернет-сегмента mesh-сети нужен минимум один узел с белым IP. Это не баг, а следствие ориентации стека на радиосети (где NAT нет).

LTE-устройства почти всегда за CG-NAT — могут быть только клиентами.

### Сравнение с альтернативами

| Сценарий | Reticulum | Matrix/Jabber | BitTorrent |
|----------|-----------|---------------|------------|
| Чат через интернет | Работает (через transport node) | Работает | Не для этого |
| Off-grid (LoRa) | ✅ Сильная сторона | ❌ Не работает | ❌ Не работает |
| Mesh radio+IP | ✅ Единый стек | ❌ Разные протоколы | ❌ |
| P2P через NAT | ❌ Нужен белый IP у кого-то | ❌ Нужен сервер | ✅ DHT/STUN |
| Self-hosted | Да (transport node) | Да (сервер) | N/A |

## Когда использовать Reticulum

**Имеет смысл:**
- Связь без интернета (LoRa, packet radio)
- Гетерогенные сети: часть на радио, часть через интернет, часть через I2P
- Инфраструктура без единой точки контроля на уровне протокола
- БПЛА, полевые mesh-сети, аварийная связь

**Не имеет смысла:**
- Просто чат с другом через интернет — self-hosted Matrix проще
- Замена Telegram/WhatsApp — другой класс задач

## Приложенные файлы

- `references/community-node-list.md` — список публичных транспортных нод
- `references/analysis-june-2026.md` — полный анализ ограничений и применимости

## Pitfalls

- Sideband на Windows требует ручной установки `rns` и `lxmf` через pip
- Отступы в конфиге обязательны — без них краш при запуске
- Не верь официальной документации про Dublin/BetweenTheBorders — они мертвы (июнь 2026)
- `rnstatus` требует живого стека (Sideband должен быть запущен)
- Reticulum не делает NAT traversal — это архитектурное решение, не баг
- Для mesh-покрытия в Москве практически нет узлов — нужно разворачивать своё
