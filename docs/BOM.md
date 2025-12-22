# Bill of Materials (Placeholder)

**Status**: Conceptual / Research Phase  
**Purpose**: Rough mass and power budget estimates for a space-hardenable inertial/gravity sensing payload  
**Disclaimer**: All entries are generic placeholders. No vendor part numbers. Assumptions clearly marked.

## Payload Concept

A modular payload for precision inertial and gravitational measurements, suitable for deep space or high-altitude missions. Core components: atom interferometer, precision IMU, timing system, data handling.

## Component Categories

### 1. Atom Interferometer Assembly

| Component | Type | Mass (kg) | Power (W) | Notes |
|-----------|------|-----------|-----------|-------|
| Laser system | Custom | 5-10 | 20-50 | Diode-pumped, frequency-stabilized |
| Vacuum chamber | Custom | 3-5 | 5-10 | Ultra-high vacuum, magnetic shielding |
| Atom source | Custom | 1-2 | 2-5 | Cold atom source (MOT/optical trap) |
| Detection optics | COTS/Custom | 1-2 | 1-2 | Photodetectors, imaging |
| Control electronics | Custom | 2-3 | 5-10 | FPGA-based control, feedback loops |
| **Subtotal** | | **12-22** | **33-77** | |

**Assumptions**:
- Laser power: 1-5 W optical output
- Vacuum: < 10^-9 Torr
- Atom species: Rubidium-87 (common choice)
- Integration time: 1-10 seconds per measurement

**Risk**: High — requires significant R&D, thermal/vibration sensitivity

### 2. Precision IMU

| Component | Type | Mass (kg) | Power (W) | Notes |
|-----------|------|-----------|-----------|-------|
| Accelerometer triad | COTS | 0.5-1.0 | 1-2 | Navigation-grade (e.g., Honeywell, Northrop) |
| Gyroscope triad | COTS | 0.5-1.0 | 1-2 | Fiber-optic or MEMS |
| Electronics | COTS/Custom | 0.5-1.0 | 2-3 | Data acquisition, filtering |
| **Subtotal** | | **1.5-3.0** | **4-7** | |

**Assumptions**:
- Bias stability: < 1 µg (accelerometer), < 0.01 deg/hr (gyro)
- Update rate: 100-1000 Hz
- Interface: SPI/I2C

**Risk**: Medium — COTS available, but space-qualified versions expensive

### 3. Timing System

| Component | Type | Mass (kg) | Power (W) | Notes |
|-----------|------|-----------|-----------|-------|
| Atomic clock | COTS | 2-5 | 5-15 | Rubidium or cesium (space-qualified) |
| Distribution | Custom | 0.5-1.0 | 1-2 | Clock distribution, synchronization |
| **Subtotal** | | **2.5-6.0** | **6-17** | |

**Assumptions**:
- Stability: < 10^-12 (short-term), < 10^-11 (long-term)
- May be shared with spacecraft bus

**Risk**: Low-Medium — COTS space clocks available

### 4. Data Handling

| Component | Type | Mass (kg) | Power (W) | Notes |
|-----------|------|-----------|-----------|-------|
| Onboard computer | COTS/Custom | 1-2 | 5-10 | Radiation-hardened processor |
| Storage | COTS | 0.5-1.0 | 2-3 | Solid-state, radiation-tolerant |
| Interfaces | Custom | 0.5-1.0 | 1-2 | Spacecraft bus interface |
| **Subtotal** | | **2.0-4.0** | **8-15** | |

**Assumptions**:
- Processing: Real-time filtering, compression
- Storage: 100+ GB for mission duration

**Risk**: Low — standard space avionics

### 5. Thermal Control

| Component | Type | Mass (kg) | Power (W) | Notes |
|-----------|------|-----------|-----------|-------|
| Heaters | COTS | 0.5-1.0 | 5-20 | Variable (depends on orbit) |
| Insulation | COTS | 1-2 | 0 | MLI blankets |
| Radiators | Custom | 1-2 | 0 | Passive cooling |
| **Subtotal** | | **2.5-5.0** | **5-20** | |

**Assumptions**:
- Operating temp: -40°C to +60°C (electronics), tighter for interferometer
- Thermal stability: < 0.1°C for interferometer

**Risk**: Medium — tight requirements for interferometer

### 6. Structure and Harness

| Component | Type | Mass (kg) | Power (W) | Notes |
|-----------|------|-----------|-----------|-------|
| Structure | Custom | 3-5 | 0 | Aluminum or composite |
| Harness | Custom | 1-2 | 0 | Cabling, connectors |
| **Subtotal** | | **4.0-7.0** | **0** | |

**Risk**: Low — standard spacecraft structures

## Total Budget Summary

| Category | Mass (kg) | Power (W) |
|----------|-----------|-----------|
| Atom Interferometer | 12-22 | 33-77 |
| IMU | 1.5-3.0 | 4-7 |
| Timing | 2.5-6.0 | 6-17 |
| Data Handling | 2.0-4.0 | 8-15 |
| Thermal | 2.5-5.0 | 5-20 |
| Structure | 4.0-7.0 | 0 |
| **Total** | **24.5-47.0** | **56-136** |

**Contingency** (30%): +7-14 kg, +17-41 W

## Custom vs COTS

- **Custom**: Atom interferometer (laser, vacuum, atom source), control electronics, some structure
- **COTS**: IMU sensors, atomic clock, computer, storage, thermal components
- **Depends on Mission**: Radiation shielding, redundancy level, interface standards

## Key Risks

See [RISK_REGISTER.md](RISK_REGISTER.md) for detailed risk analysis.

1. **Vacuum stability**: Leaks, outgassing
2. **Thermal**: Stability requirements for interferometer
3. **Vibration**: Isolation from spacecraft disturbances
4. **Radiation**: Single-event upsets, total dose
5. **Laser stability**: Frequency drift, power fluctuations
6. **Packaging**: Size constraints, integration complexity
7. **Calibration**: On-orbit calibration procedures
8. **Data downlink**: Bandwidth for high-rate measurements

## Notes

- Mass/power are rough estimates based on literature and similar missions
- Actual values depend on mission requirements, orbit, lifetime
- This BOM is for a single payload unit; constellation missions would multiply costs
- No launch costs, integration costs, or ground support equipment included

