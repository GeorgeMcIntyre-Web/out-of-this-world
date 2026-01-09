import { act, renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { Frame } from "../types/sim";
import { useSimulationPlayback } from "./useSimulationPlayback";

function makeFrames(n: number): Frame[] {
  return Array.from({ length: n }, (_, i) => ({
    t_s: i,
    bodies: [],
    craft: [],
    events: [],
  }));
}

describe("useSimulationPlayback", () => {
  it("loadFrames sets frames and resets index", () => {
    const { result } = renderHook(() => useSimulationPlayback());
    act(() => result.current.loadFrames(makeFrames(3)));
    expect(result.current.state.frames.length).toBe(3);
    expect(result.current.state.currentIndex).toBe(0);
    expect(result.current.state.isPlaying).toBe(false);
  });

  it("play/pause toggles isPlaying", () => {
    const { result } = renderHook(() => useSimulationPlayback());
    act(() => result.current.loadFrames(makeFrames(2)));
    act(() => result.current.play());
    expect(result.current.state.isPlaying).toBe(true);
    act(() => result.current.pause());
    expect(result.current.state.isPlaying).toBe(false);
  });

  it("seek clamps to valid range", () => {
    const { result } = renderHook(() => useSimulationPlayback());
    act(() => result.current.loadFrames(makeFrames(3)));
    act(() => result.current.seek(-10));
    expect(result.current.state.currentIndex).toBe(0);
    act(() => result.current.seek(999));
    expect(result.current.state.currentIndex).toBe(2);
  });

  it("stepForward/Backward clamp properly", () => {
    const { result } = renderHook(() => useSimulationPlayback());
    act(() => result.current.loadFrames(makeFrames(2)));
    act(() => result.current.stepBackward());
    expect(result.current.state.currentIndex).toBe(0);
    act(() => result.current.stepForward());
    expect(result.current.state.currentIndex).toBe(1);
    act(() => result.current.stepForward());
    expect(result.current.state.currentIndex).toBe(1);
  });
});

