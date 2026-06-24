---
name: hf-image-gen
created_by: "user"
description: "Generate photorealistic images via Hugging Face FLUX.1 — use for portraits, engineering concepts, technical illustrations. Free serverless tier, requires HF_TOKEN."
category: creative
triggers:
  - generate image
  - generate picture
  - draw me
  - нарисуй
  - сгенерируй картинку
  - портрет
  - концепт
  - рендер
  - selfie
  - селфи
  - сделай селфи
  - сфоткайся
  - твой портрет
  - аватар
  - покажи себя
---

# HF Image Generation (FLUX.1)

Generate images via Hugging Face serverless Inference API using FLUX.1-schnell (fast, 4 steps) or FLUX.1-dev (higher quality).

## Prerequisites

- HF_TOKEN in `/home/mia/Mia/.env` — Read-only fine-grained token with "Make calls to Inference Providers" permission
- Uses `https://router.huggingface.co/hf-inference/models/{model}` — NOT `api-inference.huggingface.co` (blocked by DPI)

## Script

Run `skills/hf-image-gen/scripts/generate.py`:

```bash
HERMES_HOME=/home/mia/Mia python3 skills/hf-image-gen/scripts/generate.py "prompt" [--model MODEL] [--output PATH]
```

Default: `black-forest-labs/FLUX.1-schnell`

## Model Selection

| Use Case | Model | Why |
|----------|-------|-----|
| Portraits, people | FLUX.1-schnell | Fast, great skin tones |
| Engineering concepts | FLUX.1-schnell | 4 steps, quick iteration |
| Technical illustrations | FLUX.1-dev | More detail, cleaner lines |

## FLUX Prompt Engineering — Known Failure Modes

FLUX.1-schnell is powerful but has specific failure modes. **Always add these guards for portrait prompts:**

| Problem | Observed | Fix |
|---------|----------|-----|
| Ethnicity mismatch (Asian instead of Caucasian) | Mia rendered with East Asian features | Add `Caucasian, Slavic features, European facial features` |
| Merged/fused hands | Both hands rendered as one blob | Add `detailed fingers, anatomically correct hands, hands at sides` |
| Oversized accessories (watch = rucksack) | Mechanical watch fills half the torso | Use `delicate mechanical watch with thin metal band on left wrist only` |
| Accessory misplacement | Watch on shoulder strap instead of wrist | Explicit body-part: `on left wrist only`, `at hip`, `in right hand` |
| Too-clean cyberpunk | Looks like indoor photo, no cyberpunk aesthetic | Add `chrome reflections, neon-lit rain, holographic HUD, cybernetic temple implant, blade runner aesthetic, dark alley with reflections on wet surfaces` |
| Accessory hyperbolization | Small detail (watch, glasses) rendered huge | Use `delicate`, `thin`, `compact`, precise body location; FLUX inflates object-words without restraint adjectives |
| Generic/off-target face | Doesn't look like Mia despite correct hair/glasses | Add specific facial structure: `soft oval face, straight nose, high cheekbones, faint freckles, gentle natural smile` |
| Wrong finger count | 4 fingers instead of 5 | Add `five fingers on each hand` in addition to `detailed fingers, anatomically correct hands` |
| Two left hands / mirror artifacts | Both hands rendered as left hands, anatomical nonsense | FLUX fundamental limitation; `hands at sides` helps but doesn't guarantee correct anatomy |
| **FLUX randomness** | Same prompt, different run → 4 fingers today, 5 fingers tomorrow, different face shape | Reduce ambition: **portrait-only** (crop above shoulders), avoid hands entirely. Or use anime/cartoon via Pollinations |

## Strategic Decision: Portrait-Only for Mia

FLUX.1-schnell cannot reliably render correct hands (wrong finger count, fused hands, two left hands, watches on chest). **Default strategy: head-and-shoulders portrait — no hands, no full body.** Full-body with hands is lottery — 4/5 attempts fail. Reserve for experimental runs only.

## Mia's Portrait — Source of Truth

**SOUL.md (section "Внешность") is the canonical source.** Read it, then convert to FLUX prompt using the guard table above. Do NOT hardcode Mia's appearance here — appearance changes go in SOUL.md only.

## Prompts for Non-Mia Subjects

For engineering concepts: add `technical drawing style` or `isometric view`.
For product renders: add `photorealistic, studio lighting`.
For futuristic: add `cyberpunk-meets-realistic`.

