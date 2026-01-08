/**
 * 3D Trajectory visualization using Three.js
 */

import { Canvas } from "@react-three/fiber";
import { OrbitControls, Line, Sphere, Grid } from "@react-three/drei";
import { useMemo } from "react";
import * as THREE from "three";
import type { ExperimentResult } from "../types/simulation";
import "./TrajectoryViewer.css";

interface TrajectoryViewerProps {
    experiments: ExperimentResult[];
}

function Trajectory({
    points,
    color,
    lineWidth = 2,
}: {
    points: [number, number, number][];
    color: string;
    lineWidth?: number;
}) {
    if (points.length < 2) return null;
    return (
        <Line
            points={points}
            color={color}
            lineWidth={lineWidth}
        />
    );
}

function ErrorEllipsoids({
    points,
    sigmas,
    color,
}: {
    points: [number, number, number][];
    sigmas: number[];
    color: string;
}) {
    // Show small markers at ~8 points along the trajectory
    const step = Math.max(1, Math.floor(points.length / 8));
    const indices = [];
    for (let i = step; i < points.length; i += step) {
        indices.push(i);
    }

    return (
        <>
            {indices.map((i) => {
                // Very small fixed-size markers, not scaled by sigma
                const scale = 0.02;
                return (
                    <Sphere key={i} args={[scale, 8, 8]} position={points[i]}>
                        <meshBasicMaterial color={color} transparent opacity={0.15} />
                    </Sphere>
                );
            })}
        </>
    );
}

function Spacecraft({ position }: { position: [number, number, number] }) {
    return (
        <group position={position}>
            {/* Body */}
            <mesh>
                <boxGeometry args={[0.05, 0.03, 0.03]} />
                <meshStandardMaterial color="#60a5fa" metalness={0.8} roughness={0.2} />
            </mesh>
            {/* Solar panels */}
            <mesh position={[0, 0.05, 0]}>
                <boxGeometry args={[0.02, 0.08, 0.01]} />
                <meshStandardMaterial color="#1e40af" />
            </mesh>
            <mesh position={[0, -0.05, 0]}>
                <boxGeometry args={[0.02, 0.08, 0.01]} />
                <meshStandardMaterial color="#1e40af" />
            </mesh>
        </group>
    );
}

export function TrajectoryViewer({ experiments }: TrajectoryViewerProps) {
    const trajectoryData = useMemo(() => {
        return experiments.map((exp) => {
            // Normalize positions for visualization (scale to unit cube)
            const maxPos = Math.max(
                ...exp.true_position.map((p) =>
                    Math.max(Math.abs(p.x), Math.abs(p.y), Math.abs(p.z))
                ),
                1
            );
            const scale = 1 / maxPos;

            const truePoints: [number, number, number][] = exp.true_position.map((p) => [
                p.x * scale,
                p.y * scale,
                p.z * scale,
            ]);

            const estPoints: [number, number, number][] = exp.est_position.map((p) => [
                p.x * scale,
                p.y * scale,
                p.z * scale,
            ]);

            return {
                name: exp.name,
                truePoints,
                estPoints,
                sigmas: exp.pos_sigma_m,
                isQuantum: exp.imu_profile === "quantum",
            };
        });
    }, [experiments]);

    if (experiments.length === 0) {
        return (
            <div className="trajectory-viewer empty">
                <div className="empty-state">
                    <span className="icon">🛰️</span>
                    <p>Run a simulation to see the 3D trajectory</p>
                </div>
            </div>
        );
    }

    // Use first experiment for spacecraft position
    const lastPoint = trajectoryData[0]?.truePoints.slice(-1)[0] || [0, 0, 0];

    return (
        <div className="trajectory-viewer">
            <Canvas camera={{ position: [2, 1.5, 2], fov: 50 }}>
                <ambientLight intensity={0.5} />
                <pointLight position={[10, 10, 10]} intensity={1} />

                <Grid
                    args={[4, 4]}
                    cellSize={0.2}
                    cellColor="#334155"
                    sectionColor="#475569"
                    fadeDistance={10}
                    position={[0, -0.5, 0]}
                />

                {trajectoryData.map((data) => (
                    <group key={data.name}>
                        {/* True trajectory - thicker, brighter */}
                        <Trajectory
                            points={data.truePoints}
                            color={data.isQuantum ? "#10b981" : "#3b82f6"}
                            lineWidth={3}
                        />
                        {/* Estimated trajectory - dashed effect via different shade */}
                        <Trajectory
                            points={data.estPoints}
                            color={data.isQuantum ? "#34d399" : "#60a5fa"}
                            lineWidth={1.5}
                        />
                    </group>
                ))}

                <Spacecraft position={lastPoint} />

                <OrbitControls
                    enablePan={true}
                    enableZoom={true}
                    enableRotate={true}
                    autoRotate={false}
                    autoRotateSpeed={0.5}
                />
            </Canvas>

            <div className="legend">
                <div className="legend-item">
                    <span className="color-box" style={{ background: "#3b82f6" }}></span>
                    Classical
                </div>
                <div className="legend-item">
                    <span className="color-box" style={{ background: "#22c55e" }}></span>
                    Quantum
                </div>
            </div>
        </div>
    );
}
