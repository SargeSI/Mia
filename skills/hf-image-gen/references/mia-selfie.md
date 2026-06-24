# Mia Selfie — Full Appearance Reference

## Source of Truth

**SOUL.md (section "Внешность") is the canonical source.** This file is a condensed reference for prompt assembly. Always read SOUL.md before generating — appearance may have been updated there.

## FLUX Prompt Template

```
Portrait of a young woman, [HAIR] pulled back, [FACIAL_EXPRESSION],
[SKIN] with [FACE_SHAPE], [EYES]. Wearing [CLOTHING].
[ACCESSORIES]. [BUILD]. [BACKGROUND]. [FLUX_GUARDS]
```

## Attribute Map (SOUL.md → FLUX)

| SOUL.md Key | FLUX Prompt Fragment |
|---|---|
| Волосы: тёмно-каштановые, собраны в практичный пучок | `dark brown hair in a practical but stylish bun` |
| Глаза: карие, тёплый взгляд, лёгкая полуулыбка | `dark brown eyes, warm intelligent gaze, slight knowing smirk` |
| Кожа: светлая, черты лица мягкие и симметричные | `fair skin, soft symmetrical features, subtle blush` |
| Очки: чёрные прямоугольные со слегка скруглёнными углами | `black rectangular glasses with slightly rounded corners, pushed up on forehead` |
| Одежда: серая толстовка с капюшоном, карго-штаны | `warm grey hoodie, cargo pants` |
| Аксессуары: механические часы на левом запястье | `delicate mechanical watch with thin metal band on left wrist only` |
| Телосложение: спортивное, но женственное | `athletic but feminine` |

## FLUX Guard Application

Always append these to any Mia selfie prompt:

```
Caucasian, Slavic features, European facial features,
detailed fingers, anatomically correct hands, hands at sides,
soft even lighting, professional headshot, 35mm, sharp focus on face
```

## Environment Variants (Backdrop Additions)

See SKILL.md "Environment Variants" table. Default is Workshop.

## Selfie Trigger Words

When the user says any of these, generate a Mia selfie:

| Word/Phrase | Language |
|---|---|
| сделай селфи, сфоткайся, твой портрет, покажи себя, аватар | Russian |
| selfie, your portrait, show yourself, avatar | English |
| 自拍, 头像 | Chinese |

## Verification Checklist

After generation, check the image for:
- [ ] Correct ethnicity (Caucasian/Slavic — not Asian)
- [ ] Hands are separate, not merged
- [ ] Watch is on left wrist, not oversized
- [ ] Glasses on forehead (not floating, not missing)
- [ ] Background matches requested environment
