/**
 * 3D Trajectory visualization using Three.js
 */

import { Canvas } from "@react-three/fiber";
import { OrbitControls, Line, Grid, Stars, useTexture } from "@react-three/drei";
import { useMemo, Suspense } from "react";
import * as THREE from "three";
import type { ExperimentResult } from "../types/simulation";
import "./TrajectoryViewer.css";

interface TrajectoryViewerProps {
    experiments: ExperimentResult[];
}

// Planets with texture maps - all orbits in the same ecliptic plane
function Sun() {
    const colorMap = useTexture("/textures/sun.jpg");
    return (
        <mesh position={[0, 0, 0]}>
            <sphereGeometry args={[2.5, 32, 32]} />
            <meshStandardMaterial
                map={colorMap}
                emissive="#ff6600"
                emissiveIntensity={2.5}
                toneMapped={false}
            />
            <pointLight intensity={2} distance={100} decay={0.5} />
        </mesh>
    );
}

function Mercury() {
    const colorMap = useTexture("/textures/mercury.jpg");
    const angle = 0.5;
    return (
        <group>
            <mesh position={[4 * Math.cos(angle), 0, 4 * Math.sin(angle)]}>
                <sphereGeometry args={[0.3, 32, 32]} />
                <meshStandardMaterial map={colorMap} roughness={0.9} />
            </mesh>
            <OrbitRing radius={4} color="#555" />
        </group>
    );
}

function Venus() {
    const colorMap = useTexture("/textures/venus.jpg");
    const angle = 2.5;
    return (
        <group>
            <mesh position={[6 * Math.cos(angle), 0, 6 * Math.sin(angle)]}>
                <sphereGeometry args={[0.7, 32, 32]} />
                <meshStandardMaterial map={colorMap} color="#ffe4b5" roughness={0.3} /> {/* Cream/beige tint for Venus clouds */}
            </mesh>
            <OrbitRing radius={6} color="#665" />
        </group>
    );
}

function Mars() {
    const colorMap = useTexture("/textures/mars.jpg");
    const angle = 4.2;
    return (
        <group>
            <mesh position={[12 * Math.cos(angle), 0, 12 * Math.sin(angle)]}>
                <sphereGeometry args={[0.4, 32, 32]} />
                <meshStandardMaterial map={colorMap} color="#ff6b4a" roughness={0.8} /> {/* Red tint for Mars */}
            </mesh>
            <OrbitRing radius={12} color="#743" />
        </group>
    );
}

function OrbitRing({ radius, color = "#444" }: { radius: number; color?: string }) {
    return (
        <mesh rotation={[Math.PI / 2, 0, 0]}>
            <ringGeometry args={[radius - 0.02, radius + 0.02, 128]} />
            <meshBasicMaterial color={color} side={THREE.DoubleSide} transparent opacity={0.3} />
        </mesh>
    );
}

