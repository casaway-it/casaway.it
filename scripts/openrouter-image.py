#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["openai>=2.0.0"]
# ///
"""Generate images via OpenRouter (chat-completions multimodal output).

Examples:
    ./scripts/openrouter-image.py --prompt "..." --out /tmp/test.png
    ./scripts/openrouter-image.py --model black-forest-labs/flux.2-pro \\
        --prompt "..." --out /tmp/flux.png

Default model: google/gemini-2.5-flash-image (Nano Banana — strong instruction
following and good "no text" compliance).

Requires OPENROUTER_API_KEY in env.
"""

from __future__ import annotations

import argparse
import base64
import os
import sys
from pathlib import Path

from openai import OpenAI

BASE_URL = "https://openrouter.ai/api/v1"


def generate(
    client: OpenAI,
    prompt: str,
    out: Path,
    model: str,
    aspect: str,
) -> Path:
    modalities = ["image", "text"] if "gemini" in model.lower() else ["image"]
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        modalities=modalities,
        extra_body={"image_config": {"aspect_ratio": aspect}},
    )
    message = response.choices[0].message
    images = getattr(message, "images", None) or []
    if not images:
        raise SystemExit(
            f"No image returned by {model}. Full message: {message!r}"
        )
    url = images[0]["image_url"]["url"]
    if not url.startswith("data:"):
        raise SystemExit(f"Unexpected image url shape: {url[:80]}…")
    b64 = url.split(",", 1)[1]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(base64.b64decode(b64))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate images via OpenRouter.")
    parser.add_argument("--prompt", required=True, help="Image prompt")
    parser.add_argument("--out", type=Path, default=Path("out.png"), help="Output path")
    parser.add_argument(
        "--model",
        default="google/gemini-2.5-flash-image",
        help="OpenRouter model id",
    )
    parser.add_argument(
        "--aspect",
        default="16:9",
        choices=["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3"],
    )
    args = parser.parse_args()

    if not os.environ.get("OPENROUTER_API_KEY"):
        print("ERROR: OPENROUTER_API_KEY not set", file=sys.stderr)
        return 1

    client = OpenAI(api_key=os.environ["OPENROUTER_API_KEY"], base_url=BASE_URL)
    path = generate(client, args.prompt, args.out, args.model, args.aspect)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
