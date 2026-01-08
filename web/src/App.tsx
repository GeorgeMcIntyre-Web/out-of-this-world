/**
 * Main App component - Quantum IMU Navigator Dashboard
 */

import { ConfigPanel } from "./components/ConfigPanel";
import { TrajectoryViewer } from "./components/TrajectoryViewer";
import { ErrorCharts } from "./components/ErrorCharts";
import { ResultsTable } from "./components/ResultsTable";
import { useSimulation } from "./hooks/useSimulation";
import type { RunRequest } from "./types/simulation";
import "./App.css";

function App() {
  const { status, results, error, runSimulation } = useSimulation();

  const handleRun = async (request: RunRequest) => {
    await runSimulation(request);
  };

  return (
    <div className="app">
      <header className="header">
        <h1>
          <span className="icon">🛰️</span>
          Quantum IMU Navigator
        </h1>
        <p className="subtitle">Deep-Space Navigation Simulation</p>
      </header>

      {error && (
        <div className="error-banner">
          ⚠️ {error}
          <p className="hint">Make sure the API server is running: <code>uvicorn api.main:app --reload</code></p>
        </div>
      )}

      <main className="dashboard">
        <aside className="sidebar">
          <ConfigPanel onRun={handleRun} status={status} />
          <ResultsTable
            experiments={results?.experiments || []}
            improvementFactor={results?.improvement_factor || null}
          />
        </aside>

        <div className="main-content">
          <section className="viewer-section">
            <TrajectoryViewer experiments={results?.experiments || []} />
          </section>

          <section className="charts-section">
            <ErrorCharts experiments={results?.experiments || []} />
          </section>
        </div>
      </main>

      <footer className="footer">
        <span>out-of-this-world</span>
        <span className="separator">•</span>
        <span>Research-grade navigation simulation</span>
      </footer>
    </div>
  );
}

export default App;
