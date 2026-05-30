# Chunker Performance Test — 29.05.2026

## Test 1: Small session (cron_003e29c8a5f2, 3 msgs)
- **Result:** ✅ Passed
- **Embedding:** 3/3 messages, batch_size=5
- **Clusters found:** 1 (threshold=0.5)
- **Saved to DB:** yes, message_range 9883-9888
- **DeepSeek:** not called (below min_cluster_size)
- **Time:** <2 seconds

## Test 2: Large session (cafbb586... E39_diagnostics, 525 msgs)
- **Result:** ❌ Failed — Ollama ReadTimeout
- **Attempt 1:** BATCH_SIZE=50, timeout=120s → failed at first batch
- **Attempt 2:** BATCH_SIZE=5, timeout=120s → passed 50 embeddings, failed at 55th
- **Attempt 3:** BATCH_SIZE=1 → theoretical 17 minutes, not attempted
- **Root cause:** qwen3-embedding:0.6b on CPU (192.168.51.17) can't sustain >100 embeddings synchronously
- **Practical limit:** ~100 messages (20 batches × 5, ~2 minutes)
- **Recommended fix:** Async embed with 5-10 parallel requests, or GPU

## Hardware
- Ollama host: 192.168.51.17:11434
- Model: qwen3-embedding:0.6b (1024-dim)
- Batch API: /api/embed (not /api/embeddings)
- Timeout in batch_embed(): 120s (hardcoded in recall.py line 49)
