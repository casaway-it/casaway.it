#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["google-genai>=2.4.0", "openai>=2.0.0", "PyYAML>=6.0"]
# ///
"""Generate cover images for every Things-to-Do activity in Langhe.

Reads data/activities/langhe.yaml and writes one PNG per activity to
assets/images/activities/<id>.png. Skips activities whose image already
exists unless --force is given. Same image shared between EN and IT.

Two providers supported:
    --provider openrouter  (default) — needs OPENROUTER_API_KEY
        default model: google/gemini-2.5-flash-image (best text suppression)
    --provider google                — needs GEMINI_API_KEY
        default model: imagen-4.0-ultra-generate-001

Examples:
    scripts/imagen-activities.py                       # generate all missing
    scripts/imagen-activities.py --only id1,id2        # only these
    scripts/imagen-activities.py --force               # regenerate every one
    scripts/imagen-activities.py --provider google --model imagen-4.0-generate-001
"""

from __future__ import annotations

import argparse
import base64
import os
import sys
import time
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
DATA_FILES = [
    REPO / "data" / "activities" / "langhe.yaml",
    REPO / "data" / "activities" / "brianza.yaml",
]
OUT_DIR = REPO / "assets" / "images" / "activities"

STYLE = (
    "Soft oil painting in the style of an Italian plein-air landscape — "
    "visible brushstrokes, gentle tonal gradients, refined elegant composition. "
    "Muted earth-tone palette: dark olive green, terracotta, cream, soft peach, "
    "dusty dark teal. No people, no text, no letters."
)

