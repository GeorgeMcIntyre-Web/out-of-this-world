"""Command-line interface for navigation experiments."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="ootw",
        description="Out of This World: Quantum IMU Navigation Simulation",
    )
    parser.add_argument(
        "--scenario",
        choices=["coast", "updates", "sweep", "compare"],
        default="compare",
        help="Scenario to run (default: compare)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to YAML configuration file",
    )
    parser.add_argument(
        "--imu",
        choices=["classical", "quantum"],
        default="quantum",
        help="IMU profile (default: quantum)",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=1.0,
        help="Simulation duration in hours (default: 1.0)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed (default: 42)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results"),
        help="Output directory (default: results)",
    )
    parser.add_argument(
        "--show-plots",
        action="store_true",
        help="Display plots interactively",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save outputs to files",
    )

    args = parser.parse_args()

    # Import here to avoid slow startup for --help
    from outofthisworld.output.plots import (
        plot_cadence_sweep,
        plot_error_comparison,
        plot_error_vs_time,
    )
    from outofthisworld.output.reports import (
        generate_cadence_report,
        generate_markdown_report,
        save_results_csv,
        save_results_json,
    )
    from outofthisworld.sensors.imu_profiles import CLASSICAL_IMU, QUANTUM_IMU, get_profile
    from outofthisworld.sim.experiments import (
        _run_experiment,
        load_config_from_yaml,
        run_cadence_sweep,
        run_coast_scenario,
        run_updates_scenario,
    )

    duration_s = args.duration * 3600.0
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Out of This World - Quantum IMU Navigation Simulation")
    print("=" * 60)
    print()

    # Run scenario from config file
    if args.config is not None:
        print(f"Loading configuration from: {args.config}")
        config = load_config_from_yaml(args.config)
        results = _run_experiment(config)

        _print_results(results)
        _save_outputs(
            results,
            output_dir,
            args,
            plot_error_vs_time,
            save_results_json,
            save_results_csv,
            generate_markdown_report,
        )
        return 0

    # Run named scenario
    if args.scenario == "coast":
        return _run_coast(
            args,
            output_dir,
            duration_s,
            get_profile,
            run_coast_scenario,
            plot_error_vs_time,
            save_results_json,
            save_results_csv,
            generate_markdown_report,
        )

    if args.scenario == "updates":
        return _run_updates(
            args,
            output_dir,
            duration_s,
            get_profile,
            run_updates_scenario,
            plot_error_vs_time,
            save_results_json,
            save_results_csv,
            generate_markdown_report,
        )

    if args.scenario == "sweep":
        return _run_sweep(
            args,
            output_dir,
            duration_s,
            get_profile,
            run_cadence_sweep,
            plot_cadence_sweep,
            generate_cadence_report,
        )

    if args.scenario == "compare":
        return _run_compare(
            args,
            output_dir,
            duration_s,
            run_coast_scenario,
            run_updates_scenario,
            plot_error_comparison,
            generate_markdown_report,
            CLASSICAL_IMU,
            QUANTUM_IMU,
        )

    return 0


def _run_coast(
    args,
    output_dir,
    duration_s,
    get_profile,
    run_coast_scenario,
    plot_error_vs_time,
    save_results_json,
    save_results_csv,
    generate_markdown_report,
):
    """Run coast scenario."""
    imu_profile = get_profile(args.imu)
    print(f"Running COAST scenario with {imu_profile.name} IMU...")
    print(f"Duration: {args.duration:.1f} hours, Seed: {args.seed}")
    print()

    results = run_coast_scenario(
        imu_profile=imu_profile,
        duration_s=duration_s,
        seed=args.seed,
    )

    _print_results(results)
    _save_outputs(
        results,
        output_dir,
        args,
        plot_error_vs_time,
        save_results_json,
        save_results_csv,
        generate_markdown_report,
    )
    return 0


def _run_updates(
    args,
    output_dir,
    duration_s,
    get_profile,
    run_updates_scenario,
    plot_error_vs_time,
    save_results_json,
    save_results_csv,
    generate_markdown_report,
):
    """Run updates scenario."""
    imu_profile = get_profile(args.imu)
    print(f"Running UPDATES scenario with {imu_profile.name} IMU...")
    print(f"Duration: {args.duration:.1f} hours, Update interval: 60s, Seed: {args.seed}")
    print()

    results = run_updates_scenario(
        imu_profile=imu_profile,
        update_interval=60.0,
        duration_s=duration_s,
        seed=args.seed,
    )

    _print_results(results)
    _save_outputs(
        results,
        output_dir,
        args,
        plot_error_vs_time,
        save_results_json,
        save_results_csv,
        generate_markdown_report,
    )
    return 0


def _run_sweep(
    args,
    output_dir,
    duration_s,
    get_profile,
    run_cadence_sweep,
    plot_cadence_sweep,
    generate_cadence_report,
):
    """Run cadence sweep."""
    imu_profile = get_profile(args.imu)
    print(f"Running CADENCE SWEEP with {imu_profile.name} IMU...")
    print(f"Duration: {args.duration:.1f} hours, Seed: {args.seed}")
    print()

    intervals = [10.0, 30.0, 60.0, 120.0, 300.0, 600.0, 1800.0, 3600.0]
    results_list = run_cadence_sweep(
        imu_profile=imu_profile,
        intervals=intervals,
        duration_s=duration_s,
        seed=args.seed,
    )

    print("Cadence Sweep Results:")
    print("-" * 50)
    print(f"{'Interval (s)':<15} {'Pos Error (m)':<20} {'Vel Error (m/s)':<20}")
    print("-" * 50)

    for r in results_list:
        interval = r.config.star_tracker_interval
        pos_err = r.get_final_pos_error_rms()
        vel_err = r.get_final_vel_error_rms()
        print(f"{interval:<15.0f} {pos_err:<20.2f} {vel_err:<20.6f}")

    print()

    if not args.no_save:
        plot_path = output_dir / f"cadence_sweep_{imu_profile.name}.png"
        plot_cadence_sweep(results_list, output_path=plot_path, show=args.show_plots)
        print(f"Saved plot: {plot_path}")

        report_path = output_dir / f"cadence_sweep_{imu_profile.name}.md"
        generate_cadence_report(results_list, report_path)
        print(f"Saved report: {report_path}")

    return 0


def _run_compare(
    args,
    output_dir,
    duration_s,
    run_coast_scenario,
    run_updates_scenario,
    plot_error_comparison,
    generate_markdown_report,
    CLASSICAL_IMU,
    QUANTUM_IMU,
):
    """Run classical vs quantum comparison."""
    print("Running COMPARISON: Classical vs Quantum IMU")
    print(f"Duration: {args.duration:.1f} hours, Seed: {args.seed}")
    print()

    # Coast scenarios
    print("Running coast scenarios...")
    classical_coast = run_coast_scenario(CLASSICAL_IMU, duration_s, seed=args.seed)
    quantum_coast = run_coast_scenario(QUANTUM_IMU, duration_s, seed=args.seed)

    # Updates scenarios
    print("Running updates scenarios...")
    classical_updates = run_updates_scenario(CLASSICAL_IMU, 60.0, duration_s, seed=args.seed)
    quantum_updates = run_updates_scenario(QUANTUM_IMU, 60.0, duration_s, seed=args.seed)

    results_list = [classical_coast, quantum_coast, classical_updates, quantum_updates]

    print()
    print("Comparison Results:")
    print("-" * 70)
    print(f"{'Scenario':<30} {'Pos Error (m)':<20} {'Vel Error (m/s)':<20}")
    print("-" * 70)

    for r in results_list:
        pos_err = r.get_final_pos_error_rms()
        vel_err = r.get_final_vel_error_rms()
        name = r.config.name
        print(f"{name:<30} {pos_err:<20.2f} {vel_err:<20.6f}")

    print()

    # Compute improvement ratios
    coast_ratio = (
        classical_coast.get_final_pos_error_rms() / quantum_coast.get_final_pos_error_rms()
    )
    update_ratio = (
        classical_updates.get_final_pos_error_rms() / quantum_updates.get_final_pos_error_rms()
    )

    print(f"Quantum IMU improvement factor (coast): {coast_ratio:.1f}x")
    print(f"Quantum IMU improvement factor (updates): {update_ratio:.1f}x")
    print()

    if not args.no_save:
        # Save comparison plot
        plot_path = output_dir / "comparison.png"
        plot_error_comparison(
            [classical_coast, quantum_coast],
            labels=["Classical (coast)", "Quantum (coast)"],
            output_path=plot_path,
            show=args.show_plots,
        )
        print(f"Saved plot: {plot_path}")

        # Save comparison report
        report_path = output_dir / "comparison.md"
        generate_markdown_report(results_list, report_path, "Classical vs Quantum IMU Comparison")
        print(f"Saved report: {report_path}")

    return 0


def _print_results(results):
    """Print summary of single experiment results."""
    print("Results:")
    print("-" * 40)
    print(f"Experiment: {results.config.name}")
    print(f"IMU Profile: {results.config.imu_profile.name}")
    print(f"Duration: {results.config.duration_s / 3600:.1f} hours")
    print(f"Star Tracker Updates: {results.n_updates}")
    print()
    print(f"Final Position Error: {results.get_final_pos_error_rms():.2f} m")
    print(f"Final Velocity Error: {results.get_final_vel_error_rms():.6f} m/s")
    print(f"Maximum Position Error: {results.get_max_pos_error():.2f} m")
    print()


def _save_outputs(
    results,
    output_dir,
    args,
    plot_error_vs_time,
    save_results_json,
    save_results_csv,
    generate_markdown_report,
):
    """Save outputs for single experiment."""
    if args.no_save:
        return

    prefix = results.config.name

    plot_path = output_dir / f"{prefix}_error.png"
    plot_error_vs_time(results, output_path=plot_path, show=args.show_plots)
    print(f"Saved plot: {plot_path}")

    json_path = output_dir / f"{prefix}_results.json"
    save_results_json(results, json_path)
    print(f"Saved JSON: {json_path}")

    csv_path = output_dir / f"{prefix}_timeseries.csv"
    save_results_csv(results, csv_path)
    print(f"Saved CSV: {csv_path}")

    report_path = output_dir / f"{prefix}_report.md"
    generate_markdown_report(results, report_path)
    print(f"Saved report: {report_path}")


if __name__ == "__main__":
    sys.exit(main())
