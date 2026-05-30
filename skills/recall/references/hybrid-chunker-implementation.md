# Hybrid Chunker — Implementation & Testing Results

**Date:** 2026-05-29  
**Implemented by:** Cursor-Мия  
**Spec:** `hybrid-chunker.md`

## Architecture

Two-stage chunker replacing the old LLM-only approach:

### Stage 1: Embedding-based boundary detection (free, local)
- `qwen3-embedding:0.6b` via Ollama `/api/embed`
- Batch embeddings (20 texts per batch, 120s timeout)
- Cosine distance between consecutive messages
- `boundary_threshold: 0.5` — above this = topic shift = cluster boundary

### Stage 2: DeepSeek title/summary (paid, rare)
- `deepseek-v4-flash` (no thinking, for speed)
- ~200 input tokens + ~100 output per cluster
- 10 clusters = 2000 tokens total (vs 64000 in old LLM-only version)
- Only runs at `/new` (session completion) — rare enough

## Files Changed

| File | Change |
|---|---|
| `recall.py` | New `EmbeddingClient.batch_embed()` method |
| `chunk_session.py` | Full rewrite: embedding boundaries + DeepSeek per cluster |
| `recall_config.json` | Added `chunking` section |
| `gateway/run.py` | No changes — `_bg_chunk_async()` hook already in place |

## Known Issue

Ollama on 192.168.51.17 times out on batches > 20 texts. Sessions up to 200 messages (10 batches) work fine. For 1200+ message sessions — increase `batch_embed()` timeout (currently 120s) or split into smaller batches.

## Verification

```sql
-- Check clusters after /new
SELECT cluster_title, message_range_start, message_range_end 
FROM session_clusters 
ORDER BY message_range_start;
```
