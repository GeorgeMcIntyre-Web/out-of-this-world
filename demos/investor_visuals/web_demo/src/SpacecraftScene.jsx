import React, { useMemo } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Stars } from "@react-three/drei";
import * as THREE from "three";

function NeutronStar() {
  return (
    <mesh position={[2.5, 0, 0]}>
      <sphereGeometry args={[0.35, 64, 64]} />
      <meshStandardMaterial color={"#3b82f6"} emissive={"#1d4ed8"} emissiveIntensity={0.85} />
    </mesh>
  );
}

function Spacecraft({ position }) {
  return (
    <mesh position={position}>
      <coneGeometry args={[0.10, 0.25, 24]} />
      <meshStandardMaterial color={"#fbbf24"} emissive={"#f59e0b"} emissiveIntensity={0.35} />
    </mesh>
  );
}

function TrajectoryLine({ points }) {
  const geom = useMemo(() => {
    const g = new THREE.BufferGeometry();
    const flat = points.flatMap((p) => [p[0], p[1], p[2]]);
    g.setAttribute("position", new THREE.Float32BufferAttribute(flat, 3));
    return g;
  }, [points]);

  return (
    <line geometry={geom}>
      <lineBasicMaterial color={"#22d3ee"} linewidth={2} />
    </line>
  );
}

export default function SpacecraftScene({ demoData, tIndex }) {
  const { pos, linePoints } = useMemo(() => {
    if (!demoData?.positions?.length) {
      // fallback orbit if no data
      const tt = (tIndex / 120) * Math.PI * 2;
      const p = [-2.5 + Math.cos(tt) * 2.2, Math.sin(tt) * 1.2, Math.sin(tt * 0.5) * 0.5];
      const pts = Array.from({ length: 120 }, (_, i) => {
        const a = (i / 120) * Math.PI * 2;
        return [-2.5 + Math.cos(a) * 2.2, Math.sin(a) * 1.2, Math.sin(a * 0.5) * 0.5];
      });
      return { pos: p, linePoints: pts };
    }

    // The Python demo outputs km; normalize to a nice visual scale for Three.
    const scale = 1 / 800; // km -> scene units
    const positions = demoData.positions;
    const idx = Math.max(0, Math.min(tIndex, positions.length - 1));
    const p = positions[idx];

    // Re-center around the neutron star for clarity
    const ns = demoData.neutron_star_position ?? [1000000, 0, 0];
    const centered = [(p[0] - ns[0]) * scale + 2.5, (p[1] - ns[1]) * scale, (p[2] - ns[2]) * scale];

    const pts = positions.map((q) => [
      (q[0] - ns[0]) * scale + 2.5,
      (q[1] - ns[1]) * scale,
      (q[2] - ns[2]) * scale
    ]);
    return { pos: centered, linePoints: pts };
  }, [demoData, tIndex]);

  return (
    <Canvas camera={{ position: [0, 2.2, 6.5], fov: 50 }}>
      <ambientLight intensity={0.25} />
      <directionalLight position={[5, 5, 5]} intensity={1.15} />
      <Stars radius={60} depth={35} count={2500} factor={2} saturation={0} fade speed={0.5} />

      <NeutronStar />
      <TrajectoryLine points={linePoints} />
      <Spacecraft position={pos} />

      <OrbitControls enablePan={false} maxDistance={18} minDistance={2.2} />
    </Canvas>
  );
}

