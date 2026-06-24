# FLUX.1 Pitfalls — универсальные

Обнаружены итеративно, применимы к ЛЮБОЙ генерации через FLUX.1-schnell.

## Ethnicity Bias

FLUX по умолчанию склоняется к азиатской внешности даже при явном описании европейской. Фикс: `Caucasian, Slavic features, European facial features` в промпте.

## Hand Merge

При запросе рук (hands, arms, fingers) FLUX часто сливает пальцы в одну массу или превращает две руки в одну конечность. Фикс: `detailed fingers, anatomically correct hands, hands at sides`.

## Finger Count

FLUX.1-schnell может рисовать 4 пальца вместо 5. Фикс: добавить `five fingers on each hand` в промпт. Если не помогает — переключиться на FLUX.1-dev.

## Accessory Hypertrophy

Аксессуары (watches, glasses, jewellery) FLUX гиперболизирует — часы становятся размером с рюкзак. Фикс: добавлять `delicate` к аксессуарам и явно указывать расположение (`on left wrist only`).

## Glasses Instability

Очки могут дублироваться (одна пара на носу, вторая на лбу), исчезать или парить в воздухе. Фикс: закрепить положение (`pushed up on forehead` или `worn on eyes` — но не то и другое одновременно).

## Ethnicity Spectrum

Для не-европейской внешности: не полагаться на «Asian» или «African» — FLUX понимает конкретные национальные черты (`Korean features`, `Ethiopian features`) лучше общих категорий.
