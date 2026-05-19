#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["google-genai>=2.4.0"]
# ///
"""Generate images via Google Imagen.

Examples:
    ./scripts/imagen.py --list-models
    ./scripts/imagen.py --prompt "stylized Italian hill village at sunset" \
        --out /tmp/test.png

Requires GEMINI_API_KEY in env.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from google import genai


def list_models(client: genai.Client) -> None:
    for m in client.models.list():
        name = m.name or ""
        if "imagen" in name.lower():
            print(name)


def generate(
    client: genai.Client,
    prompt: str,
    out: Path,
    model: str,
    aspect: str,
    n: int,
    negative_prompt: str | None = None,
    enhance_prompt: bool | None = None,
) -> list[Path]:
    config: dict[str, object] = {
        "number_of_images": n,
        "aspect_ratio": aspect,
    }
    if negative_prompt:
        config["negative_prompt"] = negative_prompt
    if enhance_prompt is not None:
        config["enhance_prompt"] = enhance_prompt
    response = client.models.generate_images(
        model=model,
        prompt=prompt,
        config=config,
    )
    images = response.generated_images or []
    if not images:
        raise SystemExit("No images returned (prompt may have been blocked).")

    out.parent.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    if n == 1:
        images[0].image.save(out)
        written.append(out)
    else:
        stem, ext = out.with_suffix(""), out.suffix or ".png"
        for i, img in enumerate(images, 1):
            path = stem.parent / f"{stem.name}-{i}{ext}"
            img.image.save(path)
            written.append(path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate images via Google Imagen.")
    parser.add_argument("--prompt", help="Image prompt")
    parser.add_argument("--out", type=Path, default=Path("out.png"), help="Output path")
    parser.add_argument("--model", default="imagen-4.0-generate-001", help="Model name")
    parser.add_argument(
        "--aspect",
        default="1:1",
        choices=["1:1", "16:9", "9:16", "4:3", "3:4"],
    )
    parser.add_argument("-n", "--count", type=int, default=1, help="Images per call")
    parser.add_argument(
        "--negative-prompt",
        help="Things to discourage (Vertex/Enterprise API only — Developer API rejects)",
    )
    parser.add_argument(
        "--no-enhance-prompt",
        action="store_true",
        help="Disable Imagen prompt rewriting (Vertex/Enterprise API only)",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List Imagen models and exit",
    )
    args = parser.parse_args()

    if not os.environ.get("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY not set", file=sys.stderr)
        return 1

    client = genai.Client()

    if args.list_models:
        list_models(client)
        return 0

    if not args.prompt:
        parser.error("--prompt required (or use --list-models)")

    for path in generate(
        client,
        args.prompt,
        args.out,
        args.model,
        args.aspect,
        args.count,
        negative_prompt=args.negative_prompt,
        enhance_prompt=False if args.no_enhance_prompt else None,
    ):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
