"""
Static technical diagrams (Matplotlib) for investor decks.
Produces high-resolution PNGs suitable for slides.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_demo_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    # numpy-ify
    for key in [
        "time",
        "positions",
        "true_accelerations",
        "measured_accelerations",
        "uncertainty",
        "neutron_star_position",
    ]:
        data[key] = np.array(data[key], dtype=float)
    gf = data["gravity_field"]
    data["gravity_field"] = {
        "X": np.array(gf["X"], dtype=float),
        "Y": np.array(gf["Y"], dtype=float),
        "magnitude": np.array(gf["magnitude"], dtype=float),
    }
    return data


def _style_dark():
    plt.style.use("dark_background")
    plt.rcParams.update(
        {
            "figure.facecolor": "#0b0b0f",
            "axes.facecolor": "#0b0b0f",
            "axes.edgecolor": "#9aa0a6",
            "axes.labelcolor": "white",
            "text.color": "white",
            "xtick.color": "#c7c7c7",
            "ytick.color": "#c7c7c7",
            "grid.color": "#333333",
            "font.size": 12,
        }
    )


def generate_static_charts(
    demo_data_path: str | None = None, output_dir: str | None = None
) -> dict[str, Path]:
    """
    Generate static PNG charts.

    Returns:
        Dict of artifact name -> output path.
    """
    root = _repo_root()
    if demo_data_path is None:
        demo_data_path = str(root / "demos" / "outputs" / "demo_data.json")
    if output_dir is None:
        output_dir = str(root / "demos" / "outputs" / "images")

    demo_path = Path(demo_data_path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    data = _load_demo_json(demo_path)
    _style_dark()

    t_hr = data["time"] / 3600
    ns_pos = data["neutron_star_position"]
    distance_km = np.linalg.norm(data["positions"] - ns_pos, axis=1)
    acc_true = np.linalg.norm(data["true_accelerations"], axis=1)
    noise_floor = 1e-12
    snr = acc_true / noise_floor

    artifacts: dict[str, Path] = {}

    # 1) Uncertainty vs time
    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
    ax.plot(t_hr, data["uncertainty"], color="#ff4d4d", lw=2.5)
    ax.set_yscale("log")
    ax.set_xlabel("Mission time (hours)")
    ax.set_ylabel("Position uncertainty (km)")
    ax.set_title("Navigation uncertainty collapses as gravity signature accumulates")
    ax.grid(True, which="both", alpha=0.35)
    p = out_dir / "uncertainty_vs_time.png"
    fig.tight_layout()
    fig.savefig(p, bbox_inches="tight")
    plt.close(fig)
    artifacts["uncertainty_vs_time"] = p

    # 2) SNR vs distance
    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
    ax.plot(distance_km, snr, color="#7CFF6B", lw=2.5)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Distance to neutron star (km)")
    ax.set_ylabel("Signal-to-noise ratio (unitless)")
    ax.set_title("Quantum sensor SNR across flyby geometry")
    ax.grid(True, which="both", alpha=0.35)
    p = out_dir / "snr_vs_distance.png"
    fig.tight_layout()
    fig.savefig(p, bbox_inches="tight")
    plt.close(fig)
    artifacts["snr_vs_distance"] = p

    # 3) Gravity field heatmap (static)
    gf = data["gravity_field"]
    fig, ax = plt.subplots(figsize=(10, 8), dpi=200)
    im = ax.imshow(
        gf["magnitude"],
        origin="lower",
        extent=[gf["X"][0, 0], gf["X"][0, -1], gf["Y"][0, 0], gf["Y"][-1, 0]],
        cmap="inferno",
        aspect="equal",
    )
    ax.plot(data["positions"][:, 0], data["positions"][:, 1], color="#00e5ff", lw=2)
    ax.scatter([ns_pos[0]], [ns_pos[1]], s=160, c="#3b82f6", edgecolors="white", zorder=5)
    ax.set_xlabel("X (km)")
    ax.set_ylabel("Y (km)")
    ax.set_title("Gravitational field map (log₁₀|g|) with trajectory overlay")
    cbar = fig.colorbar(im, ax=ax, shrink=0.85)
    cbar.set_label("log₁₀(|g|)  (m/s²)")
    p = out_dir / "gravity_field_static.png"
    fig.tight_layout()
    fig.savefig(p, bbox_inches="tight")
    plt.close(fig)
    artifacts["gravity_field_static"] = p

    return artifacts


if __name__ == "__main__":
    paths = generate_static_charts()
    print("✅ Static charts written:")
    for k, v in paths.items():
        print(f"  - {k}: {v}")

