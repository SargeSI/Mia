# E53 X5 Tire Selection — June 2026

> Cross-reference: LightRAG document `tires-e53-selection.md` (full research log with all rejected candidates and reasons).
> Price monitoring: cron job `80fc6aa914cd`, Mondays 9:00 AM MSK.

## Summer (purchased)

**Nexen N'Fera RU1** — UHP Summer, asymmetric tread

| Axle | Size | Index | EU Wet | EU Fuel | Noise | Price/ea |
|---|---|---|---|---|---|---|
| Front | 255/50 R19 | 107W XL | A | C | 70 dB | 14 530 ₽ |
| Rear | 285/45 R19 | 111W XL | A | C | 71 dB | 15 080 ₽ |

**Total: 59 220 ₽** for 4 tires

**Why RU1:**
- Wet grip A on both axles — critical for heavy SUV
- OE on Porsche Cayenne (2016+) and Macan — verified via PR Newswire press release
- RU5 rejected: all-season (worse wet grip C–D), unnecessary with separate winter set

**OE proof:** https://www.prnewswire.com/news-releases/nexen-tire-supplies-original-equipment-tires-for-the-porsche-cayenne-300322435.html

## Winter (candidate)

**Ikon Character Ice 8 SUV** 255/55 R18 109T XL — 14 820 ₽/ea (mosautoshina.ru, June 2026)

- Based on Nokian Hakkapeliitta 9 generation (Nordman 8 = Character Ice 8)
- XL rated for heavy SUV
- Separate R18 wheel set for winter

**Rejected candidates (all 255/55 R18 109T unless noted):**

| Model | Price | Why rejected |
|---|---|---|
| Ikon Character Ice 7 / Nordman 7 | ~12 400 ₽ | Same tire, older gen (Hakka 8), both are duplicates of each other |
| Gislaved SpikeControl SUV | 13 110 ₽ | No XL rating — dealbreaker for X5 4.4i |
| Yokohama IG65 | 13 900 ₽ | Good but noisier, ice grip slightly worse than Ikon 8 |
| Nexen Winguard Spike 3 | 12 540 ₽ | Budget, weaker ice performance |
| Kumho Wintercraft WI32 | — | Weak stud, soft sidewall |
| Roadstone Winguard Spike | — | Budget Nexen sub-brand |
| Cordiant Snow Cross 2 | 10 030 ₽ | Noisy, average ice grip |
| Viatti Bosco Nordico | 10 900 ₽ | Budget compound, weak stud retention |

**Price monitoring:** cron job `80fc6aa914cd`, Mondays 9:00 AM MSK, checks all 4 viable models (Character Ice 8, Nordman 8, IG65, Winguard Spike 3). Silent unless >5% drop.

## E53 Tire Sizes Reference

| Season | Wheels | Front | Rear |
|---|---|---|---|
| Summer | 19″ staggered | 255/50 R19 | 285/45 R19 |
| Winter | 18″ square | 255/55 R18 | 255/55 R18 |
