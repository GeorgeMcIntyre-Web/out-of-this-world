import React, { useEffect, useMemo, useState } from "react";
import SpacecraftScene from "./SpacecraftScene.jsx";
import Controls from "./Controls.jsx";

export default function App() {
  const [demoData, setDemoData] = useState(null);
  const [t, setT] = useState(0);
  const [playing, setPlaying] = useState(true);
  const [speed, setSpeed] = useState(1.0);

  useEffect(() => {
    let cancelled = false;
    fetch("/demo_data.json")
      .then((r) => r.json())
      .then((d) => {
        if (cancelled) return;
        setDemoData(d);
        setT(0);
      })
      .catch(() => {
        // If demo_data.json isn't present, we still show the scene.
        setDemoData(null);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const maxT = useMemo(() => {
    if (!demoData?.time?.length) return 1;
    return demoData.time.length - 1;
  }, [demoData]);

  useEffect(() => {
    if (!playing) return;
    const id = setInterval(() => {
      setT((prev) => (prev + Math.max(1, Math.round(speed))) % (maxT + 1));
    }, 33);
    return () => clearInterval(id);
  }, [playing, speed, maxT]);

  return (
    <div style={{ height: "100%", display: "grid", gridTemplateRows: "auto 1fr" }}>
      <div
        style={{
          padding: "14px 16px",
          borderBottom: "1px solid rgba(255,255,255,0.08)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 12
        }}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
          <div style={{ fontSize: 16, fontWeight: 700, letterSpacing: 0.2 }}>
            Cosmic Compass — Web Demo
          </div>
          <div style={{ fontSize: 12, opacity: 0.75 }}>
            Gravitational signature flyby visualization (React + Three.js)
          </div>
        </div>
        <Controls
          t={t}
          maxT={maxT}
          setT={setT}
          playing={playing}
          setPlaying={setPlaying}
          speed={speed}
          setSpeed={setSpeed}
          hasData={!!demoData}
        />
      </div>

      <div style={{ position: "relative" }}>
        <SpacecraftScene demoData={demoData} tIndex={t} />
        {!demoData && (
          <div
            style={{
              position: "absolute",
              left: 16,
              bottom: 16,
              maxWidth: 520,
              padding: 12,
              borderRadius: 12,
              background: "rgba(0,0,0,0.5)",
              border: "1px solid rgba(34,211,238,0.35)"
            }}
          >
            <div style={{ fontWeight: 700, marginBottom: 6 }}>Demo data not found</div>
            <div style={{ fontSize: 13, opacity: 0.85, lineHeight: 1.4 }}>
              Run the Python generator to create <code>demo_data.json</code> and copy it into{" "}
              <code>web_demo/public/</code>.
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

