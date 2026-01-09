import { useCallback, useEffect, useMemo, useState } from "react";
import "./App.css";
import { fetchScenarios, pingHealth, runSimulation } from "./api/sim";
import { useSimulationPlayback } from "./hooks/useSimulationPlayback";
import { SceneHost, type SceneUiState } from "./components/SceneHost";

type LoadStatus = "idle" | "loading" | "ready" | "error";

function App() {
  const [status, setStatus] = useState<LoadStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [scenarios, setScenarios] = useState<
    { id: string; name: string; description: string; defaultConfig: string | null; tags: string[] }[]
  >([]);
  const [scenarioId, setScenarioId] = useState<string>("coast");
  const [tEndSeconds, setTEndSeconds] = useState(600);
  const [dtSeconds, setDtSeconds] = useState(2);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [ui, setUi] = useState<SceneUiState>({
    showReferenceAxes: true,
    showEclipticGrid: true,
    showInertialPlane: false,
    showCameraHorizon: false,
    showOrbitalPlanes: false,
    showSpacetimeSurface: false,
    showClocks: true,
    showLightBending: false,
    relativityStrength: 0.7,
  });

  const playback = useSimulationPlayback();
  const frames = playback.state.frames;
  const frame = playback.currentFrame;

  const isBackendOffline = status === "error" && error !== null;

  const run = useCallback(async () => {
    setError(null);
    setStatus("loading");

    try {
      const next = await runSimulation({
        scenarioId,
        tEndSeconds,
        dtSeconds,
      });
      playback.loadFrames(next);
      setStatus("ready");
    } catch (e) {
      const message = e instanceof Error ? e.message : "Unknown error";
      setError(message);
      setStatus("error");
    }
  }, [dtSeconds, playback, scenarioId, tEndSeconds]);

  useEffect(() => {
    let isCancelled = false;

    async function boot() {
      setStatus("loading");
      setError(null);

      try {
        await pingHealth();
        const list = await fetchScenarios();
        if (isCancelled) return;
        setScenarios(list);

        const defaultScenario = list[0]?.id;
        if (defaultScenario !== undefined) setScenarioId(defaultScenario);
        setStatus("ready");
      } catch (e) {
        if (isCancelled) return;
        const message = e instanceof Error ? e.message : "Unknown error";
        setError(message);
        setStatus("error");
      }
    }

    void boot();
    return () => {
      isCancelled = true;
    };
  }, []);

  useEffect(() => {
    if (status !== "ready") return;
    if (frames.length !== 0) return;
    void run();
  }, [frames.length, run, status]);

  const selected = useMemo(() => {
    if (frame === null) return null;
    if (selectedId === null) return null;
    return frame.craft.find((c) => c.id === selectedId) ?? null;
  }, [frame, selectedId]);

  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === " ") {
        e.preventDefault();
        if (playback.state.isPlaying) playback.pause();
        if (playback.state.isPlaying === false) playback.play();
      }
      if (e.key === "ArrowLeft") playback.stepBackward();
      if (e.key === "ArrowRight") playback.stepForward();
      if (e.key.toLowerCase() === "f") {
        if (selectedId === null) return;
        setUi((s) => ({ ...s, focusSelected: true }));
      }
    }

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [playback, selectedId]);

  useEffect(() => {
    if (ui.focusSelected !== true) return;
    setUi((s) => ({ ...s, focusSelected: false }));
  }, [ui.focusSelected]);

  const quickStart = (
    <div className="quickstart">
      <strong>Quick start:</strong> Left panel changes scenario + duration. Drag to rotate, scroll
      to zoom. <kbd>Space</kbd> play/pause. <kbd>←</kbd>/<kbd>→</kbd> step. <kbd>F</kbd>{" "}
      focus selected.
    </div>
  );

  if (isBackendOffline) {
    return (
      <div className="offline">
        <h1>Backend not reachable</h1>
        <p>Start the API and refresh:</p>
        <pre>
          <code>uv run uvicorn api.main:app --reload</code>
        </pre>
        <p className="muted">{error}</p>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="header">
        <h1>OutOfThisWorld</h1>
        <p className="subtitle">3D navigation + relativity playground</p>
      </header>

      {quickStart}

      <main className="space-layout">
        <aside className="panel left">
          <h2>Scenario</h2>
          <label>
            Scenario
            <select
              value={scenarioId}
              onChange={(e) => setScenarioId(e.target.value)}
              disabled={status === "loading"}
            >
              {scenarios.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Duration (s)
            <input
              type="number"
              value={tEndSeconds}
              onChange={(e) => setTEndSeconds(Number(e.target.value))}
              min={1}
            />
          </label>
          <label>
            Δt (s)
            <input
              type="number"
              value={dtSeconds}
              onChange={(e) => setDtSeconds(Number(e.target.value))}
              min={0.1}
              step={0.1}
            />
          </label>
          <button onClick={run} disabled={status === "loading"}>
            Run simulation
          </button>

          <hr />

          <h2>View</h2>
          <label className="row">
            <input
              type="checkbox"
              checked={ui.showReferenceAxes}
              onChange={(e) => setUi((s) => ({ ...s, showReferenceAxes: e.target.checked }))}
            />
            Show reference axes
          </label>
          <label className="row">
            <input
              type="checkbox"
              checked={ui.showEclipticGrid}
              onChange={(e) => setUi((s) => ({ ...s, showEclipticGrid: e.target.checked }))}
            />
            Ecliptic grid
          </label>
          <label className="row">
            <input
              type="checkbox"
              checked={ui.showInertialPlane ?? false}
              onChange={(e) => setUi((s) => ({ ...s, showInertialPlane: e.target.checked }))}
            />
            Inertial plane
          </label>
          <label className="row">
            <input
              type="checkbox"
              checked={ui.showCameraHorizon ?? false}
              onChange={(e) => setUi((s) => ({ ...s, showCameraHorizon: e.target.checked }))}
            />
            Camera horizon
          </label>
          <label className="row">
            <input
              type="checkbox"
              checked={ui.showOrbitalPlanes}
              onChange={(e) => setUi((s) => ({ ...s, showOrbitalPlanes: e.target.checked }))}
            />
            Orbital plane overlay
          </label>
        </aside>

        <section className="viewport">
          <SceneHost
            frames={frames}
            currentIndex={playback.state.currentIndex}
            frame={frame}
            selectedId={selectedId}
            onSelect={setSelectedId}
            ui={ui}
          />
          <div className="timeline">
            <button onClick={playback.stepBackward} disabled={frames.length === 0}>
              ◀
            </button>
            <button
              onClick={playback.state.isPlaying ? playback.pause : playback.play}
              disabled={frames.length === 0}
            >
              {playback.state.isPlaying ? "Pause" : "Play"}
            </button>
            <button onClick={playback.stepForward} disabled={frames.length === 0}>
              ▶
            </button>
            <input
              type="range"
              min={0}
              max={Math.max(0, frames.length - 1)}
              value={playback.state.currentIndex}
              onChange={(e) => playback.seek(Number(e.target.value))}
              disabled={frames.length === 0}
            />
            <span className="time">
              t = {frame?.t_s.toFixed(1) ?? "—"} s ({playback.state.currentIndex + 1}/{frames.length})
            </span>
          </div>
        </section>

        <aside className="panel right">
          <h2>Inspector</h2>
          <div className="muted">
            {selected === null ? "Select an object in 3D." : selected.name}
          </div>

          {selected !== null && (
            <div className="kv">
              <div>
                <strong>Position</strong>
                <div className="mono">{selected.position_m.map((v) => v.toFixed(0)).join(", ")} m</div>
              </div>
              <div>
                <strong>Velocity</strong>
                <div className="mono">
                  {selected.velocity_mps.map((v) => v.toFixed(2)).join(", ")} m/s
                </div>
              </div>
              <div>
                <strong>Proper time</strong>
                <div className="mono">
                  {selected.proper_time_s === null || selected.proper_time_s === undefined
                    ? "—"
                    : `${selected.proper_time_s.toFixed(3)} s`}
                </div>
              </div>
              <div>
                <strong>Time dilation</strong>
                <div className="mono">
                  {selected.time_dilation_factor === null || selected.time_dilation_factor === undefined
                    ? "—"
                    : `${selected.time_dilation_factor.toFixed(9)} ×`}
                </div>
              </div>
            </div>
          )}

          <hr />

          <h2>Relativity</h2>
          <label className="row">
            <input
              type="checkbox"
              checked={ui.showSpacetimeSurface}
              onChange={(e) => setUi((s) => ({ ...s, showSpacetimeSurface: e.target.checked }))}
            />
            Spacetime surface
          </label>
          <label className="row">
            <input
              type="checkbox"
              checked={ui.showClocks}
              onChange={(e) => setUi((s) => ({ ...s, showClocks: e.target.checked }))}
            />
            Local clocks
          </label>
          <label className="row">
            <input
              type="checkbox"
              checked={ui.showLightBending}
              onChange={(e) => setUi((s) => ({ ...s, showLightBending: e.target.checked }))}
            />
            Light-bending rays
          </label>
          <label>
            Relativity strength
            <input
              type="range"
              min={0}
              max={1}
              step={0.01}
              value={ui.relativityStrength}
              onChange={(e) => setUi((s) => ({ ...s, relativityStrength: Number(e.target.value) }))}
            />
          </label>
        </aside>
      </main>

      {error !== null && <div className="toast">⚠ {error}</div>}
    </div>
  );
}

export default App;
