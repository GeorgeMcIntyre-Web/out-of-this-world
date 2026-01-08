import { describe, expect, it, vi } from "vitest";
import { fetchScenarios, pingHealth, runSimulation } from "./sim";

function mockFetchOnce(response: Partial<Response> & { json?: () => Promise<unknown> }) {
  const fetchMock = vi.fn(async () => response as Response);
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

describe("api/sim", () => {
  it("pingHealth succeeds on ok", async () => {
    mockFetchOnce({ ok: true, status: 200 });
    await pingHealth();
  });

  it("pingHealth throws on non-ok", async () => {
    mockFetchOnce({ ok: false, status: 500 });
    await expect(pingHealth()).rejects.toThrow("Health check failed");
  });

  it("fetchScenarios returns array payload", async () => {
    mockFetchOnce({
      ok: true,
      status: 200,
      json: async () => [{ id: "coast", name: "Coast", description: "", defaultConfig: null, tags: [] }],
    });

    const scenarios = await fetchScenarios();
    expect(Array.isArray(scenarios)).toBe(true);
    expect(scenarios[0]?.id).toBe("coast");
  });

  it("fetchScenarios throws on non-array payload", async () => {
    mockFetchOnce({
      ok: true,
      status: 200,
      json: async () => ({ hello: "world" }),
    });

    await expect(fetchScenarios()).rejects.toThrow("Unexpected scenarios payload");
  });

  it("runSimulation returns frames", async () => {
    mockFetchOnce({
      ok: true,
      status: 200,
      json: async () => [{ t_s: 0, bodies: [], craft: [], events: [] }],
    });

    const frames = await runSimulation({ scenarioId: "coast", tEndSeconds: 10, dtSeconds: 1 });
    expect(frames.length).toBe(1);
    expect(frames[0]?.t_s).toBe(0);
  });

  it("runSimulation throws on empty frames", async () => {
    mockFetchOnce({
      ok: true,
      status: 200,
      json: async () => [],
    });

    await expect(runSimulation({ scenarioId: "coast" })).rejects.toThrow("Simulation returned no frames");
  });
});

