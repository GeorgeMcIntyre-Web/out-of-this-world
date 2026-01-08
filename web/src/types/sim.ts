export type Vec3 = [number, number, number];
export type Quat = [number, number, number, number];

export type BodyKind = "star" | "planet" | "moon" | "bh" | "probe";

export type BodySnapshot = {
  id: string;
  name: string;
  kind: BodyKind;
  position_m: Vec3;
  radius_m: number;
  color?: string;
};

export type SensorReading = {
  id: string;
  kind: string;
  value: Record<string, number>;
};

export type CraftSnapshot = {
  id: string;
  name: string;
  position_m: Vec3;
  velocity_mps: Vec3;
  attitude_quat: Quat;
  sensors: SensorReading[];
};

export type Frame = {
  t_s: number;
  bodies: BodySnapshot[];
  craft: CraftSnapshot[];
  events: Record<string, unknown>[];
};

