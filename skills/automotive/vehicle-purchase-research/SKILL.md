---
name: vehicle-purchase-research
description: >-
  Research, compare, and evaluate vehicle purchase options — motorcycles and cars.
  Russian market focus: specs, reliability, real listings, budget analysis, strategy recommendations.
triggers:
  - купить мотоцикл
  - купить машину
  - выбор мотоцикла
  - выбор авто
  - замена мотоцикла
  - замена авто
  - сравни мотоциклы
  - сравни машины
  - шорт-лист
  - что взять
  - присматриваю
---

# Vehicle Purchase Research

Researching and comparing vehicle purchase options for the Russian market. Covers motorcycles and cars: specifications, common problems, real market prices, and budget-fit strategies.

## Core Principles

1. **Never estimate prices from memory.** Always check live listings on Russian marketplaces. Guessing prices is the #1 pitfall — the user sees real listings, and estimated prices that don't match erode trust immediately.
2. **Trust the user's market observations.** If the user says «I see listings at price X» and your estimate says Y, the user is right. Go verify with live searches.
3. **Budget = purchase + mandatory post-purchase work.** A motorcycle at 1.8M with 200K in immediate maintenance is a 2M purchase, not 1.8M.
4. **Pitfall — under-estimating budget-fit:** It's better to say «this stretches to 2.1M» and let the user decide, than to exclude a valid candidate based on wrong price estimates.

## Research Workflow

### Step 1: Understand criteria
- Vehicle class (sport-tourer, tour-enduro, cruiser, etc.)
- Key requirements (passenger comfort, shaft drive, engine configuration)
- Budget range
- Age/mileage preferences

### Step 2: Gather specs and reliability data
- **Web search** (`web_search`) for each model: specs, known issues, owner reviews
- **Web extract** (`web_extract`) from:
  - Owner forums: bikepost.ru (motorcycles), drive2.ru (cars), bmwclubmoto.ru, bmwmotorradclub.ru
  - Wiki sites: bikeswiki.ru (motorcycles)
  - Model-specific forums: k1600forum.com, goldwingfacts.com, etc.
- Extract: engine specs, weight, transmission, typical problems, maintenance costs

### Step 3: Check real market prices (CRITICAL — never skip)
**Russian marketplaces (live listings):**
- `auto.ru` — largest Russian vehicle marketplace. Use site:auto.ru in web_search
- `drom.ru` — strong in Far East, Japanese imports
- `avito.ru` — private sellers
- `farpost.ru` — Vladivostok, Japanese auction arrivals

**Japanese auction aggregators (for JDM imports):**
- `autosender.ru` — auction price estimates
- `priority-auto.ru` — auction listings
- `japanlife-moto.ru` — motorcycles in stock in Vladivostok
- `car-blank.ru` — auction import services

**Price search query patterns:**
- `site:auto.ru [model] купить цена` — for auto.ru
- `[model] купить бу цена пробег Россия` — general
- `[model] продажа Владивосток аукцион Япония` — for Japanese imports
- Include year filters to narrow: `2025 2026`

**Add ~30-50% to Japanese auction prices for landed cost** (shipping, customs, registration).

### Step 4: Build comparison table
Structure with columns:
- Model and years
- Price range (real, from listings)
- Typical mileage at that price
- Remaining budget (assuming mid-range purchase)
- Key specs (engine, power, weight)
- Passenger comfort rating (★/5)
- Known problems summary
- Unique advantage / «trump card»

### Step 5: Present strategy options
Group candidates into strategies, not just a ranked list. Examples:
- **Strategy A — «Rational minimum»**: cheapest reliable option, max budget remaining
- **Strategy B — «Technology leap»**: modern electronics, adaptive cruise, latest engine
- **Strategy C — «Known quantity»**: same model, fresher example — zero learning curve

Each strategy gets: price, remaining budget, what you get, what you sacrifice.

## Motorcycle-Specific Knowledge

**Reference:** `references/motorcycle-comparison-data.md` — structured data on 7 touring motorcycles (Gold Wing, K1600, GTR1400, RT series, ST1300) with specs, problems, and Russian market prices as of June 2026.

### Russian Motorcycle Market Notes

- **Japanese auctions** are the primary source for used Japanese motorcycles. Vladivostok is the entry point.
- **ST1300** production ended ~2013 in most markets, but Japanese auction examples with 30-60K km still appear regularly.
- **GTR1400** was discontinued in Europe after 2016 (Euro-4), but continued for North America through 2022. Japanese auction examples are plentiful.
- **BMW K1600** series: GTL vs GT — GTL has taller windshield, softer suspension, top case standard, passenger armrests. GT is sportier, lighter, lower bars.
- **BMW RT series**: R1200RT (2014-2018) → R1250RT (2019-2025, ShiftCam) → R1300RT (2026+, new boxer).

## Pitfalls

- **«I estimate prices at...» — STOP.** If you don't have live listing data, run the search. Guessing leads to wrong exclusion of valid candidates and user frustration.
- **Excluding candidates based on wrong price estimates.** When the user says a model fits the budget, verify before disagreeing.
- **Forgetting post-purchase costs.** A cheap motorcycle that needs 200K in immediate maintenance may total more than a pricier but ready-to-ride option.
- **Comparing across incompatible classes.** Don't pit a Gold Wing against a sport-naked. Confirm the class first.
- **Ignoring passenger requirements.** When the user specifies «с женой», passenger comfort is a first-class criterion, not an afterthought.
