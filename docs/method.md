# Mathematical Methods

This document specifies the state vector, dynamics equations, measurement models, and estimation algorithms used in the quantum IMU navigation framework.

## State Vector

The navigation filter maintains a 15-dimensional error-state vector:

```
δx = [δp, δv, δθ, δb_a, δb_ω]ᵀ ∈ ℝ¹⁵
```

| State | Dimension | Description | Units |
|-------|-----------|-------------|-------|
| δp | 3 | Position error | m |
| δv | 3 | Velocity error | m/s |
| δθ | 3 | Attitude error (small angle) | rad |
| δb_a | 3 | Accelerometer bias error | m/s² |
| δb_ω | 3 | Gyroscope bias error | rad/s |

The true state is recovered as:
```
p = p̂ + δp
v = v̂ + δv
C = (I - [δθ×]) · Ĉ
b_a = b̂_a + δb_a
b_ω = b̂_ω + δb_ω
```

Where `Ĉ` is the estimated rotation matrix and `[δθ×]` is the skew-symmetric matrix of δθ.

## Coordinate Frames

- **Inertial (i)**: Earth-centered inertial frame
- **Body (b)**: Spacecraft body frame, aligned with IMU axes
- **Navigation (n)**: For deep-space, equivalent to inertial frame

## Dynamics Model

### Orbital Mechanics

Two-body gravitational acceleration:
```
a_grav = -μ · r / ||r||³
```

Where μ = GM is the gravitational parameter.

### IMU Mechanization

The IMU provides measurements of specific force and angular velocity:

**Accelerometer**:
```
ã = a_true + b_a + n_a
```

**Gyroscope**:
```
ω̃ = ω_true + b_ω + n_ω
```

### State Propagation (Nonlinear)

Position:
```
ṗ = v
```

Velocity:
```
v̇ = C_b^n · (ã - b̂_a) + g(p)
```

Attitude (quaternion):
```
q̇ = ½ · q ⊗ [0, ω̃ - b̂_ω]ᵀ
```

### Error-State Dynamics (Linearized)

The error-state propagation follows:

```
δẋ = F · δx + G · w
```

Where the system matrix F is:

```
F = | 0₃   I₃   0₃  0₃   0₃  |
    | G    0₃  -C·[ã×] -C  0₃  |
    | 0₃   0₃   0₃  0₃  -I₃ |
    | 0₃   0₃   0₃  0₃   0₃  |
    | 0₃   0₃   0₃  0₃   0₃  |
```

Where:
- G = ∂g/∂p is the gravity gradient
- C is the body-to-nav rotation matrix
- [ã×] is the skew-symmetric cross-product matrix

The process noise matrix:
```
Q = diag(0, 0, 0, σ²_na, σ²_na, σ²_na, σ²_nω, σ²_nω, σ²_nω, σ²_ba, σ²_ba, σ²_ba, σ²_bω, σ²_bω, σ²_bω)
```

## Measurement Models

### Star Tracker

The star tracker provides attitude measurements in the inertial frame:

**Measurement**:
```
z_st = θ_measured = θ_true + n_st
```

Where n_st ~ N(0, R_st) with typical accuracy 1-10 arcsec (1σ).

**Measurement Matrix** (for attitude error states):
```
H_st = [0₃ₓ₃, 0₃ₓ₃, I₃, 0₃ₓ₃, 0₃ₓ₃]
```

**Measurement Covariance**:
```
R_st = σ²_st · I₃
```

## Extended Kalman Filter

### Prediction Step

1. Propagate nominal state using IMU:
   ```
   p̂(k+1) = p̂(k) + v̂(k)·Δt + ½·â·Δt²
   v̂(k+1) = v̂(k) + â·Δt
   q̂(k+1) = q̂(k) ⊗ δq(ω̂·Δt)
   ```

2. Propagate error covariance:
   ```
   P(k+1|k) = Φ · P(k|k) · Φᵀ + Q_d
   ```

   Where Φ = exp(F·Δt) ≈ I + F·Δt for small Δt.

### Update Step

When a measurement z is available:

1. Compute Kalman gain:
   ```
   K = P(k|k-1) · Hᵀ · (H · P(k|k-1) · Hᵀ + R)⁻¹
   ```

2. Compute innovation:
   ```
   y = z - h(x̂)
   ```

3. Update error state:
   ```
   δx = K · y
   ```

4. Correct nominal state:
   ```
   x̂ ← x̂ ⊕ δx
   ```

5. Update covariance:
   ```
   P(k|k) = (I - K·H) · P(k|k-1)
   ```

## Error Growth Analysis

### Inertial-Only (COAST) Error Growth

Under constant accelerometer bias b_a, position error grows as:
```
δp(t) ≈ ½ · b_a · t²
```

For bias instability (random walk), RMS position error:
```
δp_rms(t) ∝ t^(5/2)
```

### With Updates

Steady-state position error bounded by:
```
δp_ss ≈ σ_st · v · T_update
```

Where T_update is the update interval.

## Numerics

### Integration Method

RK4 (Runge-Kutta 4th order) for orbital dynamics:
```
k1 = f(t, y)
k2 = f(t + Δt/2, y + Δt·k1/2)
k3 = f(t + Δt/2, y + Δt·k2/2)
k4 = f(t + Δt, y + Δt·k3)
y(t+Δt) = y(t) + Δt·(k1 + 2k2 + 2k3 + k4)/6
```

### Numerical Stability

- Joseph form for covariance update: P = (I-KH)P(I-KH)ᵀ + KRKᵀ
- Quaternion normalization after each update
- Symmetric positive-definite enforcement: P = (P + Pᵀ)/2

## Simplifications in This Implementation

1. **Flat Earth approximation**: Gravity gradient ignored (valid for short simulations)
2. **Small angle attitude errors**: δθ << 1 rad assumed
3. **No Earth rotation**: Inertial frame = navigation frame
4. **Discrete-time filter**: Continuous dynamics discretized with Δt
