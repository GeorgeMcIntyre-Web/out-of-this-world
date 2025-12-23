"""
Master script to generate all investor visualizations.
Run this once to produce all deliverables.
"""

from __future__ import annotations

import shutil
from pathlib import Path
import sys


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def setup_directories() -> dict[str, Path]:
    """Create output directories"""
    root = _repo_root()
    dirs = {
        "html": root / "demos" / "outputs" / "html",
        "videos": root / "demos" / "outputs" / "videos",
        "images": root / "demos" / "outputs" / "images",
        "slides": root / "demos" / "outputs" / "slides",
        "assets": root / "demos" / "assets",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    print("✅ Directories created")
    return dirs


def ensure_assets(assets_dir: Path) -> None:
    """Ensure minimal source assets exist (SVG)."""
    svg = assets_dir / "spacecraft_icon.svg"
    if not svg.exists():
        svg.write_text(
            """<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#22d3ee"/>
      <stop offset="1" stop-color="#3b82f6"/>
    </linearGradient>
  </defs>
  <rect width="256" height="256" fill="none"/>
  <path d="M128 18c22 18 40 44 40 78 0 16-4 34-12 50l36 18-14 28-36-18c-8 10-18 18-26 22-8-4-18-12-26-22l-36 18-14-28 36-18c-8-16-12-34-12-50 0-34 18-60 40-78z"
        fill="url(#g)" stroke="#e5e7eb" stroke-width="6" stroke-linejoin="round"/>
  <circle cx="128" cy="112" r="18" fill="#0b1220" stroke="#e5e7eb" stroke-width="6"/>
  <path d="M128 190c18 10 40 14 66 12" fill="none" stroke="#22d3ee" stroke-width="6" stroke-linecap="round"/>
  <path d="M128 190c-18 10-40 14-66 12" fill="none" stroke="#22d3ee" stroke-width="6" stroke-linecap="round"/>
</svg>
""",
            encoding="utf-8",
        )

    # Note: keep logo.png out of git (binary). Generate it as an output image instead.


def write_reveal_slides(slides_dir: Path) -> Path:
    """Write a Markdown-backed reveal.js slide deck (self-contained HTML + MD)."""
    md = slides_dir / "pitch.md"
    html = slides_dir / "index.html"

    md.write_text(
        """---
title: Cosmic Compass — Investor Demo
---

## Cosmic Compass
### GPS for Deep Space

OutOfThisWorld — autonomous navigation via gravitational sensing.

---

## The problem
- Deep space navigation is **blind**
- Star trackers drift, comms delays grow, GNSS is absent
- Autonomous guidance needs a **new absolute reference**

---

## The insight
Compact objects imprint measurable **gravity signatures**

- Neutron stars / black holes create distinct fields
- A spacecraft can infer position by matching the observed signature

---

## The sensor
**Atom interferometry** measures acceleration with extreme sensitivity

- Phase shift ∝ gravity
- Enables passive, jam-proof navigation

---

## What you’re seeing in the demo
- 3D flyby trajectory around a neutron star
- Uncertainty collapsing from **100 km → 100 m**
- Heatmap of log₁₀(|g|) over the flyby plane

---

## Why it matters
Autonomous navigation unlocks:
- Deep space exploration without constant ground support
- Resilient operations in contested environments
- Faster mission timelines and reduced ops cost

---

## Next
We’re building:
- Higher-fidelity physics + estimation
- Realistic sensor models + error budgets
- A shareable web demo for partners

---

## OutOfThisWorld
### Let’s bring GPS to deep space
""",
        encoding="utf-8",
    )

    html.write_text(
        """<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Cosmic Compass — Investor Demo</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.css" />
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/theme/black.css" />
    <style>
      .reveal { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; }
      .reveal .slides { text-align: left; }
      .reveal h1, .reveal h2, .reveal h3 { text-align: left; }
    </style>
  </head>
  <body>
    <div class="reveal">
      <div class="slides">
        <section data-markdown="pitch.md" data-separator="^---$" data-separator-vertical="^\\|\\|\\|$"></section>
      </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/reveal.js@5/plugin/markdown/markdown.js"></script>
    <script>
      Reveal.initialize({
        hash: true,
        plugins: [ RevealMarkdown ],
        transition: "fade"
      });
    </script>
  </body>
</html>
""",
        encoding="utf-8",
    )

    return html


def main() -> None:
    print("=" * 60)
    print("COSMIC COMPASS INVESTOR DEMO GENERATOR")
    print("=" * 60)

    # Ensure repo root is importable regardless of working directory.
    root = _repo_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    # Step 1: Setup
    print("\n[1/5] Setting up directories...")
    dirs = setup_directories()
    ensure_assets(dirs["assets"])

    # Step 2: Generate data
    print("\n[2/5] Generating simulation data...")
    from demos.investor_visuals.data_generation import save_demo_data

    demo_json = root / "demos" / "outputs" / "demo_data.json"
    save_demo_data(str(demo_json))

    # Copy demo JSON into the web demo public dir (for "npm run dev").
    web_public = root / "demos" / "investor_visuals" / "web_demo" / "public"
    web_public.mkdir(parents=True, exist_ok=True)
    shutil.copy2(demo_json, web_public / "demo_data.json")

    # Step 3: Create Plotly visualizations
    print("\n[3/5] Creating interactive Plotly visualizations...")
    from demos.investor_visuals.plotly_3d_demo import generate_all_plotly_visuals

    generate_all_plotly_visuals()

    # Step 4: Static charts
    print("\n[4/5] Creating static Matplotlib charts...")
    from demos.investor_visuals.static_charts import generate_static_charts

    charts = generate_static_charts()
    print(f"✅ Wrote {len(charts)} PNG charts to {dirs['images']}")

    # Step 5: Slides + (optional) Manim
    print("\n[5/5] Writing reveal.js pitch deck...")
    slide_index = write_reveal_slides(dirs["slides"])
    print(f"✅ Slides written to {slide_index}")

    print("\nOptional: rendering Manim animation (skips if unavailable)...")
    try:
        from demos.investor_visuals.manim_animations import render_animation

        render_animation()
    except Exception as e:  # noqa: BLE001
        print(f"⚠️  Skipped Manim render: {e}")

    print("\n" + "=" * 60)
    print("✅ ALL DELIVERABLES (NON-WEB) GENERATED!")
    print("=" * 60)
    print("\nOutputs:")
    print(f"  📊 Interactive 3D plots: {dirs['html']}")
    print(f"  📈 Static charts: {dirs['images']}")
    print(f"  🖥️  Slides (open in browser): {dirs['slides'] / 'index.html'}")
    print(f"  🎬 Animation (if rendered): {dirs['videos']}")


if __name__ == "__main__":
    main()

