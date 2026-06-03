# -*- coding: utf-8 -*-
"""
Incremental chunker with queue-based batching.

Two modes:
  --mode full       : batch-embed all messages (for initial indexing, legacy)
  --mode incremental: add new texts to existing clusters via centroid matching

Usage:
  python chunk_session.py --session-id SID [--mode full|incremental]
      [--texts '["text1","text2"]']  # only for incremental
"""

import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from recall import load_config, EmbeddingClient, PgVectorStore

BOUNDARY_THRESHOLD = 0.5  # cosine DISTANCE > this = new cluster


def _msg_text(msg: dict) -> str:
    content = msg.get("content", "")
    if isinstance(content, list):
        return " ".join(
            p.get("text", "") for p in content if p.get("type") == "text"
        )
    return str(content)


# ── Incremental mode ───────────────────────────────────────────────────────

def _annotate_incremental_cluster(cluster_texts: list[str]) -> tuple[str, str]:
    """Generate title + summary via DeepSeek for incremental chunk.
    Prompt in Russian so cluster titles match the chat language."""
    text_blob = " ".join(t[:200] for t in cluster_texts[:5])
    if not text_blob.strip():
        return "", ""
    prompt = (
        "Дай КРАТКИЙ заголовок (до 10 слов) и КРАТКОЕ описание (2-3 предложения) "
        "для этого фрагмента переписки.\n"
        "Пиши на том же языке, на котором написан фрагмент.\n"
        "Ответь строго в JSON.\n\n"
        "Фрагмент:\n" + text_blob
    )
    import requests
    DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
    DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
    if not DEEPSEEK_KEY:
        # Fallback: try reading from .env directly
        _env_path = os.path.join(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")), ".env")
        if os.path.exists(_env_path):
            with open(_env_path) as _f:
                for _line in _f:
                    if _line.startswith("DEEPSEEK_API_KEY="):
                        DEEPSEEK_KEY = _line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    try:
        resp = requests.post(
            DEEPSEEK_URL,
            json={
                "model": "deepseek-v4-flash",
                "messages": [
                    {"role": "system", "content": "Respond strictly in JSON."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.1,
                "max_tokens": 256,
            },
            headers={
                "Authorization": "Bearer {}".format(DEEPSEEK_KEY),
                "Content-Type": "application/json",
            },
            timeout=15,
        )
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"].strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]
            if raw.endswith("```"):
                raw = raw[:-3].strip()
            if raw.startswith("json"):
                raw = raw[4:].strip()
        result = json.loads(raw)
        return result.get("title", ""), result.get("summary", "")
    except Exception:
        return texts[0][:80] if texts else "", texts[0][:200] if texts else ""


def incremental_chunk(
    session_id: str,
    texts: list[str],
    store: PgVectorStore,
    embedder: EmbeddingClient,
    msg_indices: list[int] = None,
):
    """Add new texts to existing clusters via centroid matching."""
    if not texts:
        print("No texts to process")
        return

    # Batch embed
    embs_raw = embedder.batch_embed(texts)
    new_embs = [np.array(e, dtype=np.float32) for e in embs_raw]
    print("Incremental chunk: {} texts embedded".format(len(texts)))

    # Get existing clusters for this session
    existing = store.get_clusters_with_embeddings(session_id)

    if not existing:
        # Cold start: create first cluster
        avg_emb = np.mean(new_embs, axis=0).tolist()
        idx_start = msg_indices[0] if msg_indices else None
        idx_end = msg_indices[-1] if msg_indices else None
        _title, _summary = _annotate_incremental_cluster(texts)
        store.insert_cluster(
            session_id=session_id,
            title=_title or texts[0][:80],
            summary=_summary or texts[0][:200],
            embedding=avg_emb,
            msg_start=idx_start,
            msg_end=idx_end,
        )
        store.log_decision(session_id, texts[0], _title or texts[0][:80], 0.0, " new)
        print("  Cold start: created first cluster")
        return

    # For each new embedding: find best existing cluster
    for i, new_emb in enumerate(new_embs):
        best_cluster = None
        best_sim = -1.0

        for cl in existing:
            cl_emb = np.array(cl["embedding"], dtype=np.float32)
            dot = np.dot(new_emb, cl_emb)
            n1 = np.linalg.norm(new_emb)
            n2 = np.linalg.norm(cl_emb)
            if n1 > 0 and n2 > 0:
                sim = float(dot / (n1 * n2))
                if sim > best_sim:
                    best_sim = sim
                    best_cluster = cl

        if best_cluster is None:
            # Should not happen — existing was non-empty
            continue

        distance = 1.0 - best_sim

        if distance < BOUNDARY_THRESHOLD:
            # Merge: update centroid (rolling average)
            cl_id = best_cluster["id"]
            old_emb = np.array(best_cluster["embedding"], dtype=np.float32)
            # Simple rolling: 0.8 old + 0.2 new
            new_centroid = (old_emb * 0.8 + new_emb * 0.2).tolist()
            new_end = msg_indices[i] if msg_indices else None
            store.update_cluster_embedding(cl_id, new_centroid, msg_end=new_end)
            store.log_decision(session_id, texts[i], best_cluster["cluster_title"], float(best_sim), "merge")
            print("  Text {}: merged into cluster '{}' (dist={:.3f})".format(
                i, best_cluster["cluster_title"][:40], distance))
        else:
            # New cluster
            idx_i = msg_indices[i] if msg_indices else None
            _title_nc, _summary_nc = _annotate_incremental_cluster([texts[i]])
            store.insert_cluster(
                session_id=session_id,
                title=_title_nc or texts[i][:80],
                summary=_summary_nc or texts[i][:200],
                embedding=new_emb.tolist(),
                msg_start=idx_i,
                msg_end=idx_i,
            )
            store.log_decision(session_id, texts[i], _title_nc or texts[i][:80], 1.0 - distance, "new")
            print("  Text {}: new cluster (dist={:.3f} > {})".format(
                i, distance, BOUNDARY_THRESHOLD))

    print("Done: {} texts processed".format(len(texts)))


# ── Full mode (legacy, kept for reference) ─────────────────────────────────

def compute_boundaries(
    messages: list[dict],
    embedder: EmbeddingClient,
    threshold: float,
    min_cluster_size: int,
    max_cluster_size: int,
) -> list[tuple[int, int]]:
    if not messages:
        return []
    texts = [_msg_text(m) for m in messages]
    BATCH = 20
    all_embs = []
    for i in range(0, len(texts), BATCH):
        all_embs.extend(embedder.batch_embed(texts[i : i + BATCH]))
    embeddings = [np.array(e, dtype=np.float32) for e in all_embs]
    distances = []
    for i in range(len(embeddings) - 1):
        a, b = embeddings[i], embeddings[i + 1]
        d = np.dot(a, b)
        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        if na > 0 and nb > 0:
            distances.append(1.0 - float(d / (na * nb)))
        else:
            distances.append(0.0)
    boundaries = [0]
    for i, d in enumerate(distances):
        if d > threshold:
            boundaries.append(i + 1)
    boundaries.append(len(messages))
    clusters = []
    for i in range(len(boundaries) - 1):
        s, e = boundaries[i], boundaries[i + 1]
        if e - s < min_cluster_size and clusters:
            clusters[-1] = (clusters[-1][0], e)
            continue
        while e - s > max_cluster_size:
            cut = s + max_cluster_size
            clusters.append((s, min(cut, e)))
            s = min(cut, e)
        if s < e:
            clusters.append((s, e))
    return clusters


def full_chunk(session_id: str, store: PgVectorStore, embedder: EmbeddingClient):
    config = load_config()
    cfg = config.get("chunking", {})
    threshold = cfg.get("boundary_threshold", 0.5)
    min_sz = cfg.get("min_cluster_size", 3)
    max_sz = cfg.get("max_cluster_size", 50)
    recall_home = os.path.join(os.environ.get("HERMES_HOME", "/home/mia/.hermes"))
    sys.path.insert(0, recall_home)
    from hermes_state import SessionDB
    db = SessionDB()
    messages = db.get_messages(session_id)
    messages = [m for m in messages if m.get("role") in ("user", "assistant")]
    if not messages:
        print("No messages")
        store.close()
        return
    boundaries = compute_boundaries(messages, embedder, threshold, min_sz, max_sz)
    if store.has_session_clusters(session_id):
        store.clear_session_clusters(session_id)
    for start, end in boundaries:
        cl_msgs = messages[start:end]
        texts = [_msg_text(m) for m in cl_msgs]
        embs = []
        for i in range(0, len(texts), 20):
            embs.extend(embedder.batch_embed(texts[i : i + 20]))
        avg_emb = np.mean([np.array(e, dtype=np.float32) for e in embs], axis=0).tolist()
        store.insert_cluster(
            session_id=session_id,
            title=texts[0][:80],
            summary=texts[0][:200],
            embedding=avg_emb,
            msg_start=cl_msgs[0].get("id"),
            msg_end=cl_msgs[-1].get("id"),
        )
    print("Full chunk: {} clusters".format(len(boundaries)))


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--mode", choices=["full", "incremental"], default="incremental")
    parser.add_argument("--texts", default=None, help='JSON array: ["text1","text2",...]')
    parser.add_argument("--texts-stdin", action="store_true", help='Read texts JSON from stdin instead of --texts')
    parser.add_argument("--single", action="store_true", help='Single message mode (use --text and --msg-index)')
    parser.add_argument("--text", default=None, help='Single text (for --single mode)')
    parser.add_argument("--msg-index", type=int, default=0, help='Message index (for --single mode)')
    args = parser.parse_args()

    config = load_config()
    store = PgVectorStore(config["postgresql"])
    embedder = EmbeddingClient(config["ollama"]["url"], config["ollama"]["model"])

    if args.single:
        if not args.text:
            print("ERROR: --text required for --single mode")
            store.close()
            sys.exit(1)
        incremental_chunk(
            args.session_id,
            [args.text],
            store,
            embedder,
            msg_indices=[args.msg_index],
        )
    elif args.mode == "incremental":
        if args.texts_stdin:
            texts = json.loads(sys.stdin.read())
        elif args.texts:
            texts = json.loads(args.texts)
        else:
            print("ERROR: --texts or --texts-stdin required for incremental mode")
            store.close()
            sys.exit(1)
        incremental_chunk(args.session_id, texts, store, embedder)
    else:
        full_chunk(args.session_id, store, embedder)

    store.close()


if __name__ == "__main__":
    main()