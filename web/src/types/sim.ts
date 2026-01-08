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
  schwarzschild_radius_m?: number | null;
  time_dilation_factor_at_surface?: number | null;
  time_dilation_surface?: number | null;
  potential_phi?: number | null;
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
  proper_time_s?: number | null;
  time_dilation_factor?: number | null;
  potential_phi?: number | null;
};

export type Frame = {
  t_s: number;
  bodies: BodySnapshot[];
  craft: CraftSnapshot[];
  events: Record<string, unknown>[];
};

