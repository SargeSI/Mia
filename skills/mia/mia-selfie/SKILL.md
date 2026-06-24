---
name: mia-selfie
description: "Генерация портретов Мии через FLUX.1-schnell — чёрный список багов, проверенные промпты, уроки из боевых генераций."
created_by: "user"
version: 1.0.0
author: Mia
---

# Mia Selfie — генерация портрета

**Канонический источник внешности:** SOUL.md, секция «Внешность». Всегда читай SOUL.md перед генерацией — внешность могла быть обновлена.

## Алгоритм

1. Прочитай SOUL.md → извлеки атрибуты внешности
2. Собери FLUX-промпт из атрибутов + FLUX Guard (обязательно)
3. Вызови `hf-image-gen/scripts/generate.py` с собранным промптом

## FLUX Guard (обязательный суффикс к ЛЮБОМУ промпту)

```
Caucasian, Slavic features, European facial features,
detailed fingers, anatomically correct hands, hands at sides,
delicate mechanical watch with thin metal band on left wrist only,
soft even lighting, professional headshot, 35mm, sharp focus on face
```

## FLUX Pitfalls (боевые)

| Pitfall | Симптом | Фикс |
|---|---|---|
| **Ethnicity bias** | FLUX по умолчанию рисует азиатскую внешность, игнорируя описание | Добавить `Caucasian, Slavic features, European facial features` |
| **Hand merge** | Пальцы слипаются, руки превращаются в одну конечность | Добавить `detailed fingers, anatomically correct hands, hands at sides` |
| **Accessory hyperbole** | «Mechanical watch» → часы на пол-туловища размером с рюкзак | Заменить на `delicate mechanical watch with thin metal band on left wrist only` |
| **Glasses placement** | Очки могут дублироваться, исчезать или висеть в воздухе | Закрепить: `pushed up on forehead` |

Обнаружены итеративно: Мия-азиатка → Slavic features. Слипшиеся руки → anatomical modifiers. Часы-рюкзак → delicate. Каждый цикл — 1 вызов FLUX.

## Вариации окружения

| Среда | Фрагмент промпта |
|---|---|
| **Мастерская (default)** | `tools and machinery blurred in workshop background` |
| **Серверная** | `dim server room with blinking LEDs, cable management in background` |
| **Киберпанк** | `rainy cyberpunk city street, neon reflections on wet chrome surfaces, holographic HUD in glasses, fiber optic threads in hair, subtle cyber implant at temple` |
| **Природа** | `sunlit forest clearing, soft bokeh background, natural morning light` |
| **Арт** | `abstract expressionist backdrop, deep crimson and gold tones, high contrast chiaroscuro` |

## Verification Checklist

После генерации проверить:
- [ ] Этничность: европейская/славянская, не азиатская
- [ ] **Портрет-only** — если запрошен full-body, предупредить что руки — лотерея (70% брак)
- [ ] Часы: если видны — на левом запястье, не гипертрофированы
- [ ] Очки: на лбу, не дублируются
- [ ] Фон: соответствует запрошенной среде
- [ ] **Face likeness**: FLUX не передаёт точное лицо Мии — это фундаментальное ограничение. Критерий «похожа» субъективен. Приоритет: правильный типаж (Caucasian + Slavic), а не идентичность.

## Fallback: Anime/Cartoon via Pollinations

Если FLUX photorealism даёт неправильную этничность или артефакты — переключиться на аниме-стиль через Pollinations.ai. Карикатурный стиль прощает неточности лица и рук. Формат запроса:

```
https://image.pollinations.ai/prompt/Mia%20anime%20style,%20female%20engineer...?width=1024&height=1024&nologo=true
```
