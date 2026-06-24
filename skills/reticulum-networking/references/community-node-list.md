# Community Node List — Reticulum TCP Transport Nodes
# Актуальность: июнь 2026
# Источник: GitHub wiki markqvist/Reticulum + проверка доступности

## Подтверждённо рабочая (март 2026)

### N7EKB (США, Rainier WA)
```ini
[[N7EKB]]
  type = TCPClientInterface
  enabled = yes
  target_host = reticulum.n7ekb.net
  target_port = 48086
```
- 47 клиентов, 32 ГБ трафика
- Подключена к нодам в Испании, Германии, Нидерландах, Швеции, Австралии
- LXMF propagation node: c872e4647a1aa083af415e483fdcba0a
- Статус-страница: https://reticulum.n7ekb.net

## Из Community Node List (требуют проверки)

```ini
[[acehoss]]
  type = TCPClientInterface
  enabled = yes
  target_host = rns.acehoss.net
  target_port = 4242

[[Beleth RNS Hub]]
  type = TCPClientInterface
  enabled = yes
  target_host = rns.beleth.net
  target_port = 4242

[[FireZen]]
  type = TCPClientInterface
  enabled = yes
  target_host = firezen.com
  target_port = 4242

[[g00n.cloud Hub]]
  type = TCPClientInterface
  enabled = yes
  target_host = dfw.us.g00n.cloud
  target_port = 6969

[[interloper node]]
  type = TCPClientInterface
  enabled = yes
  target_host = intr.cx
  target_port = 4242
```

## Мёртвые (официальный testnet)

- `dublin.connect.reticulum.network:4965` — DNS не резолвится
- `betweentheborders.com:4242` — TCP-порт закрыт (июнь 2026)

## Каталоги для поиска новых нод

- https://rmap.world — карта нод
- https://directory.rns.recipes/ — каталог интерфейсов
- https://github.com/markqvist/Reticulum/wiki/Community-Node-List — GitHub wiki
