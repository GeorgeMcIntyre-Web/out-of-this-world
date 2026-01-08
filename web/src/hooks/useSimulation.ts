/**
 * Hook for simulation API interactions
 */

import { useState, useCallback } from "react";
import type {
    RunRequest,
    RunResponse,
    SimulationStatus,
} from "../types/simulation";

const API_BASE = "http://localhost:8000/api";

export function useSimulation() {
    const [status, setStatus] = useState<SimulationStatus>("idle");
    const [results, setResults] = useState<RunResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    const runSimulation = useCallback(async (request: RunRequest) => {
        setStatus("running");
        setError(null);

        try {
            const response = await fetch(`${API_BASE}/run`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(request),
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || "Simulation failed");
            }

            const data: RunResponse = await response.json();
            setResults(data);
            setStatus("complete");
            return data;
        } catch (err) {
            const message = err instanceof Error ? err.message : "Unknown error";
            setError(message);
            setStatus("error");
            return null;
        }
    }, []);

    const reset = useCallback(() => {
        setStatus("idle");
        setResults(null);
        setError(null);
    }, []);

    return { status, results, error, runSimulation, reset };
}