SCENES: dict[str, str] = {
    "sentinels-of-langhe": (
        "the Langhe wine region in Piedmont. Rolling vineyard hills under a "
        "clear dusk sky filled with soft gradient colour, four medieval "
        "hilltop castles silhouetted on distant ridges, geometric vineyard "
        "rows curving across the foreground hills."
    ),
    "panoramic-viewpoints": (
        "a panoramic terrace looking out over a sea of vineyard hills at "
        "golden hour, layered ridges receding into haze, a low stone parapet "
        "in the foreground, gradient warm sky above."
    ),
    "dogliani-dolcetti": (
        "a quiet Langhe village seen from a vineyard above — tile rooftops, "
        "a slender church bell tower, and vineyard rows wrapping the hill "
        "below. Soft afternoon light, no people."
    ),
    "noble-residences": (
        "an ornate 19th-century Italian country villa with a small formal "
        "garden in front, set among vineyard hills under a warm afternoon "
        "sky. Cypress trees frame the composition."
    ),
    "romanesque-pilgrim-route": (
        "a small Romanesque stone country chapel with a single bell tower, "
        "perched on a wooded hillside, framed by tall trees, a winding "
        "pilgrim path leading up to it."
    ),
    "bench-northern-loop": (
        "an oversized red giant bench on top of a hill at dusk, looking out "
        "over Alta Langa hazelnut groves and distant villages, the bench "
        "filling the foreground at a low angle."
    ),
    "bench-western-loop": (
        "an oversized orange giant bench on a vineyard ridge, layered Barolo "
        "hills receding into the distance, warm afternoon light, the bench "
        "filling the foreground."
    ),
    "bossolasco-benches": (
        "a winding village street lined with blooming roses leading to an "
        "oversized giant bench overlooking the Alta Langa hills, low stone "
        "houses on either side."
    ),
    "primula-trail": (
        "a soft dirt forest path winding through young hazelnut and chestnut "
        "trees, dappled sunlight on the ground, gentle hills visible through "
        "the canopy in the distance."
    ),
    "roddino-easy": (
        "a gentle walking path between hazelnut grove rows on a rolling "
        "ridge, an open view of distant Langhe hills, late morning light, "
        "wildflowers along the path edges."
    ),
    "serravalle-forest": (
        "a forest trail descending into a small valley between two Alta "
        "Langa villages perched on opposite ridges, autumn leaves on the "
        "trees, a meandering path in the foreground."
    ),
    "via-crucis-bossolasco": (
        "a quiet stone path through pasture and woodland with small "
        "weathered devotional chapel stations along it, gentle hills, soft "
        "afternoon light."
    ),
    "virgin-of-hal": (
        "a hilltop country sanctuary with a single bell tower and a small "
        "rose window, reached by a winding path through woodland, a wide "
        "valley visible below, golden hour light."
    ),
    "sentiero-del-barolo": (
        "a brightly coloured contemporary art chapel with geometric patches "
        "of red, yellow, blue and green standing among Barolo vineyard rows, "
        "an oversized red giant bench in the middle distance on a higher "
        "vineyard hill."
    ),
    "sorgenti-del-belbo": (
        "a forest clearing with a small pond and stream sources, a wooden "
        "boardwalk loop weaving between mature trees, ferns and mosses on "
        "the forest floor, soft filtered green light."
    ),
    "alba-cento-torri": (
        "the medieval town of Alba seen from a nearby vineyard hill — a "
        "compact cluster of red-tiled rooftops dominated by tall stone "
        "towers and a cathedral spire, soft golden-hour light, Langhe hills "
        "rolling beyond."
    ),
    "castiglione-falletto-borgo": (
        "a small Langhe village wrapped around a squat round-tower castle on "
        "the top of a hill, vineyard rows climbing toward it, warm afternoon "
        "light."
    ),
    "serralunga-village": (
        "the iconic tall narrow medieval castle of Serralunga d'Alba on its "
        "vineyard ridge, the village's terracotta rooftops clustered around "
        "its base, warm late-afternoon light."
    ),
    "bossolasco-roses": (
        "a quiet village street in Bossolasco lined with blooming roses "
        "spilling onto the pavement, low stone houses on both sides, an Alta "
        "Langa hill visible at the end of the street."
    ),
    "sale-san-giovanni-lavender": (
        "a lavender field in bloom in the Piedmont hills. Rows of purple "
        "lavender filling the foreground and converging toward a small stone "
        "chapel on a gentle hilltop, two cypress trees flanking the field, "
        "late-afternoon golden light. Palette adds dusty lavender purple and "
        "soft sage green."
    ),
    "alba-truffle-fair": (
        "an autumn Alba street scene during the truffle fair — cobbled lane "
        "under medieval arcades with empty market stalls and overhead "
        "festoons of golden autumn leaves, warm late-afternoon light, no "
        "people."
    ),
    "autumn-foliage": (
        "Alta Langa hills in peak autumn — copper, gold and ochre hazelnut "
        "groves and chestnut woodland blanketing rolling ridges, a single "
        "narrow country road winding through, no vehicles, no people, soft "
        "diffused light."
    ),
    # ── Brianza activities ──────────────────────────────────────────────
    "naviglio-martesana-cycle": (
        "a flat tree-lined canal towpath in the Lombard plain — the Naviglio "
        "Martesana water mirror-still alongside, leafy trees overhanging the "
        "path, the canal extending into the distance, soft morning light."
    ),
    "parco-monza-cycle": (
        "a wide gravel cycling avenue inside a grand royal park — tall plane "
        "trees flanking the path, the cream facade of Villa Reale visible "
        "through the trees at the far end, dappled morning light."
    ),
    "crespi-trezzo-loop": (
        "the UNESCO worker village of Crespi d'Adda — orderly rows of late-"
        "19th-century brick workers' houses with red-tile roofs lining a "
        "quiet straight street, the Adda river visible beyond, soft "
        "afternoon light."
    ),
    "adda-greenway-walk": (
        "a quiet riverside walking path along the Adda river — calm green "
        "water on one side, woodland and tall reeds on the other, an iron "
        "footbridge crossing in the middle distance."
    ),
    "parco-monza-walk": (
        "a sweeping royal park lawn with mature oak and plane trees, a small "
        "lake reflecting the canopy, a stone path winding through, late "
        "afternoon golden light."
    ),
    "brianza-villas-drive": (
        "an 18th-century Lombard noble villa with formal Italian gardens — "
        "symmetrical box hedges, gravel walks, a central fountain, the "
        "cream-coloured villa facade behind."
    ),
    "romanesque-brianza-drive": (
        "a small Romanesque stone basilica with a slender bell tower set in "
        "flat farmland — surrounding cypress trees, soft afternoon light, a "
        "single country lane leading up to it."
    ),
    "monza-historic-center": (
        "the medieval centre of Monza — the iron-clad bell tower of the "
        "Duomo seen over red-tiled rooftops, narrow cobbled lanes, a stone "
        "bridge over the Lambro river in the foreground."
    ),
    "bergamo-citta-alta": (
        "the medieval upper town of Bergamo perched on a hill — terracotta "
        "rooftops, defensive Venetian walls, a slim cathedral bell tower, "
        "the Lombard plain stretching out below."
    ),
    "lecco-lakefront": (
        "the lakefront of Lecco on Lake Como — calm blue water reflecting "
        "steep mountains on the far shore, pastel-coloured townhouses lining "
        "the promenade, small fishing boats moored at quay."
    ),
    "milan-day-trip": (
        "the spires of the Duomo of Milan against a soft cream sky, the "
        "Galleria Vittorio Emanuele facade glimpsed in the foreground, the "
        "central piazza seen from a high angle."
    ),
    "como-lakefront": (
        "the town of Como at the foot of Lake Como — neoclassical waterfront "
        "buildings, a single steamer at the dock, steep wooded mountains "
        "rising on both sides, soft morning haze on the lake."
    ),
    "ville-aperte-festival": (
        "an open Lombard noble villa during a heritage festival — its grand "
        "front gate ajar, a gravel courtyard inside, late-spring trees in "
        "bloom, soft light through tall windows."
    ),
    "monza-f1-weekend": (
        "the iconic curved banked corner of an old motor-racing circuit — "
        "empty tarmac curving away into the tall trees of a park, no cars, "
        "soft morning light."
    ),
    "brianza-sagre-autumn": (
        "an autumn village fair in a small Lombard piazza — wooden trestle "
        "tables under string lights, copper pots of polenta on a wood "
        "stove, chestnuts roasting on a brazier, low ochre buildings, late "
        "afternoon."
    ),
    "vimercate-carnevale": (
        "a Lombard town piazza during carnival — drifting confetti and "
        "streamers in mid-air, brightly painted carnival floats in soft "
        "focus, low pastel buildings, daylight."
    ),
}


