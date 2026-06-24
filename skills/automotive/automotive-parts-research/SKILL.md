---
name: automotive-parts-research
description: Research and select automotive parts — tires, suspension, brakes, electronics. Multi-source verification, EU labels, OE claims, market classification awareness. For BMW E39/E53 and other vehicles.
---

# Automotive Parts Research

Use this skill when the user asks to research, compare, or select automotive parts — tires, suspension components, brake parts, electronics, or accessories.

## Core Principles

1. **Multi-source verification** — never trust a single source. Cross-check manufacturer specs, independent tests, user reviews, and EU labels.
2. **OE claims must be backed by primary sources** — «factory equipment on Porsche» needs a press release or OEM database, not a forum post.
3. **Classification varies by market** — a tire sold as «all-season» in the US may be sold as «летняя» in Russia. Check the actual spec (compound, tread pattern, test category), not just the label.
4. **For heavy vehicles (SUV, truck) — load index and XL rating are non-negotiable.** If a candidate lacks XL for a 2+ ton vehicle, it's out regardless of other merits.

## Tire Research Workflow

**Reference:** `references/tire-market-notes.md` — knowledge bank of tire model classifications, rebrandings, test summaries, and EU labels. Check before researching a model that was already analyzed.

### Step 0: Check existing data before asking the user

Before asking the user for vehicle specs (engine, weight, driving style, VIN):
- **Query LightRAG** (`mcp_LightRAG_rag_query` + `rag_search_entities`) — VIN, бортжурнал, previous tire discussions, vehicle specs
- **Search Obsidian** (`search_files` in `/home/sarge/Second_Brain`) — vehicle-specific notes, maintenance logs, tire size history
- If data exists, use it to narrow the analysis. If not, ask concisely.
- **Pitfall:** skipping this step and asking the user «какой двигатель?» when the answer is in their own knowledge base is a workflow error. The user expects you to check available sources first.

### Step 1: Identify the class
- Summer UHP vs Touring vs All-Season vs Winter studded/studless
- Don't compare across classes — eliminate the wrong class first

### Step 1.5: Clarify actual usage conditions (BEFORE filtering by specs)
- **Speed:** Ask what speeds the user actually drives, not what the engine/chip can theoretically do. A chipped 220+ hp car does NOT automatically need Y-rated tires if the owner never approaches 270 km/h. Filtering by theoretical max wastes time and eliminates good candidates.
- **Weather:** Ask what weather the car sees. If the user has multiple vehicles (e.g., motorcycle for sunny days), the car may be primarily for wet weather — this flips priorities toward wet grip + aquaplaning > dry grip.
- **Vehicle role:** Summer-only daily, weekend car, rain-day backup, highway cruiser, city runabout — each reshapes the priority matrix.
- **Pitfall:** assuming «fast car = Y-rating» or «summer tire = all conditions» without asking.

### Step 2: Check EU labels (the three numbers)
- **Wet grip** (A–E): most critical safety metric. Difference A→E = up to 18m braking at 80 km/h
- **Fuel efficiency / rolling resistance** (A–E): ~7.5% consumption difference A→E
- **Noise** (dB): 3 dB = double sound intensity
- Prefer tires with wet grip A or B for heavy vehicles

### Step 3: Verify OE claims
- Search for manufacturer press releases (PR Newswire, official site)
- OEM databases (FCP Euro, Turner Motorsport) as secondary confirm
- Porsche/BMW/Mercedes OE contracts are publicly announced
- **OE fitments are a quality signal, especially for wet performance:** premium OEMs (Porsche, VW Group) prioritize wet grip and aquaplaning in their OE approval process. A tire that passed Porsche's OE qualification is almost certainly strong in wet conditions — use this as a shortcut when wet weather is a priority.
- **Known OE references:** Nexen N'Fera Sport — OE on Porsche Panamera (Gen 2), Porsche Cayenne (2024, all variants except Turbo GT), VW Golf 8, SEAT Leon. See `references/nexen-oe-fitments.md`.

### Step 4: Check fitment specifics
- Load index sufficient for axle weight
- XL (Extra Load) for SUVs
- Speed rating adequate (H = 210, V = 240, W = 270 km/h)
- Staggered setups: confirm both sizes exist in the model

### Step 5: Price monitoring
- Record baseline price at decision time
- Set up cron job for periodic checks if user wants to wait for discount
- Threshold: notify only on significant drop (>5%)

