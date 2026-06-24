# E39 → E60 Rear Brake Conversion (540i/545i)

**Status:** planned/indirect — основная механика подтверждена, есть открытые вопросы.

## Vehicle Requirements

- **Donor:** дорестайл E60 540i/545i седан (до 03/2005)
- **Recipient:** E39 **до 09/2001** (после 09/2001 — требуются рычаги от E60)
- Сергей: E39 535i 2000 г. — подходит

## Verified BOM (confirmed via multiple live sources)

### Buy from E60

| # | Part | OEM | Qty | Verified |
|---|---:|---:|---|
| 1 | Кулак задний левый | 33326770905 | 1 | ✅ |
| 2 | Кулак задний правый | 33326770906 | 1 | ✅ |
| 3 | Диск тормозной 345×24 мм | 34216763827 | 2 | ✅ |
| 4 | Суппорт задний левый | 34216753679 | 1 | ✅ |
| 5 | Суппорт задний правый | 34216753680 | 1 | ✅ |
| 6 | Скоба суппорта | 34216766074 | 2 | ✅ |

### Keep from E39 (confirmed compatible)

| Part | OEM | Verification |
|---|---|---|
| Ступица задняя | 33411093371 | ЦО 74.1 мм совпадает E39/E60 |
| Подшипник ступицы | 33411095652 | Общий для E39 и E60 |

### Confirmed identical E39/E60 (keep E39 parts)

| Part | OEM | Source |
|---|---|---|
| Колодки ручника | 34416761293 | Schmiedmann, RM European, Bimmerworld — единый номер на E39+E60 |
| Разжимной замок ручника | 34416851439 | Bimmerworld: E39 1997-2003 и E60 2004-2010 в одном списке |

### Parking brake architecture

Both E39 and E60 use **drum-in-rotor** parking brake (not integrated into caliper). The expanding lock (34416851439) and shoes (34416761293) are the same parts. Only the **cables** differ:
- E39: 34401166237
- E60: 34406770602
- Test-fit required: E39 cables may work with E60 knuckles; if too short, switch to E60 cables.

## Compatibility Notes

- **Driveshafts:** 30 splines — совпадает E39/E60
- **Ball joints and integral links:** общие для обеих платформ
- **Knuckles:** bolt-on на рычаги E39 (при условии E39 до 09/2001)
- **Splined hub:** 33411093371 (E39) переиспользуется

## Open Questions (not yet verified)

1. **Wheel fitment** — 345 mm discs may not clear all wheel designs. Test-fit required, especially for winter R17 if applicable.
2. **H-arm bushings** — some reports that E60 subframe mounting points differ. May require drilling or adapters. No confirmed part numbers.
3. **Caliper spacers/brackets** — unclear if any are needed beyond the E60 carrier brackets (34216766074).
4. **Brake pads for E60** — not yet looked up. Need RealOEM for correct compound.
5. **Brake hoses** — E60 hoses may be needed; not yet confirmed.
6. **Bolts/hardware** — carrier-to-knuckle and caliper-to-carrier bolts. Usually included with calipers/carriers but verify.

## Sources Verified (live, 13 June 2026)

- Bimmerworld: expanding lock 34416851439 fitment list (E39 + E60)
- Schmiedmann: brake shoes 34416761293 fitment (E39 + E60)
- Pelican Parts: E60 parking brake drum-in-rotor architecture confirmed
- FCP Euro: expanding lock 34416851439 commonality confirmed
