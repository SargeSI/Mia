---
name: retro-gaming-hardware
description: Complete retro gaming hardware lifecycle — pre-purchase research, model variant identification, defect assessment, market evaluation, inspection checklists, and console repair procedures. Covers PS3, PS Vita, and similar retro consoles/handhelds.
---

# Retro Gaming Hardware

Covers the full lifecycle of retro gaming hardware ownership: researching what to buy → evaluating specific units → inspecting before purchase → diagnosing issues → repairing common failures.

## Sections

- [Retro Hardware Research](#section-1-retro-hardware-research) — pre-purchase evaluation
- [Console Repair](#section-2-console-repair) — post-purchase diagnostics and repair

---

## Section 1: Retro Hardware Research

Systematic pre-purchase research for used/retro gaming hardware. Helps answer "do I need it", "which variant", and "what to check" before buying.

### Triggers

- "стоит ли купить [console]"
- "какую версию [console] выбрать"
- "чем отличается [model A] от [model B]"
- Any retro console/handheld evaluation before purchase

### Methodology

#### Phase 1: Need Analysis
- Ask: **what do you want to play on it?** This determines whether the hardware is right at all
- Identify alternatives (modern clones, emulation, other consoles)
- The native library is the decisive factor — if they want those specific games, original hardware wins

#### Phase 2: Model/Variant Identification
- Research ALL model variants (revisions, regions, special editions)
- Key differentiators: screen technology, internal storage, port types, SoC revisions, known defects
- Use authoritative sources: consolemods.org, psdevwiki, reddit r/<console>hacks, GBAtemp
- **Pitfall:** SKU codes from wikis may not match what's printed on the device sticker. Verify with real photos on eBay before claiming "the sticker says X"

#### Phase 3: Defect Research
- Identify model-specific failure modes and their prevalence
- Distinguish repairable defects from unfixable ones
- Prioritize: unfixable defects (e.g., OLED burn-in) > difficult repairs > easy repairs > cosmetics

#### Phase 4: Modding & Upgrade Path
- CFW/homebrew status: which firmware versions are hackable?
- Storage expansion options (SD adapters, internal mods)
- Port upgrades (USB-C mods, battery replacements)
- Part availability and cost for common repairs

#### Phase 5: Market Evaluation
- Check current market prices on Avito, eBay, local marketplaces
- Identify fair price range for each variant
- Flag overpriced listings vs bargains vs potential scams (franken-consoles, aftermarket shells)

#### Phase 6: Inspection Checklist
- For in-person inspection: specific tests to run, what to look for visually
- For remote purchase (photos only): what to ask seller to photograph, red flags in photos
- Specific screen test patterns (which colors/backgrounds reveal which defects)

---

## Section 2: Console Repair

Diagnose and repair gaming consoles. Covers common failure modes, part sourcing, and step-by-step repair instructions.

### Triggers

- Console failure symptoms: beeping, flashing lights, no power, YLOD, RLOD
- "моя [console] не включается / пищит / мигает"
- User asks for repair plan or part list

### Workflow

#### Phase 1: Diagnosis
- Identify exact model number (CECHxx for PS3, PCH-xxxx for Vita, etc.)
- Match symptoms to known failure modes
- Distinguish between power supply, capacitor, and BGA issues based on behavior patterns
- **Key differentiators:** cold-start behavior (capacitors), load-dependent failures (PSU), progressive worsening (caps), sudden death (BGA)

#### Phase 2: Repair Plan
- Confirm required parts with exact specifications
- Source parts locally (list specific stores and part numbers when possible)
- List required tools
- Assess difficulty and whether DIY or professional repair is appropriate

#### Phase 3: Repair Instructions
- Disassembly steps
- Component replacement procedure with photos/links to references
- Reassembly and testing

---

## Reference Files

- `references/ps-vita-buying-guide.md` — PS Vita Fat (PCH-1000) complete buying guide with model matrix, defect catalog, modding paths, and market data
- `references/ps3-nec-tokin-replacement.md` — PS3 Fat NEC/TOKIN capacitor replacement (YLOD fix), CECHH08-specific, parts in Moscow

## Pitfalls

1. **SKU vs sticker** — wiki SKU codes often don't match the sticker on the device. Verify with real photos.
2. **Franken-consoles** — units with aftermarket shells and knockoff replacement displays. Price below market is suspicious.
3. **OLED replacement displays** — many "OLED" replacements on AliExpress are actually LCD. Verify before ordering.
4. **Capacitor polarity** — reversing tantalum capacitor polarity causes a short circuit on power-on. Always verify with a multimeter.
5. **BGA vs capacitor confusion** — cold-start-only failures (works after warm-up) are capacitor problems, not BGA. Heat-gun and reballing won't fix capacitor degradation.
6. **Model-specific failure modes** — not all console generations have the same defects. Research the *specific model revision* before diagnosing.
