import type { Frame } from "../types/sim";

export type ScenarioSummary = {
  id: string;
  name: string;
  description: string;
  defaultConfig: string | null;
  tags: string[];
};

export async function pingHealth(): Promise<void> {
  const response = await fetch("/api/health");
  if (response.ok === false) throw new Error(`Health check failed: ${response.status}`);
}

export async function fetchScenarios(): Promise<ScenarioSummary[]> {
  const response = await fetch("/api/scenarios");
  if (response.ok === false) throw new Error(`Failed to fetch scenarios: ${response.status}`);
  const data = (await response.json()) as unknown;
  if (Array.isArray(data) === false) throw new Error("Unexpected scenarios payload");
  return data as ScenarioSummary[];
}

export async function runSimulation(params: {
  scenarioId: string;
  tEndSeconds?: number;
  dtSeconds?: number;
  configPath?: string;
}): Promise<Frame[]> {
  const response = await fetch("/api/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      scenario_id: params.scenarioId,
      config_path: params.configPath,
      t_end_s: params.tEndSeconds,
      dt_s: params.dtSeconds,
    }),
  });

  if (response.ok === false) throw new Error(`Sim run failed: ${response.status}`);
  const frames = (await response.json()) as unknown;
  if (Array.isArray(frames) === false) throw new Error("Unexpected frames payload");
  if (frames.length === 0) throw new Error("Simulation returned no frames");
  return frames as Frame[];
}

