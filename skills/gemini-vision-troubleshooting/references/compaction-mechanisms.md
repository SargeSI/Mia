# Context Compaction — Two Mechanisms

**Date:** 4 June 2026
**Source:** Code inspection of `gateway/run.py`, `agent/conversation_loop.py`, `agent/conversation_compression.py`

## Problem

User observed context being compacted mid-conversation, losing important dialogue context. The agent was confused about what triggers compaction and whether `compression.enabled: false` would stop it.

## Two Independent Mechanisms

| Mechanism | Where | Threshold | Controlled by `compression.enabled`? |
|---|---|---|---|
| **Preflight compression** | `agent/conversation_loop.py` line ~633 | 50% of context window (configurable via `compression.threshold`) | ✅ YES |
| **Session hygiene** | `gateway/run.py` lines 8624-8659 | 85% AND hard limit 400 messages | ❌ NO |

### Preflight Compression

Fires at agent startup (CLI and gateway). Checks if the loaded session history exceeds `compression.threshold` (default 0.5 = 50% of context window).

For DeepSeek v4-pro (1M tokens), threshold is 500K tokens. Our sessions rarely reach this — the problem is actually triggered by continuation compaction (see below).

Config key: `compression.threshold` (default 0.5).

### Session Hygiene (Gateway-only)

Fires at session load time in gateway. Three triggers:
1. Messages ≥ 4 AND tokens ≥ 85% of context window
2. Messages > 400 (hard limit)
3. Actual API-reported `last_prompt_tokens` from previous turn

The model used for token estimation is taken from `config.yaml` → `model.default`, NOT the hardcoded Claude fallback.

Config key: `hygiene_hard_message_limit` (default 400, in `hermes_cli/config.py` line 994).

### Continuation Compaction

A third mechanism: when gateway restarts and resumes a session, old messages are compacted into `[CONTEXT COMPACTION — REFERENCE ONLY]` blocks. This is triggered in `gateway/run.py` around line 2837 (continuation path). This is the one that most often annoys users — it fires on every gateway restart for long sessions.

## Solution Paths

1. **Raise `compression.threshold`** to 0.9 — preflight won't trigger but stays as safety net
2. **Set `compression.enabled: false`** — stops preflight, session hygiene still active independently
3. **Edit `hygiene_hard_message_limit`** to a very high number — effectively disables hygiene
4. **Code change** — add a flag for continuation compaction specifically

## Recommendation (from twin, handoff_20260606)

Don't disable compression entirely. Raise threshold to 0.9:
```yaml
compression:
  threshold: 0.9
```
This stops preflight from firing on every restart but keeps it as protection for genuinely large sessions. Hygiene (85% + 400msgs) and DeepSeek's huge context window make actual compaction rare.