def load_activity_ids() -> list[str]:
    ids: list[str] = []
    for path in DATA_FILES:
        data = yaml.safe_load(path.read_text())
        for cat in data.get("categories", []):
            for activity in cat.get("activities", []):
                ids.append(activity["id"])
    return ids


def build_prompt(activity_id: str) -> str:
    scene = SCENES.get(activity_id)
    if scene is None:
        raise KeyError(f"No SCENES entry for activity '{activity_id}'")
    return f"An oil painting of {scene} {STYLE}"


def generate_google(prompt: str, model: str, out_path: Path) -> None:
    from google import genai

    client = genai.Client()
    response = client.models.generate_images(
        model=model,
        prompt=prompt,
        config={"number_of_images": 1, "aspect_ratio": "16:9"},
    )
    images = response.generated_images or []
    if not images:
        raise SystemExit(f"No image returned by {model} (prompt blocked?)")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    images[0].image.save(out_path)


def generate_openrouter(prompt: str, model: str, out_path: Path) -> None:
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url="https://openrouter.ai/api/v1",
    )
    # Gemini chat models output text+image; pure image models (Flux, Recraft, …) output image only.
    modalities = ["image", "text"] if "gemini" in model.lower() else ["image"]
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        modalities=modalities,
        extra_body={"image_config": {"aspect_ratio": "16:9"}},
    )
    message = response.choices[0].message
    images = getattr(message, "images", None) or []
    if not images:
        raise SystemExit(f"No image returned by {model}. Message: {message!r}")
    url = images[0]["image_url"]["url"]
    if not url.startswith("data:"):
        raise SystemExit(f"Unexpected image url shape: {url[:80]}…")
    b64 = url.split(",", 1)[1]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(base64.b64decode(b64))


PROVIDER_DEFAULTS = {
    "openrouter": ("google/gemini-2.5-flash-image", "OPENROUTER_API_KEY"),
    "google": ("imagen-4.0-ultra-generate-001", "GEMINI_API_KEY"),
}

PROVIDER_FNS = {
    "openrouter": generate_openrouter,
    "google": generate_google,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--provider",
        choices=list(PROVIDER_DEFAULTS),
        default="openrouter",
        help="Image-gen backend (default: openrouter)",
    )
    parser.add_argument("--model", help="Override the provider's default model")
    parser.add_argument(
        "--only",
        help="Comma-separated activity ids to (re)generate",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate even if the image already exists",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=1.0,
        help="Seconds to wait between API calls (default: 1.0)",
    )
    args = parser.parse_args()

    default_model, env_var = PROVIDER_DEFAULTS[args.provider]
    model = args.model or default_model

    if not os.environ.get(env_var):
        print(f"ERROR: {env_var} not set", file=sys.stderr)
        return 1

    all_ids = load_activity_ids()
    selected = (
        [s.strip() for s in args.only.split(",")] if args.only else all_ids
    )
    unknown = [i for i in selected if i not in all_ids]
    if unknown:
        print(f"ERROR: unknown activity ids: {unknown}", file=sys.stderr)
        return 1

    todo = [
        i for i in selected if args.force or not (OUT_DIR / f"{i}.png").exists()
    ]
    if not todo:
        print("Nothing to generate (all cached).")
        return 0

    generate_fn = PROVIDER_FNS[args.provider]
    print(f"Generating {len(todo)} image(s) with {args.provider}:{model}…")
    for i, activity_id in enumerate(todo, 1):
        out_path = OUT_DIR / f"{activity_id}.png"
        print(f"  [{i}/{len(todo)}] {activity_id} -> {out_path}")
        prompt = build_prompt(activity_id)
        generate_fn(prompt, model, out_path)
        if i < len(todo):
            time.sleep(args.sleep)

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
