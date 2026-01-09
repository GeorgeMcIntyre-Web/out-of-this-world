import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Html, Line, OrbitControls, Stars, Text } from "@react-three/drei";
import { useEffect, useMemo, useRef, useState } from "react";
import * as THREE from "three";
import type { Frame, Vec3 } from "../types/sim";

export type SceneUiState = {
  showReferenceAxes: boolean;
  showEclipticGrid: boolean;
  showInertialPlane?: boolean;
  showCameraHorizon?: boolean;
  showOrbitalPlanes: boolean;
  showSpacetimeSurface: boolean;
  showClocks: boolean;
  showLightBending: boolean;
  relativityStrength: number;
  focusSelected?: boolean;
};

type Props = {
  frames: Frame[];
  currentIndex: number;
  frame: Frame | null;
  selectedId: string | null;
  onSelect: (id: string | null) => void;
  ui: SceneUiState;
};

function maxAbsFromFrames(frames: Frame[]): number {
  if (frames.length === 0) return 1;
  let max = 1;
  for (const f of frames) {
    for (const b of f.bodies) {
      max = Math.max(max, Math.abs(b.position_m[0]), Math.abs(b.position_m[1]), Math.abs(b.position_m[2]));
      max = Math.max(max, b.radius_m);
    }
    for (const c of f.craft) {
      max = Math.max(max, Math.abs(c.position_m[0]), Math.abs(c.position_m[1]), Math.abs(c.position_m[2]));
    }
  }
  return max;
}

function scaleVec3(v: Vec3, scale: number): [number, number, number] {
  return [v[0] * scale, v[1] * scale, v[2] * scale];
}

function normalizeSafe(v: THREE.Vector3): THREE.Vector3 {
  const len = v.length();
  if (len <= 1e-9) return v;
  return v.multiplyScalar(1 / len);
}

type OrbitalElements = {
  orbitNormal: THREE.Vector3;
  inclinationDeg: number;
  omegaDeg: number;
  nodeDir: THREE.Vector3;
};

function computeOrbitalElements(frames: Frame[], craftId: string): OrbitalElements | null {
  if (frames.length === 0) return null;
  const first = frames.find((f) => f.craft.some((c) => c.id === craftId)) ?? null;
  if (first === null) return null;
  const craft = first.craft.find((c) => c.id === craftId) ?? null;
  if (craft === null) return null;

  const r = new THREE.Vector3(...craft.position_m);
  const v = new THREE.Vector3(...craft.velocity_mps);
  const h = new THREE.Vector3().crossVectors(r, v);
  if (h.length() <= 1e-9) return null;
  const orbitNormal = h.normalize();

  const k = new THREE.Vector3(0, 1, 0);
  const c = Math.max(-1, Math.min(1, orbitNormal.dot(k)));
  const inclinationDeg = (Math.acos(c) * 180) / Math.PI;

  const node = new THREE.Vector3().crossVectors(k, orbitNormal);
  if (node.length() <= 1e-9) {
    return {
      orbitNormal,
      inclinationDeg,
      omegaDeg: 0,
      nodeDir: new THREE.Vector3(1, 0, 0),
    };
  }

  const nodeDir = node.normalize();
  const omega = Math.atan2(nodeDir.z, nodeDir.x);
  const omegaDeg = ((omega * 180) / Math.PI + 360) % 360;
  return { orbitNormal, inclinationDeg, omegaDeg, nodeDir };
}

function warpTowardMass(position: THREE.Vector3, strength: number, rSScene: number): THREE.Vector3 {
  if (strength <= 0) return position;
  const r = position.length();
  if (r <= 1e-6) return position;
  const pull = (rSScene / r) * 0.75 * strength;
  const dir = normalizeSafe(position.clone()).multiplyScalar(-pull);
  return position.clone().add(dir);
}

function ReferenceAxes({ length, opacity }: { length: number; opacity: number }) {
  const o = Math.max(0, Math.min(1, opacity));
  return (
    <>
      <Line points={[[0, 0, 0], [length, 0, 0]]} color="#ef4444" transparent opacity={o} />
      <Line points={[[0, 0, 0], [0, length, 0]]} color="#22c55e" transparent opacity={o} />
      <Line points={[[0, 0, 0], [0, 0, length]]} color="#3b82f6" transparent opacity={o} />
    </>
  );
}

function InertialPlane({ radius, opacity }: { radius: number; opacity: number }) {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]}>
      <circleGeometry args={[radius, 96]} />
      <meshBasicMaterial color="#94a3b8" transparent opacity={opacity} side={THREE.DoubleSide} />
    </mesh>
  );
}

