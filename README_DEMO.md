## Cosmic Compass Investor Demo System

This repo includes an **investor-facing visualization bundle** under `demos/investor_visuals/`.

### What it generates

- **Interactive Plotly HTML (shareable)**: `demos/outputs/html/`
- **Static technical charts (PNG)**: `demos/outputs/images/`
- **Pitch deck template (reveal.js)**: `demos/outputs/slides/index.html`
- **Optional 30s Manim video (MP4)**: `demos/outputs/videos/` (skips if Manim is unavailable)
- **Web demo (React + Three.js)**: `demos/investor_visuals/web_demo/`

### One-command generation (Python)

From repo root:

```bash
uv sync
uv run python demos/investor_visuals/generate_all.py
```

Then open:
- `demos/outputs/html/trajectory_3d.html`
- `demos/outputs/html/gravity_field.html`
- `demos/outputs/html/performance_dashboard.html`
- `demos/outputs/slides/index.html`
and (if rendered):
- `demos/outputs/videos/cosmic_compass_explainer.mp4`

### Web demo (React + Three.js)

The generator copies `demos/outputs/demo_data.json` into `demos/investor_visuals/web_demo/public/demo_data.json`.

```bash
cd demos/investor_visuals/web_demo
npm install
npm run dev
```

### Notes

- **Manim fallback**: if Manim fails or isn’t installed, the generator will skip video rendering and still produce the Plotly + static assets.
- **Asset limits**: Plotly HTML files are self-contained; if file size becomes a concern, regenerate with lighter sampling (see `data_generation.py` parameters).