## BMW-Specific Knowledge

### E53 X5 Audio / I-Bus

- **BlueBus:** Bluetooth adapter that emulates CD changer on I-Bus. Replaces (not supplements) the physical CD changer. $199. S/PDIF digital output to DSP.
- **AUX input location:** in the monitor harness, ~10 cm from the 16:9 display, NOT in the glovebox or trunk
- **AUX gain adjustment:** through BM54 service mode (NOT MK4 navigation computer — MK4 is navigation only, sound goes through BM54 radio module)
  - Access: ignition pos 1 → radio ON → hold SELECT ≥8 sec → scroll to TONE LINE → presets #1–6
  - For vehicles 09/2001–03/2002: SELECT button
  - For earlier vehicles: INFO → RDS → hold right knob ≥8 sec
- **DSP S677:** Top Hi-Fi with digital signal processor. BM54 is the radio module, separate from MK4 nav computer.

### BMW E53 X5 Brake/Suspension Diagnostics

- **Front control arms (31126760275 left, 31126760276 right):** OE supplier is **Lemförder** (part of ZF Group). Lemförder numbers: 3048601 (left), 3048701 (right).
- **Warped discs → ball joint failure chain:** Axial runout from warped rotors sends micro-impacts through the hub directly into the ball joint. Silent blocks are spared (they handle radial/torsional loads). This explains why ball joints fail repeatedly while bushings look fine.
- **Stub axle runout check:** Required tool — dial indicator (0.01 mm resolution) + magnetic stand. TIS spec: ≤0.02 mm axial runout on the mounting flange. If out of spec, the stub axle must be replaced — new discs will warp within 1000 km regardless of quality.
- **Causes of repeated brake disc warping (in priority order):**
  1. Stub axle flange runout (>0.02 mm) — disc sits crooked, heats unevenly, warps
  2. Stuck caliper (collapsed brake hose acting as check valve, seized guide pins)
  3. Hub bearing play or incorrect torque
  4. Disc mounting surface contamination (rust, paint, debris)

## Pitfalls

- **Speed rating over-escalation:** Don't convert engine specs or chip-tuning numbers into required speed rating without asking. A chipped 220+ hp car does NOT automatically need Y-rated (300 km/h) tires if the owner never approaches those speeds. Before filtering by speed index, ask: «What speeds do you actually drive this car at?» Filtering the entire shortlist by theoretical max wastes time and eliminates good candidates that are perfectly adequate for real-world use.
- **«All-season» vs «летняя» confusion:** Russian sellers often label all-season tires as summer because «all-season» is not a recognized category in Russia. Check the actual tire classification on manufacturer's global site or international retailers (Tire Rack, SimpleTire, tyre reviews). **Known examples:** Nexen N'Fera AU7 — on SimpleTire (US) listed as UHP All-Season, in Russia sold as «летняя». EU label wet grip C (255/45R20) — reject for pure summer use unless user explicitly wants all-season. Ikon/Nokian Nordman SZ2 and Character Ultra are the SAME tire — Nokian Tyres rebranded to Ikon Tyres in 2025, Nordman SZ2 renamed to Character Ultra. Do not treat as separate options.
- **XL is non-negotiable for heavy SUVs:** Gislaved SpikeControl is a good winter tire but lacks XL. For an E53 X5 4.4i (~2.2 tons), this is a deal-breaker — sidewall too soft, risk of blowout under load.
- **MK4 ≠ BM54:** MK4 is the navigation computer (maps, GPS, display). BM54 is the radio module (sound, AUX, amplifier). Service mode for AUX gain is in BM54, not MK4.
- **BlueBus kills the CD changer:** It physically occupies the same I-Bus connector. No pass-through, no coexistence.
- **Never trust a single price:** Always check the full alternative table on the product page — often reveals hidden gems or confirms the candidate is overpriced.
- **Previous research (LightRAG, twin, past sessions) is INDIRECT evidence, not confirmed fact.** Especially for safety-critical systems (brakes, steering, suspension cross-model conversions): every compatibility claim must be re-verified against live primary sources (manufacturer catalogs, RealOEM cross-reference, retailer fitment databases like FCP Euro/Bimmerworld). LightRAG stores what was concluded — not necessarily what was verified. Treat stored research as «planned/indirect» until you confirm each claim with a live lookup.
