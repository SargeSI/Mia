# Выбор шин для BMW E53 X5 4.4i

## Летние (куплены, июнь 2026)

**Модель:** Nexen N'Fera RU1

| Ось | Размер | Индекс | EU Wet | EU Fuel | Шум | Цена (06.2026) |
|---|---|---|---|---|---|---|
| Перед | 255/50 R19 | 107W XL | A | C | 70 dB | 14 530 ₽ |
| Зад | 285/45 R19 | 111W XL | A | C | 71 dB | 15 080 ₽ |
| **Итого** | | | | | | **59 220 ₽** |

- Класс: UHP летняя
- OE: Porsche Cayenne (255/55 R18, 2016), Porsche Macan
- Асимметричный протектор, 4 канала, «тихие ламели»
- Износ: 40-65 тыс км по отзывам

**Отклонена:** Nexen N'Fera RU5 — всесезонка, хуже wet grip (C-D vs A), не нужна при отдельном зимнем комплекте.

## Зимние (кандидат)

**Модель:** Ikon Character Ice 8 SUV (бывш. Nokian Nordman 8)

- Размер: 255/55 R18 109T XL
- Технология: поколение Nokian Hakkapeliitta 9
- Цена: ~14 820 ₽ (mosautoshina.ru, июнь 2026)
- Отдельный комплект дисков R18

**Альтернативы (отклонены):**
- Gislaved SpikeControl SUV — НЕТ XL (опасно для X5)
- Ikon Character Ice 7 / Nordman 7 — устаревшее поколение (Hakka 8)
- Yokohama IG65 — шумнее, хуже лёд
- Nexen Winguard Spike 3 — слабее по льду
- Cordiant Snow Cross 2, Viatti Bosco Nordico, Kumho WI32 — бюджет

## Мониторинг цен

Cron-задача 80fc6aa914cd, каждый понедельник 9:00. Проверяет цены на mosautoshina.ru:
- Ikon Character Ice 8 SUV (порог: < 14 079 ₽)
- Ikon Nordman 8 SUV (порог: < 14 927 ₽)
- Yokohama IG65 (порог: < 13 205 ₽)
- Nexen Winguard Spike 3 (порог: < 11 913 ₽)

## Проблема: слабые басы через AUX (DSP S677)

- AUX в жгуте 16:9 монитора, ~10 см от монитора
- AUX gain поднимается через сервисное меню BM54 (SELECT ≥8 сек → TONE LINE → пресеты #1-6)
- BlueBus не подходит — отключает штатный CD-чейнджер
