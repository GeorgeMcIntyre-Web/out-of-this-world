/**
 * Interactive error charts using Recharts
 */

import {
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    Area,
    ComposedChart,
} from "recharts";
import { useMemo } from "react";
import type { ExperimentResult } from "../types/simulation";
import "./ErrorCharts.css";

interface ErrorChartsProps {
    experiments: ExperimentResult[];
}

function formatTime(seconds: number): string {
    if (seconds < 60) return `${seconds.toFixed(0)}s`;
    if (seconds < 3600) return `${(seconds / 60).toFixed(0)}m`;
    return `${(seconds / 3600).toFixed(1)}h`;
}

function formatError(meters: number): string {
    if (meters >= 1000) return `${(meters / 1000).toFixed(2)} km`;
    if (meters >= 1) return `${meters.toFixed(1)} m`;
    return `${(meters * 100).toFixed(1)} cm`;
}

export function ErrorCharts({ experiments }: ErrorChartsProps) {
    const chartData = useMemo(() => {
        if (experiments.length === 0) return [];

        // Use first experiment's time as reference
        const times = experiments[0].time_s;

        return times.map((t, i) => {
            const point: Record<string, number> = { time: t };
            experiments.forEach((exp) => {
                const suffix = exp.imu_profile === "quantum" ? "_q" : "_c";
                const scenarioSuffix = exp.name.includes("coast") ? "_coast" : "_upd";
                const key = `pos${suffix}${scenarioSuffix}`;
                point[key] = exp.pos_error_m[i] || 0;
                point[`sigma${suffix}`] = exp.pos_sigma_m[i] || 0;
            });
            return point;
        });
    }, [experiments]);

    if (experiments.length === 0) {
        return (
            <div className="error-charts empty">
                <div className="empty-state">
                    <span className="icon">📊</span>
                    <p>Run a simulation to see error charts</p>
                </div>
            </div>
        );
    }

    // Determine which lines to show
    const hasClassical = experiments.some((e) => e.imu_profile === "classical");
    const hasQuantum = experiments.some((e) => e.imu_profile === "quantum");
    const hasCoast = experiments.some((e) => e.name.includes("coast"));
    const hasUpdates = experiments.some((e) => e.name.includes("updates"));

    return (
        <div className="error-charts">
            <h3>Position Error vs Time</h3>
            <ResponsiveContainer width="100%" height={300}>
                <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <defs>
                        <linearGradient id="gradientClassical" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="gradientQuantum" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis
                        dataKey="time"
                        stroke="#64748b"
                        tickFormatter={formatTime}
                        tick={{ fill: "#94a3b8" }}
                    />
                    <YAxis
                        stroke="#64748b"
                        tickFormatter={(v) => formatError(v)}
                        tick={{ fill: "#94a3b8" }}
                        scale="log"
                        domain={["auto", "auto"]}
                    />
                    <Tooltip
                        contentStyle={{
                            background: "rgba(15, 23, 42, 0.95)",
                            border: "1px solid rgba(148, 163, 184, 0.2)",
                            borderRadius: "8px",
                        }}
                        labelFormatter={(v) => `Time: ${formatTime(v as number)}`}
                        formatter={(value) => {
                            if (typeof value !== "number") return ["—", ""];
                            return [formatError(value), ""];
                        }}
                    />
                    <Legend />

                    {hasClassical && hasCoast && (
                        <>
                            <Area
                                type="monotone"
                                dataKey="sigma_c"
                                fill="url(#gradientClassical)"
                                stroke="none"
                                name="3σ (Classical)"
                            />
                            <Line
                                type="monotone"
                                dataKey="pos_c_coast"
                                stroke="#3b82f6"
                                strokeWidth={2}
                                dot={false}
                                name="Classical (coast)"
                            />
                        </>
                    )}

                    {hasClassical && hasUpdates && (
                        <Line
                            type="monotone"
                            dataKey="pos_c_upd"
                            stroke="#60a5fa"
                            strokeWidth={2}
                            strokeDasharray="5 5"
                            dot={false}
                            name="Classical (updates)"
                        />
                    )}

                    {hasQuantum && hasCoast && (
                        <>
                            <Area
                                type="monotone"
                                dataKey="sigma_q"
                                fill="url(#gradientQuantum)"
                                stroke="none"
                                name="3σ (Quantum)"
                            />
                            <Line
                                type="monotone"
                                dataKey="pos_q_coast"
                                stroke="#22c55e"
                                strokeWidth={2}
                                dot={false}
                                name="Quantum (coast)"
                            />
                        </>
                    )}

                    {hasQuantum && hasUpdates && (
                        <Line
                            type="monotone"
                            dataKey="pos_q_upd"
                            stroke="#86efac"
                            strokeWidth={2}
                            strokeDasharray="5 5"
                            dot={false}
                            name="Quantum (updates)"
                        />
                    )}
                </ComposedChart>
            </ResponsiveContainer>
        </div>
    );
}
