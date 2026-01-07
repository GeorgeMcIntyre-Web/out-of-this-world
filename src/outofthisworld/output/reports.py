"""Report generation and data export."""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from outofthisworld.sim.experiments import ExperimentResults


def save_results_json(
    results: ExperimentResults,
    output_path: Path,
) -> None:
    """
    Save experiment results to JSON file.

    Args:
        results: Experiment results
        output_path: Path to output JSON file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = results.to_dict()
    data["generated_at"] = datetime.now(UTC).isoformat()

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)


def save_results_csv(
    results: ExperimentResults,
    output_path: Path,
) -> None:
    """
    Save time-series results to CSV file.

    Args:
        results: Experiment results
        output_path: Path to output CSV file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pos_err_norm = np.linalg.norm(results.pos_error, axis=1)
    vel_err_norm = np.linalg.norm(results.vel_error, axis=1)
    pos_sig_norm = np.linalg.norm(results.pos_sigma, axis=1)
    vel_sig_norm = np.linalg.norm(results.vel_sigma, axis=1)

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "time_s",
                "pos_error_m",
                "vel_error_m_s",
                "pos_3sigma_m",
                "vel_3sigma_m_s",
            ]
        )

        for i in range(len(results.time)):
            writer.writerow(
                [
                    f"{results.time[i]:.2f}",
                    f"{pos_err_norm[i]:.6e}",
                    f"{vel_err_norm[i]:.6e}",
                    f"{3.0 * pos_sig_norm[i]:.6e}",
                    f"{3.0 * vel_sig_norm[i]:.6e}",
                ]
            )


def generate_markdown_report(
    results: ExperimentResults | list[ExperimentResults],
    output_path: Path,
    title: str = "Navigation Experiment Results",
) -> None:
    """
    Generate markdown summary report.

    Args:
        results: Single result or list of results
        output_path: Path to output markdown file
        title: Report title
    """
    if isinstance(results, list):
        results_list = results
    else:
        results_list = [results]

    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# {title}",
        "",
        f"Generated: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        "## Summary",
        "",
        "| Experiment | IMU Profile | Duration | Final Pos Error | Final Vel Error | Updates |",
        "|------------|-------------|----------|-----------------|-----------------|---------|",
    ]

    for r in results_list:
        duration_h = r.config.duration_s / 3600.0
        pos_err = r.get_final_pos_error_rms()
        vel_err = r.get_final_vel_error_rms()

        # Format position error
        if pos_err > 1000:
            pos_str = f"{pos_err / 1000:.2f} km"
        else:
            pos_str = f"{pos_err:.2f} m"

        # Format velocity error
        if vel_err > 1:
            vel_str = f"{vel_err:.3f} m/s"
        else:
            vel_str = f"{vel_err * 1000:.3f} mm/s"

        lines.append(
            f"| {r.config.name} | {r.config.imu_profile.name} | "
            f"{duration_h:.1f} h | {pos_str} | {vel_str} | {r.n_updates} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
        ]
    )

    # Add interpretation based on results
    if len(results_list) >= 2:
        r1, r2 = results_list[0], results_list[1]
        ratio = r1.get_final_pos_error_rms() / max(r2.get_final_pos_error_rms(), 1e-10)

        if "classical" in r1.config.imu_profile.name and "quantum" in r2.config.imu_profile.name:
            lines.extend(
                [
                    f"The quantum-class IMU reduces final position error by a factor of **{ratio:.1f}x** "
                    "compared to the classical IMU under identical conditions.",
                    "",
                ]
            )

    # Coast scenario interpretation
    coast_results = [r for r in results_list if r.n_updates == 0]
    if coast_results:
        lines.extend(
            [
                "### Coast (Inertial-Only) Behavior",
                "",
                "Without external updates, position error grows approximately quadratically "
                "due to integrated accelerometer bias. The quantum-class IMU's lower bias "
                "instability results in significantly slower error growth.",
                "",
            ]
        )

    # Updates scenario interpretation
    update_results = [r for r in results_list if r.n_updates > 0]
    if update_results:
        lines.extend(
            [
                "### With Star Tracker Updates",
                "",
                "Periodic attitude updates from the star tracker bound navigation error. "
                "The steady-state error is limited by the star tracker accuracy and the "
                "rate at which IMU errors accumulate between updates.",
                "",
            ]
        )

    lines.extend(
        [
            "## Limitations",
            "",
            "1. Simplified dynamics: constant velocity, no gravity",
            "2. Star tracker provides attitude only (no position)",
            "3. IMU biases initialized to zero (optimistic)",
            "4. No time-correlated noise modeling",
            "5. Hypothetical quantum IMU parameters",
            "",
        ]
    )

    with open(output_path, "w") as f:
        f.write("\n".join(lines))


def generate_cadence_report(
    results_list: list[ExperimentResults],
    output_path: Path,
) -> None:
    """
    Generate markdown report for cadence sweep.

    Args:
        results_list: Results from cadence sweep
        output_path: Path to output file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    imu_name = results_list[0].config.imu_profile.name if results_list else "unknown"

    lines = [
        "# Update Cadence Sensitivity Analysis",
        "",
        f"Generated: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        f"IMU Profile: **{imu_name}**",
        "",
        "## Results",
        "",
        "| Update Interval (s) | Final Pos Error (m) | Final Vel Error (m/s) |",
        "|---------------------|---------------------|----------------------|",
    ]

    for r in results_list:
        interval = r.config.star_tracker_interval
        pos_err = r.get_final_pos_error_rms()
        vel_err = r.get_final_vel_error_rms()

        lines.append(f"| {interval:.0f} | {pos_err:.2f} | {vel_err:.6f} |")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "As update interval increases, navigation error grows. The error-interval "
            "relationship is approximately linear for short intervals (where IMU error "
            "growth is dominated by bias), transitioning to quadratic growth for long "
            "intervals (where the filter essentially operates in coast mode).",
            "",
        ]
    )

    with open(output_path, "w") as f:
        f.write("\n".join(lines))
