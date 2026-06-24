# Groq / STT Debugging Chain

**Date:** 4-6 June 2026
**Symptom:** Voice transcription fails with 403 Forbidden

## Chain of Discovery

| Step | Attempt | Result | What we learned |
|---|---|---|---|
| 1 | Groq through VPN (tg-dubai) | 403: error code 1010 | Cloudflare WAF blocks VPN IP `188.208.110.155` |
| 2 | Groq without VPN (direct) | 403: Forbidden | Geo-blocking — Russia not supported |
| 3 | Groq without VPN | `unsupported_country_region_territory` | Actually came from OpenAI (config had `stt.provider: openai`), not Groq |
| 4 | Switched to `stt.provider: openai` | 403 | OpenAI also blocks Russia — needs API key + VPN |
| 5 | With OPENAI_API_KEY | Pending test | — |

## Root Cause

Groq API is behind Cloudflare. Cloudflare WAF blocks traffic from VPN IP `188.208.110.155` (likely flagged as suspicious/proxy). Direct access from Russia is also blocked by Groq's geo-restrictions.

## Key Lessons

1. **Check `stt.provider` in config first** — we spent time debugging Groq when config was set to `openai`
2. **Credentials ONLY in `.env`** — the debugging chain led to OPENAI_API_KEY being exposed in systemd `env.conf`. See `references/secrets-management-env-only.md`
3. **Hermes reads `.env` via `load_env()`** — no need for systemd EnvironmentFile. See `references/secrets-management-env-only.md`
4. **Groq key format:** `gsk_` prefix, 56 chars, NO quotes in any valid key

## Current Status

`stt.provider: openai` with `OPENAI_API_KEY` in `.env`. Awaiting test with gateway restart.
