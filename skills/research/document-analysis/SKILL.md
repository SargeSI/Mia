---
name: document-analysis
description: "Analyse tenders, procurement documents, contracts (docx/xlsx) — extract key requirements, identify contradictions, write structured analytical notes (справки)."
version: 1.0.0
tags: [research, analysis, tender, procurement, documents, справка]
---

# Document Analysis — Tender & Procurement Intelligence

Analyse procurement documents, tenders, contracts, and technical specifications. Extract key requirements, cross-reference contradictions, and produce structured analytical notes (справки).

## Trigger conditions

- User sends .docx, .xlsx, .pdf files from a procurement/tender
- User asks to «изучить документы и написать справку»
- User needs competitive intelligence from tender documentation

## Workflow

### Phase 1: Read documents

1. Install Python readers if missing:
   ```bash
   pip install python-docx openpyxl --break-system-packages
   ```

2. Read .docx:
   ```python
   from docx import Document
   doc = Document('path/to/file.docx')
   for para in doc.paragraphs:
       if para.text.strip():
           print(para.text)
   ```

3. Read .xlsx (all sheets):
   ```python
   import openpyxl
   wb = openpyxl.load_workbook('path/to/file.xlsx')
   for sheet_name in wb.sheetnames:
       ws = wb[sheet_name]
       for row in ws.iter_rows(min_row=1, max_row=ws.max_row, values_only=False):
           cells = [str(c.value) if c.value is not None else "" for c in row]
           print(" | ".join(cells))
   ```

4. Check for tables in .docx:
   ```python
   for table in doc.tables:
       for row in table.rows:
           print([cell.text for cell in row.cells])
   ```

### Phase 2: Cross-reference

- Compare key parameters across documents (ТЗ vs КП vs АСТ/анкета)
- Identify contradictions: price fixation, VAT, contract terms, SLA
- Classify requirements: blocking (B) vs additional (D)

### Phase 3: Write справка (analytical note)

Structure:
1. **Предмет закупки** — what's really being bought
2. **Ключевые параметры** — table with реализуемость assessment
3. **Блокирующие критерии** — what disqualifies bidders
4. **Внутренние противоречия** — contradictions between documents
5. **Стратегический анализ** — market implications
6. **Резюме** — actionable conclusions

Use comparison tables. Mark реализуемость: ✅ / ⚠️ / ❌.

### Phase 4: Save reference

After completion, save the specific analysis as `references/<tender-name>-<year>.md` for future competitive intelligence.

## Pitfalls

1. **python-docx and openpyxl may not be installed** — install on first use
2. **Excel formulas vs values** — `cell.value` returns the formula if not evaluated; use `data_only=True` if needed
3. **Multi-sheet Excel** — always scan all sheets, important details may be in unexpected tabs
4. **docx paragraphs without text** — filter `para.text.strip()` to skip empty formatting runs
5. **Contradictions between documents** — always cross-reference ТЗ, КП, and compliance questionnaire; procurement documents notoriously conflict
6. **SaaS/PaaS marketing** — tenders often use IT terminology for non-IT services; identify what's actually being procured vs what they CALL it

## Reference files

- `references/x5-tender-2026.md` — X5 Digital drone delivery tender analysis (Jun 2026)