function CameraHorizonPlane({ size, opacity }: { size: number; opacity: number }) {
  const ref = useRef<THREE.Mesh>(null);
  const { camera } = useThree();

  useFrame(() => {
    const mesh = ref.current;
    if (mesh === null) return;
    mesh.quaternion.copy(camera.quaternion);
  });

  return (
    <mesh ref={ref} position={[0, 0, 0]}>
      <planeGeometry args={[size, size, 1, 1]} />
      <meshBasicMaterial color="#94a3b8" transparent opacity={opacity} side={THREE.DoubleSide} />
    </mesh>
  );
}

function EclipticDisk({ radius }: { radius: number }) {
  const circles = useMemo(() => [0.25, 0.5, 0.75, 1].map((t) => t * radius), [radius]);
  const radials = useMemo(() => {
    const lines: [number, number, number][][] = [];
    const n = 24;
    for (let i = 0; i < n; i += 1) {
      const a = (i / n) * Math.PI * 2;
      const x = Math.cos(a) * radius;
      const z = Math.sin(a) * radius;
      lines.push([
        [0, 0, 0],
        [x, 0, z],
      ]);
    }
    return lines;
  }, [radius]);

  const labels = useMemo(
    () => [
      { text: "0°", pos: [radius, 0, 0] as const },
      { text: "90°", pos: [0, 0, radius] as const },
      { text: "180°", pos: [-radius, 0, 0] as const },
      { text: "270°", pos: [0, 0, -radius] as const },
    ],
    [radius],
  );

  return (
    <group>
      {circles.map((r) => (
        <mesh key={r} rotation={[-Math.PI / 2, 0, 0]}>
          <ringGeometry args={[r - radius * 0.002, r + radius * 0.002, 128]} />
          <meshBasicMaterial color="#94a3b8" transparent opacity={0.08} side={THREE.DoubleSide} />
        </mesh>
      ))}
      {radials.map((p, idx) => (
        <Line key={idx} points={p} color="#94a3b8" transparent opacity={0.06} />
      ))}
      {labels.map((l) => (
        <Text
          key={l.text}
          position={[l.pos[0], l.pos[1] + radius * 0.01, l.pos[2]]}
          fontSize={radius * 0.04}
          color="#cbd5e1"
          anchorX="center"
          anchorY="middle"
        >
          {l.text}
        </Text>
      ))}
    </group>
  );
}

function OrbitalPlane({
  normal,
  radius,
  inclinationDeg,
}: {
  normal: THREE.Vector3;
  radius: number;
  inclinationDeg: number;
}) {
  const axis = normalizeSafe(new THREE.Vector3().crossVectors(new THREE.Vector3(0, 1, 0), normal));
  const angle = Math.acos(Math.max(-1, Math.min(1, normal.clone().normalize().dot(new THREE.Vector3(0, 1, 0)))));

  const quat = new THREE.Quaternion();
  if (axis.length() > 1e-9) quat.setFromAxisAngle(axis, angle);

  return (
    <group quaternion={quat}>
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[radius, 96]} />
        <meshBasicMaterial color="#60a5fa" transparent opacity={0.18} side={THREE.DoubleSide} />
      </mesh>
      <Text position={[radius * 0.6, radius * 0.02, 0]} fontSize={radius * 0.05} color="#93c5fd">
        i = {inclinationDeg.toFixed(1)}°
      </Text>
    </group>
  );
}

function NodesLine({
  nodeDir,
  omegaDeg,
  radius,
}: {
  nodeDir: THREE.Vector3;
  omegaDeg: number;
  radius: number;
}) {
  if (nodeDir.length() <= 1e-9) return null;
  const dir = nodeDir.clone();
  const p1 = dir.clone().multiplyScalar(-radius);
  const p2 = dir.clone().multiplyScalar(radius);
  const asc = dir.clone().multiplyScalar(radius * 0.9);

  return (
    <group>
      <Line points={[[p1.x, p1.y, p1.z], [p2.x, p2.y, p2.z]]} color="#fbbf24" transparent opacity={0.55} />
      <mesh position={[asc.x, asc.y, asc.z]}>
        <coneGeometry args={[radius * 0.03, radius * 0.08, 3]} />
        <meshBasicMaterial color="#fbbf24" transparent opacity={0.9} />
      </mesh>
      <Text position={[asc.x, asc.y + radius * 0.06, asc.z]} fontSize={radius * 0.05} color="#fde68a">
        Ω = {omegaDeg.toFixed(0)}°
      </Text>
    </group>
  );
}

