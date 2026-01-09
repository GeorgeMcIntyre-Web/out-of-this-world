/**
 * Configuration panel for experiment settings
 */

import { useState } from "react";
import type { RunRequest, SimulationStatus } from "../types/simulation";
import "./ConfigPanel.css";

interface ConfigPanelProps {
    onRun: (request: RunRequest) => void;
    status: SimulationStatus;
}

export function ConfigPanel({ onRun, status }: ConfigPanelProps) {
    const [imuProfile, setImuProfile] = useState<"classical" | "quantum">("quantum");
    const [scenario, setScenario] = useState<"coast" | "updates" | "compare">("compare");
    const [durationHours, setDurationHours] = useState(1.0);
    const [updateInterval, setUpdateInterval] = useState(60);
    const [seed, setSeed] = useState(42);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onRun({
            imu_profile: imuProfile,
            scenario,
            duration_hours: durationHours,
            update_interval: updateInterval,
            seed,
        });
    };

    const isRunning = status === "running";

    return (
        <div className="config-panel">
            <h2>⚙️ Configuration</h2>
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="imu">IMU Profile</label>
                    <select
                        id="imu"
                        value={imuProfile}
                        onChange={(e) => setImuProfile(e.target.value as "classical" | "quantum")}
                        disabled={isRunning}
                    >
                        <option value="classical">Classical (FOG/RLG)</option>
                        <option value="quantum">Quantum (Atom Interferometry)</option>
                    </select>
                </div>

                <div className="form-group">
                    <label htmlFor="scenario">Scenario</label>
                    <select
                        id="scenario"
                        value={scenario}
                        onChange={(e) => setScenario(e.target.value as "coast" | "updates" | "compare")}
                        disabled={isRunning}
                    >
                        <option value="coast">Coast (No Updates)</option>
                        <option value="updates">With Star Tracker</option>
                        <option value="compare">Compare Classical vs Quantum</option>
                    </select>
                </div>

                <div className="form-group">
                    <label htmlFor="duration">Duration: {durationHours}h</label>
                    <input
                        type="range"
                        id="duration"
                        min="0.1"
                        max="4"
                        step="0.1"
                        value={durationHours}
                        onChange={(e) => setDurationHours(parseFloat(e.target.value))}
                        disabled={isRunning}
                    />
                </div>

                {(scenario === "updates" || scenario === "compare") && (
                    <div className="form-group">
                        <label htmlFor="interval">Update Interval: {updateInterval}s</label>
                        <input
                            type="range"
                            id="interval"
                            min="10"
                            max="600"
                            step="10"
                            value={updateInterval}
                            onChange={(e) => setUpdateInterval(parseInt(e.target.value))}
                            disabled={isRunning}
                        />
                    </div>
                )}

                <div className="form-group">
                    <label htmlFor="seed">Random Seed</label>
                    <input
                        type="number"
                        id="seed"
                        value={seed}
                        onChange={(e) => setSeed(parseInt(e.target.value) || 42)}
                        disabled={isRunning}
                    />
                </div>

                <button type="submit" className="run-button" disabled={isRunning}>
                    {isRunning ? "⏳ Running..." : "▶️ Run Simulation"}
                </button>
            </form>
        </div>
    );
}