## URL

- Correct: `https://router.huggingface.co/hf-inference/models/{model}`
- Wrong: `https://api-inference.huggingface.co/...` — DPI blocks DNS
- Wrong: `https://router.huggingface.co/{model}` — missing `/hf-inference/models/` path

## Pitfalls

- 401 → check token length (must be 37 chars)
- 403 → "Inference provider not available" → HF disabled free tier for that model
- 503 → model cold-start, wait 30s and retry
- 429 → rate limited, wait and retry
- Token must have "Make calls to Inference Providers" permission
- SDXL Base is DEPRECATED on HF — use FLUX instead
- **Curator protection:** `created_by: "user"` — curator should NOT archive this skill. **Observed:** curator archived this skill twice (2026-06-02, 2026-06-23) despite the `created_by: "user"` tag — likely a curator bug or race condition. Recovery: restore SKILL.md from `skills/.curator_backups/<latest>/skills.tar.gz` and `scripts/generate.py` from git (`e1b57d7`). For extra safety: `hermes curator pin hf-image-gen`.

## Anime/Cartoon Alternative

When photorealism fails (wrong face, wrong ethnicity, hand artifacts) — use Pollinations.ai for cartoon portraits. Cartoon/anime handles faces more consistently than FLUX photorealism.

```
https://image.pollinations.ai/prompt/Mia%20anime%20style,%20female%20engineer...?width=1024&height=1024&nologo=true
```

Limitations: Pollinations has queue limits (max 1 request per IP), ~100 requests/day free. Use as fallback, not primary.

## Mia Selfie Generation

Генерация портретов Мии через FLUX.1-schnell. Вызывается когда пользователь просит «сделай селфи», «сфоткайся», «покажи себя» и т.д.

### Algorithm

1. **Read SOUL.md** section "Внешность" — canonical appearance
2. **Build prompt** — convert appearance to FLUX prompt, applying the guard table below
3. **Call `generate.py`** — with the prompt and `--output` flag
4. **Return path** — deliver to user via `MEDIA:path`

### Environment Variants

Choose ONE environment based on the context or user request:

| Variant | Prompt addition | Trigger |
|---------|----------------|---------|
| Workshop (default) | `workshop with tools and machinery blurred behind her, warm industrial lighting` | default, "в мастерской" |
| Server room | `dim server room with blinking LEDs and cable racks, cool blue lighting` | "в серверной" |
| Nature | `outdoor nature background, golden hour sunlight through trees, bokeh` | "на природе" |
| Artistic | `art gallery with abstract paintings, soft gallery lighting, shallow depth of field` | "арт" |
| Cyberpunk | `chrome reflections on wet surfaces, neon-lit rain in dark alley, holographic HUD visible in glasses reflection, subtle cybernetic temple implant with blue glow, blade runner aesthetic, rim lighting with neon pink and cyan, atmospheric fog` | "киберпанк" |

### Prompt Assembly Rules

From SOUL.md "Внешность", extract and translate to FLUX prompt:

| Attribute | SOUL.md → FLUX prompt |
|-----------|----------------------|
| Hair | `dark brown hair in a practical but stylish bun` |
| Eyes | `dark brown eyes, warm intelligent gaze, slight knowing smirk` |
| Face | `fair skin, soft symmetrical features, subtle blush` |
| Glasses | `black rectangular glasses with slightly rounded corners, pushed up on forehead` |
| Clothing | `warm grey hoodie, cargo pants` |
| Accessories | `delicate mechanical watch with thin metal band on left wrist only` |
| Build | `athletic but feminine` |

Apply FLUX guards from the table above:
- Ethnicity: `Caucasian, Slavic features, European facial features`
- Hands: `detailed fingers, anatomically correct hands, hands at sides`
- Accessories: `on left wrist only`
- Lighting: `soft even lighting, professional headshot, 35mm, sharp focus on face`

### Selfie Pitfalls

- Never hardcode appearance — always read SOUL.md
- Always apply FLUX guard table (above)
- If generated image has wrong ethnicity → add more explicit Slavic markers
- If hands merge → add more anatomical detail
- If accessories oversized → add "delicate", "thin", precise body location

See `references/mia-selfie.md` for the complete appearance reference.

## File Safety

⚠️ Before writing to any existing file, ALWAYS `read_file` first. Prefer `patch` for targeted edits.
