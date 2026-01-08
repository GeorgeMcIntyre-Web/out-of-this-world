import { useCallback, useEffect, useMemo, useState } from "react";
import type { Frame } from "../types/sim";

export type PlaybackState = {
  frames: Frame[];
  currentIndex: number;
  isPlaying: boolean;
  playbackRateFps: number;
};

export function useSimulationPlayback() {
  const [frames, setFrames] = useState<Frame[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackRateFps, setPlaybackRateFps] = useState(30);

  const currentFrame = useMemo(() => {
    if (frames.length === 0) return null;
    if (currentIndex < 0) return frames[0] ?? null;
    if (currentIndex >= frames.length) return frames[frames.length - 1] ?? null;
    return frames[currentIndex] ?? null;
  }, [frames, currentIndex]);

  const loadFrames = useCallback((next: Frame[]) => {
    if (next.length === 0) return;
    setFrames(next);
    setCurrentIndex(0);
    setIsPlaying(false);
  }, []);

  const play = useCallback(() => {
    if (frames.length === 0) return;
    setIsPlaying(true);
  }, [frames.length]);

  const pause = useCallback(() => {
    setIsPlaying(false);
  }, []);

  const seek = useCallback((index: number) => {
    if (frames.length === 0) return;
    if (Number.isFinite(index) === false) return;
    const clamped = Math.min(frames.length - 1, Math.max(0, Math.floor(index)));
    setCurrentIndex(clamped);
  }, [frames.length]);

  const stepForward = useCallback(() => {
    if (frames.length === 0) return;
    setCurrentIndex((i) => Math.min(frames.length - 1, i + 1));
  }, [frames.length]);

  const stepBackward = useCallback(() => {
    if (frames.length === 0) return;
    setCurrentIndex((i) => Math.max(0, i - 1));
  }, [frames.length]);

  useEffect(() => {
    if (isPlaying === false) return;
    if (frames.length === 0) return;
    if (playbackRateFps <= 0) return;

    const stepMs = 1000 / playbackRateFps;
    const handle = window.setInterval(() => {
      setCurrentIndex((i) => {
        if (i >= frames.length - 1) return i;
        return i + 1;
      });
    }, stepMs);

    return () => window.clearInterval(handle);
  }, [frames.length, isPlaying, playbackRateFps]);

  return {
    state: { frames, currentIndex, isPlaying, playbackRateFps } satisfies PlaybackState,
    currentFrame,
    loadFrames,
    play,
    pause,
    seek,
    stepForward,
    stepBackward,
    setPlaybackRateFps,
  };
}

