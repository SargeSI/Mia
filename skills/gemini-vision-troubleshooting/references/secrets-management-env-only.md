# Secrets Management — Critical Security Rule

**Date:** 3-4 June 2026
**Status:** Resolved — lesson embedded in SOUL.md

## The Incident

Twice during configuration, API keys were placed in `/etc/systemd/system/hermes-gateway.service.d/env.conf` (systemd Environment override) instead of `.env`:

| Key | When | Why |
|---|---|---|
| `GOOGLE_API_KEY` | 31 May 2026 | `hermes doctor` falsely reported missing key (checks `os.environ`, not `.env`) |
| `OPENAI_API_KEY` | 4 June 2026 | STT troubleshooting — wanted to "quickly fix" env loading |

Both keys were exposed in plaintext in a world-readable systemd file.

## Root Cause

Agent's incorrect assumption: "gateway via systemd does not inherit `.env` → must put keys in systemd Environment."

## Reality

Hermes reads `.env` via `load_env()` (see `hermes_cli/config.py` and `agent/credential_pool.py`). The function `_get_env_prefer_dotenv(key)` checks `.env` FIRST, then falls back to `os.environ`. Systemd `Environment` / `EnvironmentFile` is NOT needed for Hermes to find keys.

Additionally, `python-dotenv` is a dependency (`pyproject.toml` line 35: `"python-dotenv==1.2.2"`).

## Rule (embedded in SOUL.md since 4 June 2026)

> Все API-ключи — ТОЛЬКО в `.env`. Никаких ключей в systemd Environment. `load_env()` уже работает.

## Lessons

1. **Never put secrets in systemd Environment** — they are visible in `systemctl cat`, `ps aux`, and `/proc/<pid>/environ`.
2. **`hermes doctor` can lie** — it checks `os.environ`, not `.env`. Don't trust its "missing key" reports without verifying.
3. **Prefer understanding the architecture over quick fixes.** `load_env()` was already working. The systemd route was unnecessary and dangerous.