function SpacetimeSurface({
  radius,
  strength,
}: {
  radius: number;
  strength: number;
}) {
  const meshRef = useRef<THREE.Mesh>(null);

  useEffect(() => {
    const mesh = meshRef.current;
    if (mesh === null) return;
    const geometry = mesh.geometry as THREE.PlaneGeometry;
    const pos = geometry.attributes.position;
    const wellScale = radius * 0.25 * strength;
    for (let i = 0; i < pos.count; i += 1) {
      const x = pos.getX(i);
      const z = pos.getY(i); // planeGeometry is XY; we rotate it into XZ later.
      const r = Math.sqrt(x * x + z * z) + 1e-6;
      const y = -wellScale / r;
      pos.setZ(i, y);
    }
    pos.needsUpdate = true;
    geometry.computeVertexNormals();
  }, [radius, strength]);

  return (
    <mesh ref={meshRef} rotation={[-Math.PI / 2, 0, 0]}>
      <planeGeometry args={[radius * 2, radius * 2, 96, 96]} />
      <meshStandardMaterial
        color="#8b5cf6"
        transparent
        opacity={0.18}
        wireframe
      />
    </mesh>
  );
}

function LightBendingRays({ radius, strength, rSScene }: { radius: number; strength: number; rSScene: number }) {
  const rays = useMemo(() => [-0.3, 0, 0.3], []);
  const makeRay = (z0: number) => {
    const points: [number, number, number][] = [];
    const n = 64;
    for (let i = 0; i <= n; i += 1) {
      const t = i / n;
      const x = (t - 0.5) * radius * 2;
      const z = z0 * radius;
      const base = new THREE.Vector3(x, 0, z);
      const curved = warpTowardMass(base, strength, rSScene * 1.5);
      points.push([curved.x, curved.y + radius * 0.02, curved.z]);
    }
    return points;
  };

  return (
    <>
      {rays.map((z0) => (
        <Line key={z0} points={makeRay(z0)} color="#fb7185" transparent opacity={0.8} />
      ))}
    </>
  );
}

function formatDistanceMeters(m: number): string {
  const a = Math.abs(m);
  if (a >= 1e9) return `${(m / 1e9).toFixed(2)} Gm`;
  if (a >= 1e6) return `${(m / 1e6).toFixed(2)} Mm`;
  if (a >= 1e3) return `${(m / 1e3).toFixed(2)} km`;
  return `${m.toFixed(0)} m`;
}

function HudProbe({
  onUpdate,
}: {
  onUpdate: (next: { cameraDistance: number; fovDeg: number }) => void;
}) {
  const { camera } = useThree();
  const lastRef = useRef(0);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    if (t - lastRef.current < 0.2) return;
    lastRef.current = t;
    onUpdate({ cameraDistance: camera.position.length(), fovDeg: (camera as THREE.PerspectiveCamera).fov ?? 45 });
  });

  return null;
}

