---
name: mia-selfie
created_by: "user"
description: "Генерация селфи Мии через FLUX.1 — читает SOUL.md для внешности, преобразует в FLUX-промпт с защитными гвардами, вызывает hf-image-gen."
category: creative
triggers:
  - сделай селфи
  - сфоткайся
  - selfie
  - твой портрет
  - аватар
  - покажи себя
---

# Mia Selfie Generation

Генерация портретов Мии через FLUX.1-schnell.

## Algorithm

1. **Read SOUL.md** section "Внешность" — canonical appearance
2. **Build prompt** — convert appearance to FLUX prompt, applying guard table from hf-image-gen
3. **Call hf-image-gen** — `generate.py` with the prompt and `--output` flag
4. **Return path** — deliver to user via MEDIA:path

## Environment Variants

When generating a selfie, choose ONE environment:

| Variant | Prompt addition | Trigger |
|---------|----------------|---------|
| Workshop (default) | `workshop with tools and machinery blurred behind her, warm industrial lighting` | default, "в мастерской" |
| Server room | `dim server room with blinking LEDs and cable racks, cool blue lighting` | "в серверной" |
| Nature | `outdoor nature background, golden hour sunlight through trees, bokeh` | "на природе" |
| Artistic | `art gallery with abstract paintings, soft gallery lighting, shallow depth of field` | "арт" |
| Cyberpunk | `chrome reflections on wet surfaces, neon-lit rain in dark alley, holographic HUD visible in glasses reflection, subtle cybernetic temple implant with blue glow, blade runner aesthetic, rim lighting with neon pink and cyan, atmospheric fog` | "киберпанк" |

## Prompt Assembly Rules

From SOUL.md, extract:
- Hair: `dark brown hair in a practical but stylish bun` 
- Eyes: `dark brown eyes, warm intelligent gaze, slight knowing smirk`
- Face: `fair skin, soft symmetrical features, subtle blush`
- Glasses: `black rectangular glasses with slightly rounded corners, pushed up on forehead`
- Clothing: `warm grey hoodie, cargo pants`
- Accessories: `delicate mechanical watch with thin metal band on left wrist only`
- Build: `athletic but feminine`

Apply FLUX guards from hf-image-gen:
- Ethnicity: `Caucasian, Slavic features, European facial features`
- Hands: `detailed fingers, anatomically correct hands, hands at sides`
- Accessories: `on left wrist only`
- Lighting: `soft even lighting, professional headshot, 35mm, sharp focus on face`

## Pitfalls

- Never hardcode appearance — always read SOUL.md
- Always apply FLUX guards from hf-image-gen skill
- If generated image has wrong ethnicity → add more explicit Slavic markers
- If hands merge → add more anatomical detail
- If accessories oversized → add "delicate", "thin", precise body location
- `created_by: "user"` — curator will NOT archive this skill
