/**
 * TypeScript types for simulation API
 */

export interface TrajectoryPoint {
  x: number;
  y: number;
  z: number;
}

export interface ExperimentResult {
  name: string;
  imu_profile: string;
  final_pos_error_m: number;
  final_vel_error_m_s: number;
  max_pos_error_m: number;
  n_updates: number;
  time_s: number[];
  pos_error_m: number[];
  vel_error_m_s: number[];
  pos_sigma_m: number[];
  true_position: TrajectoryPoint[];
  est_position: TrajectoryPoint[];
}

export interface RunRequest {
  imu_profile: "classical" | "quantum";
  scenario: "coast" | "updates" | "compare";
  duration_hours: number;
  update_interval: number;
  seed: number;
}

export interface RunResponse {
  id: string;
  experiments: ExperimentResult[];
  improvement_factor: number | null;
}

export interface ProfileInfo {
  name: string;
  description: string;
  accel_bias_instability_ug: number;
  gyro_bias_instability_deg_h: number;
}

export interface ScenarioInfo {
  name: string;
  description: string;
}

export type SimulationStatus = "idle" | "running" | "complete" | "error";
