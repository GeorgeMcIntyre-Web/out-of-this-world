"""Plotting functions for experiment results."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np

if TYPE_CHECKING:
    from outofthisworld.sim.experiments import ExperimentResults


def plot_error_vs_time(
    results: ExperimentResults,
    output_path: Path | None = None,
    show: bool = False,
) -> None:
    """
    Plot position and velocity error vs time with 3-sigma bounds.

    Args:
        results: Experiment results to plot
        output_path: Path to save figure (optional)
        show: Whether to display the plot
    """
    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    time_min = results.time / 60.0  # Convert to minutes

    # Position error
    pos_err_norm = np.linalg.norm(results.pos_error, axis=1)
    pos_3sig = 3.0 * np.linalg.norm(results.pos_sigma, axis=1)

    ax1 = axes[0]
    ax1.semilogy(time_min, pos_err_norm, "b-", label="Position Error", linewidth=1.5)
    ax1.semilogy(time_min, pos_3sig, "b--", label="3σ Bound", linewidth=1.0, alpha=0.7)
    ax1.set_ylabel("Position Error (m)")
    ax1.set_title(f"Navigation Error: {results.config.name}")
    ax1.legend(loc="upper left")
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(bottom=1e-3)

    # Velocity error
    vel_err_norm = np.linalg.norm(results.vel_error, axis=1)
    vel_3sig = 3.0 * np.linalg.norm(results.vel_sigma, axis=1)

    ax2 = axes[1]
    ax2.semilogy(time_min, vel_err_norm, "r-", label="Velocity Error", linewidth=1.5)
    ax2.semilogy(time_min, vel_3sig, "r--", label="3σ Bound", linewidth=1.0, alpha=0.7)
    ax2.set_ylabel("Velocity Error (m/s)")
    ax2.set_xlabel("Time (minutes)")
    ax2.legend(loc="upper left")
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(bottom=1e-6)

    plt.tight_layout()

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches="tight")

    if show:
        plt.show()

    plt.close(fig)


def plot_error_comparison(
    results_list: list[ExperimentResults],
    labels: list[str] | None = None,
    output_path: Path | None = None,
    show: bool = False,
) -> None:
    """
    Compare position error across multiple experiments.

    Args:
        results_list: List of experiment results
        labels: Labels for each result (uses config name if None)
        output_path: Path to save figure
        show: Whether to display plot
    """
    if labels is None:
        labels = [r.config.name for r in results_list]

    fig, ax = plt.subplots(figsize=(10, 6))

    colors = plt.cm.tab10(np.linspace(0, 1, len(results_list)))

    for results, label, color in zip(results_list, labels, colors):
        time_min = results.time / 60.0
        pos_err_norm = np.linalg.norm(results.pos_error, axis=1)
        ax.semilogy(time_min, pos_err_norm, label=label, color=color, linewidth=1.5)

    ax.set_xlabel("Time (minutes)")
    ax.set_ylabel("Position Error (m)")
    ax.set_title("Position Error Comparison: Classical vs Quantum IMU")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)
    ax.set_ylim(bottom=1e-3)

    plt.tight_layout()

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches="tight")

    if show:
        plt.show()

    plt.close(fig)


def plot_cadence_sweep(
    results_list: list[ExperimentResults],
    output_path: Path | None = None,
    show: bool = False,
) -> None:
    """
    Plot final error vs update cadence.

    Args:
        results_list: List of results from cadence sweep
        output_path: Path to save figure
        show: Whether to display plot
    """
    intervals = []
    final_pos_errors = []
    final_vel_errors = []

    for r in results_list:
        intervals.append(r.config.star_tracker_interval)
        final_pos_errors.append(r.get_final_pos_error_rms())
        final_vel_errors.append(r.get_final_vel_error_rms())

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    # Position error vs interval
    ax1 = axes[0]
    ax1.loglog(intervals, final_pos_errors, "bo-", markersize=8, linewidth=2)
    ax1.set_ylabel("Final Position Error (m)")
    ax1.set_title(f"Error vs Update Cadence ({results_list[0].config.imu_profile.name} IMU)")
    ax1.grid(True, alpha=0.3, which="both")

    # Velocity error vs interval
    ax2 = axes[1]
    ax2.loglog(intervals, final_vel_errors, "ro-", markersize=8, linewidth=2)
    ax2.set_ylabel("Final Velocity Error (m/s)")
    ax2.set_xlabel("Star Tracker Update Interval (s)")
    ax2.grid(True, alpha=0.3, which="both")

    plt.tight_layout()

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches="tight")

    if show:
        plt.show()

    plt.close(fig)
