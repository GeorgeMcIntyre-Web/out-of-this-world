"""
Create investor-grade interactive visualizations using Plotly.
Outputs self-contained HTML files that can be embedded in presentations.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_demo_data(path: str | None = None):
    """Load pre-generated demo data"""
    if path is None:
        path = str(_repo_root() / "demos" / "outputs" / "demo_data.json")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert lists back to numpy arrays
    for key in [
        "positions",
        "velocities",
        "true_accelerations",
        "measured_accelerations",
        "uncertainty",
    ]:
        data[key] = np.array(data[key], dtype=float)

    data["time"] = np.array(data["time"], dtype=float)
    data["neutron_star_position"] = np.array(data["neutron_star_position"], dtype=float)

    return data


def create_3d_trajectory_plot(
    data: dict, output_path: str | None = None
):
    """
    Create interactive 3D plot of spacecraft trajectory with gravity field.
    """
    if output_path is None:
        output_path = str(_repo_root() / "demos" / "outputs" / "html" / "trajectory_3d.html")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    positions = data["positions"]
    ns_pos = data["neutron_star_position"]
    uncertainty = data["uncertainty"]

    # Normalize time for color scale (0 to 1)
    time_normalized = (data["time"] - data["time"][0]) / (data["time"][-1] - data["time"][0])

    fig = go.Figure()

    # Neutron star
    fig.add_trace(
        go.Scatter3d(
            x=[ns_pos[0]],
            y=[ns_pos[1]],
            z=[ns_pos[2]],
            mode="markers",
            marker=dict(size=20, color="blue", symbol="diamond", line=dict(color="cyan", width=2)),
            name="Neutron Star",
            hovertemplate="Neutron Star<br>Mass: 1.4 M☉<extra></extra>",
        )
    )

    # Spacecraft trajectory (colored by time)
    fig.add_trace(
        go.Scatter3d(
            x=positions[:, 0],
            y=positions[:, 1],
            z=positions[:, 2],
            mode="lines",
            line=dict(
                color=time_normalized,
                colorscale="Viridis",
                width=4,
                colorbar=dict(
                    title="Mission<br>Time", tickvals=[0, 0.5, 1], ticktext=["Start", "Mid", "End"]
                ),
            ),
            name="Spacecraft Path",
            hovertemplate="Position: (%{x:.0f}, %{y:.0f}, %{z:.0f}) km<extra></extra>",
        )
    )

    # Add uncertainty spheres at key points
    sample_indices = np.linspace(0, len(positions) - 1, 10, dtype=int)
    for k, idx in enumerate(sample_indices):
        u, v = np.mgrid[0 : 2 * np.pi : 20j, 0 : np.pi : 10j]
        x_sphere = uncertainty[idx] * np.cos(u) * np.sin(v) + positions[idx, 0]
        y_sphere = uncertainty[idx] * np.sin(u) * np.sin(v) + positions[idx, 1]
        z_sphere = uncertainty[idx] * np.cos(v) + positions[idx, 2]

        fig.add_trace(
            go.Surface(
                x=x_sphere,
                y=y_sphere,
                z=z_sphere,
                opacity=0.12,
                colorscale=[[0, "red"], [1, "red"]],
                showscale=False,
                hoverinfo="skip",
                name="Uncertainty" if k == 0 else None,
                showlegend=(k == 0),
            )
        )

    # Layout
    fig.update_layout(
        title=dict(
            text="Cosmic Compass: Gravitational Signature Detection<br><sub>Spacecraft Flyby of Neutron Star</sub>",
            font=dict(size=24),
        ),
        scene=dict(
            xaxis=dict(title="X (km)", backgroundcolor="black", gridcolor="gray"),
            yaxis=dict(title="Y (km)", backgroundcolor="black", gridcolor="gray"),
            zaxis=dict(title="Z (km)", backgroundcolor="black", gridcolor="gray"),
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.2)),
            aspectmode="data",
        ),
        paper_bgcolor="black",
        plot_bgcolor="black",
        font=dict(color="white", family="Arial, sans-serif"),
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor="rgba(0,0,0,0.5)",
            bordercolor="cyan",
            borderwidth=1,
        ),
        width=1200,
        height=800,
    )

    fig.write_html(str(output_file), include_plotlyjs=True, full_html=True)
    print(f"3D trajectory plot saved to {output_file}")
    return fig


def create_gravity_heatmap(data: dict, output_path: str | None = None):
    """
    Create 2D heatmap of gravitational field with trajectory overlay.
    """
    if output_path is None:
        output_path = str(_repo_root() / "demos" / "outputs" / "html" / "gravity_field.html")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    gf = data["gravity_field"]
    X, Y = np.array(gf["X"], dtype=float), np.array(gf["Y"], dtype=float)
    magnitude = np.array(gf["magnitude"], dtype=float)

    positions = data["positions"]
    ns_pos = data["neutron_star_position"]

    fig = go.Figure()

    # Gravity field heatmap
    fig.add_trace(
        go.Heatmap(
            x=X[0, :],
            y=Y[:, 0],
            z=magnitude,
            colorscale="Hot",
            colorbar=dict(title="log₁₀(g)<br>m/s²", titleside="right"),
            hovertemplate="X: %{x:.0f} km<br>Y: %{y:.0f} km<br>Gravity: 10^%{z:.1f} m/s²<extra></extra>",
            name="Gravity Field",
        )
    )

    # Spacecraft trajectory
    fig.add_trace(
        go.Scatter(
            x=positions[:, 0],
            y=positions[:, 1],
            mode="lines+markers",
            line=dict(color="cyan", width=3),
            marker=dict(size=4, color="white"),
            name="Spacecraft Path",
            hovertemplate="Position: (%{x:.0f}, %{y:.0f}) km<extra></extra>",
        )
    )

    # Neutron star
    fig.add_trace(
        go.Scatter(
            x=[ns_pos[0]],
            y=[ns_pos[1]],
            mode="markers",
            marker=dict(size=20, color="blue", symbol="star", line=dict(color="white", width=2)),
            name="Neutron Star",
        )
    )

    # Layout
    fig.update_layout(
        title="Gravitational Field Strength and Trajectory",
        xaxis=dict(title="X Position (km)", gridcolor="gray"),
        yaxis=dict(title="Y Position (km)", scaleanchor="x", gridcolor="gray"),
        paper_bgcolor="black",
        plot_bgcolor="black",
        font=dict(color="white", size=14),
        width=1000,
        height=800,
    )

    fig.write_html(str(output_file), include_plotlyjs=True, full_html=True)
    print(f"Gravity heatmap saved to {output_file}")
    return fig


def create_performance_dashboard(data: dict, output_path: str | None = None):
    """
    Multi-panel dashboard showing sensor performance metrics.
    """
    if output_path is None:
        output_path = str(
            _repo_root() / "demos" / "outputs" / "html" / "performance_dashboard.html"
        )

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    time_hours = data["time"] / 3600
    uncertainty = data["uncertainty"]

    # Distance from neutron star
    ns_pos = data["neutron_star_position"]
    distance = np.linalg.norm(data["positions"] - ns_pos, axis=1)

    # Acceleration magnitude
    acc_measured = np.linalg.norm(data["measured_accelerations"], axis=1)
    acc_true = np.linalg.norm(data["true_accelerations"], axis=1)

    # Create subplots
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Navigation Uncertainty vs Time",
            "Distance from Neutron Star",
            "Detected Gravitational Acceleration",
            "Sensor Performance (Signal/Noise)",
        ),
        specs=[[{"type": "scatter"}, {"type": "scatter"}], [{"type": "scatter"}, {"type": "scatter"}]],
    )

    # Plot 1: Uncertainty reduction
    fig.add_trace(
        go.Scatter(
            x=time_hours,
            y=uncertainty,
            mode="lines",
            line=dict(color="red", width=3),
            name="Position Uncertainty",
            hovertemplate="Time: %{x:.1f} hr<br>Uncertainty: %{y:.2f} km<extra></extra>",
        ),
        row=1,
        col=1,
    )

    # Plot 2: Distance
    fig.add_trace(
        go.Scatter(
            x=time_hours,
            y=distance,
            mode="lines",
            line=dict(color="cyan", width=3),
            name="Distance",
            fill="tozeroy",
            fillcolor="rgba(0,255,255,0.1)",
            hovertemplate="Time: %{x:.1f} hr<br>Distance: %{y:.0f} km<extra></extra>",
        ),
        row=1,
        col=2,
    )

    # Plot 3: Acceleration
    fig.add_trace(
        go.Scatter(
            x=time_hours,
            y=acc_measured * 1e9,  # Convert to nm/s^2
            mode="lines",
            line=dict(color="yellow", width=2),
            name="Measured",
            hovertemplate="Acceleration: %{y:.3f} nm/s²<extra></extra>",
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=time_hours,
            y=acc_true * 1e9,
            mode="lines",
            line=dict(color="green", width=1, dash="dash"),
            name="True Signal",
            hovertemplate="True: %{y:.3f} nm/s²<extra></extra>",
        ),
        row=2,
        col=1,
    )

    # Plot 4: SNR
    noise_floor = 1e-12  # m/s^2
    snr = acc_true / noise_floor
    fig.add_trace(
        go.Scatter(
            x=time_hours,
            y=snr,
            mode="lines",
            line=dict(color="lime", width=3),
            name="SNR",
            hovertemplate="SNR: %{y:.1e}<extra></extra>",
        ),
        row=2,
        col=2,
    )

    # Update axes
    fig.update_xaxes(title_text="Mission Time (hours)", gridcolor="gray")
    fig.update_yaxes(title_text="Uncertainty (km)", type="log", gridcolor="gray", row=1, col=1)
    fig.update_yaxes(title_text="Distance (km)", gridcolor="gray", row=1, col=2)
    fig.update_yaxes(
        title_text="Acceleration (nm/s²)", type="log", gridcolor="gray", row=2, col=1
    )
    fig.update_yaxes(
        title_text="Signal-to-Noise Ratio", type="log", gridcolor="gray", row=2, col=2
    )

    # Layout
    fig.update_layout(
        title_text="Cosmic Compass Performance Dashboard",
        paper_bgcolor="black",
        plot_bgcolor="black",
        font=dict(color="white", size=12),
        showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0.5)", bordercolor="white", borderwidth=1),
        height=900,
        width=1400,
    )

    fig.write_html(str(output_file), include_plotlyjs=True, full_html=True)
    print(f"Performance dashboard saved to {output_file}")
    return fig


def generate_all_plotly_visuals():
    """Generate all Plotly visualizations"""
    print("Loading demo data...")
    data = load_demo_data()

    print("\nGenerating 3D trajectory plot...")
    create_3d_trajectory_plot(data)

    print("\nGenerating gravity field heatmap...")
    create_gravity_heatmap(data)

    print("\nGenerating performance dashboard...")
    create_performance_dashboard(data)

    print("\n✅ All Plotly visualizations generated successfully!")
    print(f"Find outputs in {_repo_root() / 'demos' / 'outputs' / 'html'}")


if __name__ == "__main__":
    generate_all_plotly_visuals()

