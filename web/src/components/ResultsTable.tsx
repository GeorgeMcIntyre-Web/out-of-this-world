/**
 * Results summary table
 */

import type { ExperimentResult } from "../types/simulation";
import "./ResultsTable.css";

interface ResultsTableProps {
    experiments: ExperimentResult[];
    improvementFactor: number | null;
}

function formatError(meters: number): string {
    if (meters >= 1000) return `${(meters / 1000).toFixed(2)} km`;
    if (meters >= 1) return `${meters.toFixed(1)} m`;
    return `${(meters * 100).toFixed(1)} cm`;
}

export function ResultsTable({ experiments, improvementFactor }: ResultsTableProps) {
    if (experiments.length === 0) {
        return (
            <div className="results-table empty">
                <h2>📋 Results</h2>
                <p className="no-data">No results yet</p>
            </div>
        );
    }

    return (
        <div className="results-table">
            <h2>📋 Results</h2>

            <div className="results-grid">
                {experiments.map((exp) => (
                    <div
                        key={exp.name}
                        className={`result-card ${exp.imu_profile}`}
                    >
                        <div className="result-header">
                            <span className="profile-badge">{exp.imu_profile}</span>
                            <span className="scenario">{exp.name.includes("coast") ? "Coast" : "Updates"}</span>
                        </div>
                        <div className="result-value">
                            {formatError(exp.final_pos_error_m)}
                        </div>
                        <div className="result-label">Position Error</div>
                        {exp.n_updates > 0 && (
                            <div className="result-updates">
                                {exp.n_updates} updates
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {improvementFactor !== null && (
                <div className="improvement-banner">
                    <span className="improvement-icon">⚛️</span>
                    <span className="improvement-text">
                        Quantum IMU: <strong>{improvementFactor.toFixed(1)}×</strong> improvement
                    </span>
                </div>
            )}
        </div>
    );
}
