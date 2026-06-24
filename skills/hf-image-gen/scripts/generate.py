#!/usr/bin/env python3
"""Generate images via Hugging Face FLUX.1 serverless API.

Usage:
    python3 generate.py "prompt" [--model MODEL] [--output PATH]
    
Default model: black-forest-labs/FLUX.1-schnell
Requires: HF_TOKEN in ~/Mia/.env
"""

import argparse
import subprocess
import sys
import time
import requests


def get_token():
    """Read HF_TOKEN from ~/Mia/.env."""
    import os
    home = os.environ.get("HERMES_HOME", os.path.expanduser("~/Mia"))
    env_path = os.path.join(home, ".env")
    
    r = subprocess.run(
        f"awk -F= '/^HF_TOKEN/{{print $2}}' {env_path}",
        shell=True, capture_output=True, text=True
    )
    token = r.stdout.strip()
    
    if not token or len(token) < 20:
        print("ERROR: HF_TOKEN not found or too short in .env", file=sys.stderr)
        sys.exit(1)
    
    return token


def generate(prompt, model="black-forest-labs/FLUX.1-schnell", output=None, max_retries=2):
    """Generate image via HF Inference API (router)."""
    token = get_token()
    url = f"https://router.huggingface.co/hf-inference/models/{model}"
    
    for attempt in range(max_retries + 1):
        print(f"[{attempt+1}/{max_retries+1}] Generating with {model}...", file=sys.stderr)
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {token}"},
            json={"inputs": prompt},
            timeout=120
        )
        
        if resp.status_code == 200:
            if output is None:
                import os, tempfile
                fd, output = tempfile.mkstemp(suffix=".png", prefix="hf_")
                os.close(fd)
            
            with open(output, "wb") as f:
                f.write(resp.content)
            
            print(f"OK: {len(resp.content)} bytes → {output}", file=sys.stderr)
            print(output)  # stdout for piping
            return output
        
        elif resp.status_code == 503:
            print(f"  Model loading (503), waiting 30s...", file=sys.stderr)
            time.sleep(30)
            continue
        
        elif resp.status_code == 401:
            print(f"ERROR 401: Invalid token. Check HF_TOKEN in .env", file=sys.stderr)
            sys.exit(1)
        
        elif resp.status_code == 429:
            print(f"  Rate limited (429), waiting 10s...", file=sys.stderr)
            time.sleep(10)
            continue
        
        elif resp.status_code == 410:
            print(f"ERROR 410: Model {model} deprecated. Try FLUX.1-schnell or FLUX.1-dev", file=sys.stderr)
            sys.exit(1)
        
        else:
            print(f"ERROR {resp.status_code}: {resp.text[:300]}", file=sys.stderr)
            sys.exit(1)
    
    print(f"ERROR: Failed after {max_retries+1} attempts", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate images via Hugging Face FLUX")
    parser.add_argument("prompt", help="Image generation prompt")
    parser.add_argument("--model", "-m", default="black-forest-labs/FLUX.1-schnell",
                        help="Model ID (default: FLUX.1-schnell)")
    parser.add_argument("--output", "-o", help="Output file path (default: temp file)")
    args = parser.parse_args()
    
    generate(args.prompt, args.model, args.output)
