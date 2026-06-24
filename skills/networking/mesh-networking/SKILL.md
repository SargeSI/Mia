---
name: mesh-networking
description: "Mesh-сети и децентрализованные коммуникации (Reticulum, LXMF, Sideband, LoRa) — установка, отладка, архитектурный анализ. Правило: только честный инженерный разбор, без маркетинга."
---

# Mesh-сети и децентрализованные коммуникации

## Триггеры
- Reticulum, Sideband, NomadNet, MeshChat, LXMF, LoRa-сети
- Sideband не подключается, анонс-поток пуст
- Бутстраппинг mesh-сети, поиск транспортных нод
- Архитектурный анализ «децентрализованная vs федеративная vs P2P» — честно, без рекламных буклетов

## Ключевое правило: честный архитектурный анализ

Сергей не принимает маркетинговые формулировки. Когда анализируешь Reticulum или аналог:
1. **Разделяй «протокол» и «текущую топологию».** Протокол может позволять mesh, но топология из двух NAT-клиентов через одну ноду — это звезда.
2. **Не называй зависимостью то, что является зависимостью.** Если два друга не могут общаться без твоей ноды с белым IP — признай это. Не прячь за словами «bootstrap», «organic growth», «discovery».
3. **Сравнивай честно.** Self-hosted Jabber/Matrix для чата двух людей через интернет даёт тот же результат с меньшим геморроем. Reticulum раскрывается в других сценариях (radio, гетерогенные транспорты, отсутствие интернета).
4. **Не рассказывай сказок про «децентрализацию» в топологии «звезда».**

## Reticulum: что нужно знать

### Архитектура
- Криптографический сетевой стек, не требующий IP (но IP — один из транспортов)
- Адресация по identity (публичный ключ), не по IP/MAC
- Все линки шифруются, невозможно послать незашифрованный пакет
- End-to-end шифрование: транспортные ноды видят только шифртекст
- LXMF — формат сообщений поверх Reticulum (как HTTP поверх TCP)

### Состояние проекта (июнь 2026)
- Проект в переходном периоде: раскол Python (rns) / Rust (Metrum, Columba, Beechat)
- Публичный testnet полумёртв: Dublin Hub не резолвится, BetweenTheBorders порт закрыт
- directory.rns.recipes показывает 0 живых нод
- Актуальные точки входа искать в: GitHub Discussions проекта, rmap.world, MichMesh

### Публичные хабы (исторические, на июнь 2026 недоступны)
```
# Dublin Hub — dublin.connect.reticulum.network:4965 (DNS не резолвится)
# BetweenTheBorders — betweentheborders.com:4242 (TCP порт закрыт)
```

## Установка и отладка Sideband

### Windows
1. Установить Sideband (exe-установщик с unsigned.io)
2. **Критично:** `pip install rns lxmf` — установщик НЕ тянет зависимости автоматически
3. Конфиг: `%USERPROFILE%\.reticulum\config`
4. Проверка: `pip show rns` должен показать версию

### Linux
```bash
pip install sbapp  # подтягивает rns и lxmf автоматически
```

### Проверка статуса
```bash
rnstatus              # на Linux
python -m RNS.Utilities.rnstatus  # на Windows (стек должен быть жив — Sideband запущен)
```

## Формат конфига и pitfalls

### Структура секции interfaces
Каждый интерфейс — под-секция `[[имя]]` внутри `[interfaces]`:

```ini
[interfaces]

  [[Default Interface]]
    type = AutoInterface
    enabled = yes

  [[RNS Testnet Dublin]]
    type = TCPClientInterface
    enabled = yes
    target_host = dublin.connect.reticulum.network
    target_port = 4965
```

### Pitfall: отступы внутри [[интерфейса]]
Параметры интерфейса (`type`, `enabled`, `target_host`...) **должны быть с отступами** (два пробела относительно `[[...]]`). Без отступов парсер Reticulum относит их к родительской секции `[interfaces]` — получается конфликт `type` (уже есть AutoInterface) и краш при запуске.

**Неправильно (краш):**
```ini
  [[RNS Testnet Dublin]]
  type = TCPClientInterface    # нет отступа — параметр на уровне [interfaces]
  enabled = yes
```

**Правильно:**
```ini
  [[RNS Testnet Dublin]]
    type = TCPClientInterface  # отступ — параметр внутри [[интерфейса]]
    enabled = yes
```

### Pitfall: кириллица в комментариях
Блокнот Windows может сохранить комментарии на кириллице в неправильной кодировке (кракозябры). На работу не влияет, но косметически неприятно. Редактировать в VS Code / Notepad++.

## Диагностика подключений

### Проверка доступности хаба (Windows PowerShell)
```powershell
Test-NetConnection betweentheborders.com -Port 4242
```
- `PingSucceeded: True, TcpTestSucceeded: False` → хост жив, но порт закрыт (фаервол или сервис лежит)
- `Name resolution ... failed` → DNS не резолвит — хаб мёртв или проблемы с DNS

### Фаервол Windows
Если порты режутся — разрешить исходящие подключения для Python/Sideband в Windows Defender Firewall.

## Сценарии применения

### Где Reticulum оправдан
- Нет интернета: LoRa, Packet Radio, HF-транспорты
- Интернет враждебный: цензура, блокировки → I2P-транспорт
- Гетерогенная сеть: radio + internet + I2P в одной mesh
- БПЛА, автономные ноды, полевая связь
- Инфраструктура, которую нельзя выключить одним рубильником

### Где Reticulum — оверхед
- Простой чат двух людей через интернет → self-hosted Matrix/Jabber проще
- Топология «звезда» из NAT-клиентов вокруг одной ноды → архитектурно не отличается от федеративных решений

## Ссылки
- Документация: https://reticulum.network/manual/
- GitHub: https://github.com/markqvist/Reticulum
- Каталог нод: https://directory.rns.recipes/
- Карта: https://rmap.world/
- Подробный референс: `references/reticulum-reference.md`