export function SceneHost({ frames, currentIndex, frame, selectedId, onSelect, ui }: Props) {
  const maxAbs = useMemo(() => maxAbsFromFrames(frames), [frames]);
  const sceneScale = useMemo(() => {
    const base = maxAbs;
    if (base <= 0) return 1;
    return 1 / base;
  }, [maxAbs]);

  const metersRadius = useMemo(() => 1 / sceneScale, [sceneScale]); // "meters" extents
  const sceneRadius = useMemo(() => metersRadius * sceneScale, [metersRadius, sceneScale]);

  const compact = useMemo(() => {
    if (frame === null) return null;
    return frame.bodies.find((b) => b.id === "compact") ?? null;
  }, [frame]);

  const rSScene = useMemo(() => {
    const rS = compact?.schwarzschild_radius_m;
    if (rS === undefined || rS === null) return 0;
    return rS * sceneScale;
  }, [compact?.schwarzschild_radius_m, sceneScale]);

  const selectedPos = useMemo(() => {
    if (frame === null) return null;
    if (selectedId === null) return null;
    const craft = frame.craft.find((c) => c.id === selectedId) ?? null;
    if (craft === null) return null;
    return new THREE.Vector3(...scaleVec3(craft.position_m, sceneScale));
  }, [frame, sceneScale, selectedId]);

  const orbital = useMemo(() => {
    if (selectedId === null) return null;
    return computeOrbitalElements(frames, selectedId);
  }, [frames, selectedId]);

  const trail = useMemo(() => {
    if (frames.length === 0) return null;
    if (selectedId === null) return null;
    const points: [number, number, number][] = [];
    const upto = Math.min(frames.length - 1, Math.max(0, currentIndex));
    for (let i = 0; i <= upto; i += 1) {
      const f = frames[i];
      const c = f.craft.find((cc) => cc.id === selectedId) ?? null;
      if (c === null) continue;
      const p = new THREE.Vector3(...scaleVec3(c.position_m, sceneScale));
      points.push([p.x, p.y, p.z]);
    }
    if (points.length < 2) return null;
    return points;
  }, [currentIndex, frames, sceneScale, selectedId]);

  const trailRel = useMemo(() => {
    if (trail === null) return null;
    if (ui.relativityStrength <= 0) return null;
    if (rSScene <= 0) return null;
    return trail.map((p) => {
      const v = new THREE.Vector3(p[0], p[1], p[2]);
      const w = warpTowardMass(v, ui.relativityStrength, rSScene);
      return [w.x, w.y, w.z] as [number, number, number];
    });
  }, [rSScene, trail, ui.relativityStrength]);

  const controlsRef = useRef<any>(null);
  const [hud, setHud] = useState<{ cameraDistance: number; fovDeg: number } | null>(null);

  useEffect(() => {
    if (ui.focusSelected !== true) return;
    const controls = controlsRef.current as any;
    if (controls === null) return;
    if (selectedPos === null) return;
    controls.target.set(selectedPos.x, selectedPos.y, selectedPos.z);
    controls.update();
  }, [selectedPos, ui.focusSelected]);

  if (frame === null) {
    return <div className="trajectory-viewer empty">Run a simulation to see 3D.</div>;
  }

  const rulerMeters = (() => {
    if (hud === null) return null;
    if (sceneScale <= 0) return null;
    const fovRad = (hud.fovDeg * Math.PI) / 180;
    const viewHeight = 2 * hud.cameraDistance * Math.tan(fovRad / 2);
    const sceneLen = viewHeight * 0.25;
    const metersLen = sceneLen / sceneScale;
    return Math.max(0, metersLen);
  })();

  return (
    <div className="trajectory-viewer">
      <Canvas
        camera={{ position: [1.5, 1.1, 1.5], fov: 45 }}
        onPointerMissed={() => onSelect(null)}
      >
        <fog attach="fog" args={["#0b1020", 2, 6]} />
        <ambientLight intensity={0.25} />
        <pointLight position={[2, 2, 2]} intensity={1.2} />
        <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={0} />

        {ui.showReferenceAxes && <ReferenceAxes length={sceneRadius * 0.6} opacity={0.6} />}
        {ui.showEclipticGrid && <EclipticDisk radius={sceneRadius * 0.75} />}
        {ui.showInertialPlane && <InertialPlane radius={sceneRadius * 0.62} opacity={0.06} />}
        {ui.showCameraHorizon && <CameraHorizonPlane size={sceneRadius * 0.9} opacity={0.02} />}

        {ui.showSpacetimeSurface && (
          <SpacetimeSurface radius={sceneRadius * 0.65} strength={ui.relativityStrength} />
        )}

        {ui.showLightBending && (
          <LightBendingRays radius={sceneRadius * 0.6} strength={ui.relativityStrength} rSScene={rSScene} />
        )}

        {ui.showOrbitalPlanes && orbital !== null && (
          <>
            <OrbitalPlane
              normal={orbital.orbitNormal}
              radius={sceneRadius * 0.6}
              inclinationDeg={orbital.inclinationDeg}
            />
            <NodesLine nodeDir={orbital.nodeDir} omegaDeg={orbital.omegaDeg} radius={sceneRadius * 0.65} />
          </>
        )}

        {trail !== null && <Line points={trail} color="#60a5fa" lineWidth={2} />}
        {trailRel !== null && <Line points={trailRel} color="#fb923c" lineWidth={2} />}

        {frame.bodies.map((b, idx) => {
          const pos = scaleVec3(b.position_m, sceneScale);
          const r = Math.max(0.01, b.radius_m * sceneScale);
          const color = b.color ?? "#94a3b8";
          const isSelected = selectedId === b.id;
          // Vertical offset for label to prevent overlap (stagger based on index)
          const labelYOffset = r + 0.2 + idx * 0.35;

          return (
            <mesh
              key={b.id}
              position={pos}
              onClick={(e) => {
                e.stopPropagation();
                onSelect(b.id);
              }}
              scale={isSelected ? 1.1 : 1}
            >
              <sphereGeometry args={[r, 32, 32]} />
              <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.15} />
              {ui.showClocks && (
                <Html
                  position={[0, labelYOffset, 0]}
                  center
                  style={{ pointerEvents: 'none' }}
                >
                  <div className={`clock ${isSelected ? 'clock--expanded' : ''}`}>
                    <div className="clock-title">{b.name}</div>
                    {isSelected && (
                      <>
                        <div className="clock-row">
                          rₛ:{" "}
                          {b.schwarzschild_radius_m === undefined || b.schwarzschild_radius_m === null
                            ? "—"
                            : `${b.schwarzschild_radius_m.toFixed(0)} m`}
                        </div>
                        <div className="clock-row">
                          rate@surface:{" "}
                          {b.time_dilation_factor_at_surface === undefined || b.time_dilation_factor_at_surface === null
                            ? "—"
                            : `${b.time_dilation_factor_at_surface.toFixed(9)}×`}
                        </div>
                      </>
                    )}
                  </div>
                </Html>
              )}
            </mesh>
          );
        })}

        {frame.craft.map((c, idx) => {
          const posScene = new THREE.Vector3(...scaleVec3(c.position_m, sceneScale));
          const warped = warpTowardMass(posScene, ui.relativityStrength, rSScene);
          const pos = ui.relativityStrength <= 0 ? posScene : warped;
          const isSelected = selectedId === c.id;
          // Vertical offset for craft labels - start after body labels to avoid collision
          // Use negative offset (below object) to separate from body labels above
          const labelYOffset = -(0.3 + idx * 1.5);

          const color = c.id.endsWith(".est") ? "#22c55e" : "#e2e8f0";
          const emissive = isSelected ? "#fbbf24" : color;

          return (
            <mesh
              key={c.id}
              position={[pos.x, pos.y, pos.z]}
              onClick={(e) => {
                e.stopPropagation();
                onSelect(c.id);
              }}
              scale={isSelected ? 1.5 : 1}
            >
              <sphereGeometry args={[0.02, 20, 20]} />
              <meshStandardMaterial color={color} emissive={emissive} emissiveIntensity={0.6} />
              {ui.showClocks && (
                <Html
                  position={[0, labelYOffset, 0]}
                  center
                  style={{ pointerEvents: 'none' }}
                >
                  <div className={`clock ${isSelected ? 'clock--expanded' : ''}`}>
                    <div className="clock-title">{c.name}</div>
                    {isSelected && (
                      <>
                        <div className="clock-row">t: {frame.t_s.toFixed(1)} s</div>
                        <div className="clock-row">
                          τ:{" "}
                          {c.proper_time_s === undefined || c.proper_time_s === null
                            ? "—"
                            : `${c.proper_time_s.toFixed(3)} s`}
                        </div>
                        <div className="clock-row">
                          rate:{" "}
                          {c.time_dilation_factor === undefined || c.time_dilation_factor === null
                            ? "—"
                            : `${c.time_dilation_factor.toFixed(9)}×`}
                        </div>
                      </>
                    )}
                  </div>
                </Html>
              )}
            </mesh>
          );
        })}

        <OrbitControls
          ref={controlsRef as unknown as React.RefObject<any>}
          enablePan
          enableRotate
          enableZoom
          makeDefault
        />

        <HudProbe onUpdate={setHud} />
      </Canvas>

      <div className="hud">
        <div className="hud-card">
          <div className="hud-title">Legend</div>
          <div className="hud-row">
            <span className="swatch" style={{ background: "#60a5fa" }} /> Flat trail
          </div>
          <div className="hud-row">
            <span className="swatch" style={{ background: "#fb923c" }} /> Relativity overlay
          </div>
          <div className="hud-row muted">
            Axes: {ui.showReferenceAxes ? "on" : "off"} · Planes:{" "}
            {ui.showOrbitalPlanes || ui.showEclipticGrid || ui.showInertialPlane ? "on" : "off"} · Clocks:{" "}
            {ui.showClocks ? "on" : "off"}
          </div>
        </div>

        {rulerMeters !== null && rulerMeters > 0 && (
          <div className="hud-card">
            <div className="hud-title">Scale</div>
            <div className="ruler">
              <div className="ruler-line" />
              <div className="ruler-label">{formatDistanceMeters(rulerMeters)}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

