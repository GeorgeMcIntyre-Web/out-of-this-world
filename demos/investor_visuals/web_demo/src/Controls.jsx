import React from "react";

export default function Controls({
  t,
  maxT,
  setT,
  playing,
  setPlaying,
  speed,
  setSpeed,
  hasData
}) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
      <button
        onClick={() => setPlaying((p) => !p)}
        style={{
          padding: "8px 10px",
          borderRadius: 10,
          border: "1px solid rgba(255,255,255,0.15)",
          background: playing ? "rgba(34,211,238,0.20)" : "rgba(255,255,255,0.06)",
          color: "white",
          cursor: "pointer"
        }}
      >
        {playing ? "Pause" : "Play"}
      </button>

      <div style={{ display: "flex", alignItems: "center", gap: 8, minWidth: 260 }}>
        <span style={{ fontSize: 12, opacity: 0.8 }}>t</span>
        <input
          type="range"
          min={0}
          max={maxT}
          value={Math.min(t, maxT)}
          onChange={(e) => setT(parseInt(e.target.value, 10))}
          disabled={!hasData}
          style={{ width: 200 }}
        />
        <span style={{ fontSize: 12, opacity: 0.8, minWidth: 46, textAlign: "right" }}>
          {Math.min(t, maxT)}/{maxT}
        </span>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <span style={{ fontSize: 12, opacity: 0.8 }}>speed</span>
        <select
          value={speed}
          onChange={(e) => setSpeed(parseFloat(e.target.value))}
          style={{
            padding: "7px 10px",
            borderRadius: 10,
            border: "1px solid rgba(255,255,255,0.15)",
            background: "rgba(255,255,255,0.06)",
            color: "white"
          }}
        >
          <option value={1}>1×</option>
          <option value={2}>2×</option>
          <option value={4}>4×</option>
          <option value={8}>8×</option>
        </select>
      </div>
    </div>
  );
}

