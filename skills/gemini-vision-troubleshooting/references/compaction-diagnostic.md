# Compaction: preflight vs hygiene (diagnostic 04.06.2026)

Hermes has TWO independent compression mechanisms:

| Mechanism | Where | Threshold | Triggers | Controlled by compression.enabled? |
|-----------|-------|-----------|----------|-------------------------------------|
| **Preflight** | conversation_compression.py (CLI + gateway) | 0.5 (50% tokens) | Every session load (incl. after gateway restart) | ✅ Yes |
| **Session hygiene** | gateway/run.py (~line 8624) | 0.85 + 400 msg hard limit | Gateway-only, before agent starts | ❌ No |

## Preflight (main pain)

Sits in `agent/conversation_compression.py`. Fires at every session load when tokens > 50% of model context. For DeepSeek (1M context): fires at 500K tokens. For long gateway sessions that survive multiple restarts, this triggers on EVERY restart — old messages get compressed into `[CONTEXT COMPACTION]` summary, causing context loss.

**To disable:** `hermes config set compression.enabled false` → BUT this also disables normal mid-conversation compression.

**Recommended:** raise threshold: `hermes config set compression.threshold 0.9` → 900K tokens for DeepSeek.

## Session hygiene (rare, gateway-only)

Sits in `gateway/run.py` lines 8624-8650. Fires when:
- Messages > 400 (hard limit), OR
- Token estimate > 85% of model context

Uses REAL model from config (not the hardcoded Claude default on line 8652 — it's overridden on line 8665 from `model.default` in config.yaml).

**Cannot be disabled via config flag** — `compression.enabled: false` doesn't affect it (different mechanisms). Can only be disabled by code change or by setting `hygiene_hard_message_limit` very high.

## Diagnostic commands

```bash
# Check current compression config
hermes config check | grep -A3 compression

# View the actual thresholds
grep -n 'hygiene\|_hyg_threshold\|hard_msg_limit' gateway/run.py

# Monitor gateway logs for compaction events
grep -i 'compaction\|compression\|preflight\|hygiene' ~/Mia/logs/gateway.log | tail -20
```

## Key insight

Preflight is the culprit for most "compaction ate my context" complaints. It fires on session LOAD (not on message send), which means after every gateway restart. Hygiene is a safety net that almost never fires (85% threshold for DeepSeek 1M = 850K tokens).

## Twin handoff

Full diagnostic was handed off to Cursor-Мия in `handoff_20260604_compaction_diagnostic.md`. Twin's recommendation: raise preflight threshold to 0.9, keep hygiene as-is.