function TexturedEarthAndMoon() {
    const [colorMap, normalMap, specularMap, cloudsMap] = useTexture([
        "/textures/2k_earth_daymap.jpg",
        "/textures/2k_earth_normal_map.png",
        "/textures/2k_earth_specular_map.png",
        "/textures/2k_earth_clouds.png",
    ]);

    const moonColorMap = useTexture("/textures/2k_moon.jpg");

    // Position Earth at angle 1.2 radians on its orbit
    const angle = 1.2;
    const earthX = 9 * Math.cos(angle);
    const earthZ = 9 * Math.sin(angle);

    return (
        <>
            {/* Earth's orbit ring stays at origin */}
            <OrbitRing radius={9} color="#357" />

            <group position={[earthX, 0, earthZ]}>
                <group rotation={[0, 0, 0.4]}> {/* Earth's axial tilt */}
                    {/* Earth Sphere */}
                    <mesh>
                        <sphereGeometry args={[0.8, 64, 64]} />
                        <meshPhongMaterial
                            map={colorMap}
                            normalMap={normalMap}
                            specularMap={specularMap}
                            specular={new THREE.Color(0x333333)}
                            shininess={5}
                        />
                    </mesh>
                    {/* Cloud Layer */}
                    <mesh scale={[1.01, 1.01, 1.01]}>
                        <sphereGeometry args={[0.8, 64, 64]} />
                        <meshPhongMaterial
                            map={cloudsMap}
                            transparent
                            opacity={0.8}
                            side={THREE.DoubleSide}
                            blending={THREE.AdditiveBlending}
                            depthWrite={false}
                        />
                    </mesh>
                    {/* Atmosphere Glow */}
                    <mesh scale={[1.15, 1.15, 1.15]}>
                        <sphereGeometry args={[0.8, 32, 32]} />
                        <meshBasicMaterial color="#3b82f6" transparent opacity={0.1} side={THREE.BackSide} />
                    </mesh>

                    {/* Moon - Orbiting Earth */}
                    <group rotation={[0, Math.PI / 3, 0]}>
                        <mesh position={[2, 0, 0]}>
                            <sphereGeometry args={[0.22, 32, 32]} />
                            <meshStandardMaterial
                                map={moonColorMap}
                                roughness={0.8}
                                metalness={0.1}
                            />
                        </mesh>
                        {/* Moon Orbit Ring */}
                        <mesh rotation={[Math.PI / 2, 0, 0]}>
                            <ringGeometry args={[1.98, 2.02, 64]} />
                            <meshBasicMaterial color="#555" side={THREE.DoubleSide} transparent opacity={0.15} />
                        </mesh>
                    </group>
                </group>
            </group>
        </>
    );
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

function DetailedSpacecraft({ position }: { position: [number, number, number] }) {
    return (
        <group position={position} rotation={[0, Math.PI / 4, Math.PI / 6]}>
            {/* Main Hull */}
            <mesh rotation={[0, 0, Math.PI / 2]}>
                <cylinderGeometry args={[0.02, 0.02, 0.1, 32]} />
                <meshStandardMaterial color="#e2e8f0" metalness={0.8} roughness={0.2} />
            </mesh>

            {/* Engine Nozzle */}
            <mesh position={[0.055, 0, 0]} rotation={[0, 0, -Math.PI / 2]}>
                <coneGeometry args={[0.015, 0.03, 32]} />
                <meshStandardMaterial color="#334155" />
            </mesh>

            {/* Engine Glow */}
            <mesh position={[0.07, 0, 0]}>
                <sphereGeometry args={[0.008, 16, 16]} />
                <meshBasicMaterial color="#f97316" />
                <pointLight color="#f97316" intensity={2} distance={0.5} decay={2} />
            </mesh>

            {/* Solar Panel Strut */}
            <mesh rotation={[Math.PI / 2, 0, 0]}>
                <cylinderGeometry args={[0.005, 0.005, 0.25]} />
                <meshStandardMaterial color="#94a3b8" />
            </mesh>

            {/* Solar Panels (Left & Right) */}
            {[-0.15, 0.15].map((z, i) => (
                <group key={i} position={[0, 0, z]}>
                    <mesh rotation={[0, 0, 0]}>
                        <boxGeometry args={[0.06, 0.002, 0.12]} />
                        <meshStandardMaterial color="#1e3a8a" metalness={0.6} roughness={0.1} />
                    </mesh>
                    {/* Grid lines texture simulation */}
                    <mesh position={[0, 0.002, 0]}>
                        <boxGeometry args={[0.05, 0.001, 0.11]} />
                        <meshStandardMaterial color="#2563eb" emissive="#1d4ed8" emissiveIntensity={0.2} />
                    </mesh>
                </group>
            ))}

            {/* Sensor Array / Antenna */}
            <group position={[-0.03, 0.025, 0]} rotation={[0, 0, Math.PI / 4]}>
                <mesh>
                    <cylinderGeometry args={[0.003, 0.003, 0.05]} />
                    <meshStandardMaterial color="#cbd5e1" />
                </mesh>
                <mesh position={[0, 0.025, 0]}>
                    <sphereGeometry args={[0.015, 16, 16]} />
                    <meshStandardMaterial color="#fbbf24" metalness={0.9} roughness={0.1} />
                </mesh>
            </group>
        </group>
    );
}

function SceneContent({ experiments }: { experiments: ExperimentResult[] }) {
    const trajectoryData = useMemo(() => {
        return experiments.map((exp) => {
            // Keep existing normalization logic
            const maxPos = Math.max(
                ...exp.true_position.map((p) =>
                    Math.max(Math.abs(p.x), Math.abs(p.y), Math.abs(p.z))
                ),
                1
            );
            const scale = 1 / maxPos;

            // Position Earth at angle 1.2 radians
            const earthAngle = 1.2;
            const earthX = 9 * Math.cos(earthAngle);
            const earthZ = 9 * Math.sin(earthAngle);

            const truePoints: [number, number, number][] = exp.true_position.map((p) => [
                p.x * scale * 2 + earthX,
                p.y * scale * 2,
                p.z * scale * 2 + earthZ,
            ]);

            const estPoints: [number, number, number][] = exp.est_position.map((p) => [
                p.x * scale * 2 + earthX,
                p.y * scale * 2,
                p.z * scale * 2 + earthZ,
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

    // Position spacecraft near Earth
    const earthAngle = 1.2;
    const earthX = 9 * Math.cos(earthAngle);
    const earthZ = 9 * Math.sin(earthAngle);
    const lastPoint = trajectoryData[0]?.truePoints.slice(-1)[0] || [earthX, 0, earthZ];

    return (
        <>
            <ambientLight intensity={0.1} />
            <pointLight position={[0, 0, 0]} intensity={2} color="#fff" /> {/* Sun Light */}
            <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={0.5} />

            <Sun />
            <Mercury />
            <Venus />
            <Mars />

            <Suspense fallback={null}>
                <TexturedEarthAndMoon />
            </Suspense>

            {trajectoryData.map((data) => (
                <group key={data.name}>
                    <Trajectory
                        points={data.truePoints}
                        color={data.isQuantum ? "#10b981" : "#3b82f6"}
                        lineWidth={3}
                    />
                    <Trajectory
                        points={data.estPoints}
                        color={data.isQuantum ? "#34d399" : "#60a5fa"}
                        lineWidth={1.5}
                    />
                </group>
            ))}

            <DetailedSpacecraft position={lastPoint} />

            <Grid
                args={[40, 40]}
                cellSize={1}
                cellThickness={0.5}
                cellColor="#1e293b"
                sectionSize={5}
                sectionThickness={1}
                sectionColor="#334155"
                fadeDistance={50}
                position={[0, -5, 0]}
            />
        </>
    );
}

export function TrajectoryViewer({ experiments }: TrajectoryViewerProps) {
    return (
        <div className="trajectory-viewer">
            <Canvas camera={{ position: [15, 10, 15], fov: 45 }}>
                <SceneContent experiments={experiments} />
                <OrbitControls enablePan={true} enableZoom={true} enableRotate={true} />
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
