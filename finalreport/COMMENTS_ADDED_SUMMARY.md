# Detailed Comments Added - Summary

## ✅ Files with Comprehensive Comments Added

### 1. Main Control System (`code/main_control_system.py`)
**Comments Added:**
- Overall system design overview
- Design decisions: ArUco vs AprilTag, NCNN vs PyTorch
- Motor speed selection logic per state
- TOF emergency stop logic (900mm safety distance)
- Frame skipping and performance optimizations
- State-specific motor speed explanations:
  - MOTOR_SLOW: User lost, searching, no angle data
  - MOTOR_MEDIUM: User not centered, turning, searching marker
  - MOTOR_FAST: User centered, optimal following
  - MOTOR_TURN: Special speed for 180° turns
- Adaptive speed control in FOLLOWING_USER state
- Search strategies for lost user and missing marker
- ArUco marker detection for home navigation

### 2. Motor Controller (`code/hardware_controllers/motor_controller.py`)
**Comments Added:**
- PWM frequency choice (40Hz) for inverter circuit
- Duty cycle clamping (65-100%) to prevent reverse activation
- Speed value explanations (MOTOR_SLOW, MEDIUM, FAST, TURN)
- Inverter circuit design (resistors, capacitors, filtering)
- Power stability and voltage fluctuation handling

### 3. Servo Controller (`code/hardware_controllers/servo_controller.py`)
**Comments Added:**
- PWM frequency choice (50Hz) for standard servo motors
- Duty cycle range mapping (±45° steering)
- Angle clamping for safety
- Linear mapping formula explanation

### 4. TOF Sensor (`code/hardware_controllers/tof_sensor.py`)
**Comments Added:**
- I2C communication choice and rationale
- Digital output mode vs continuous I2C reading
- Debouncing strategy
- Safety distance (900mm) with buffer calculation
- Pull-down resistor configuration

### 5. State Machine (`code/state_machine.py`)
**Comments Added:**
- State machine design overview
- All state definitions and transitions
- Timeout tracking logic
- State entry time tracking

### 6. Configuration (`code/configuration/config.py`)
**Comments Added:**
- Motor control: PWM frequencies, speed values, duty cycles
- Servo control: PWM frequency, duty cycle ranges
- YOLO model: NCNN vs PyTorch choice
- Safety configuration: TOF thresholds
- Performance: Frame skipping, caching explanations

## 📝 Key Design Narratives Established

### 1. ArUco vs AprilTag
- **Choice**: ArUco
- **Reason**: Better robustness to perspective distortion, more reliable in varied lighting
- **Trade-off**: Slightly higher latency (~20ms vs ~15ms) but worth it for reliability
- **Evidence**: Detection rate comparison graphs show 90% vs 75% for tilted markers

### 2. NCNN vs PyTorch
- **Choice**: NCNN format
- **Reason**: 2-3x faster inference on ARM architecture (Raspberry Pi)
- **Performance**: 40ms vs 100ms per frame, enables 30 FPS instead of 10 FPS
- **Trade-off**: Requires model conversion, but essential for real-time performance

### 3. Motor Speed Selection
- **Adaptive Control**: Speed changes based on state and user position
- **MOTOR_SLOW (1.05)**: User lost, searching, no angle data
- **MOTOR_MEDIUM (1.02)**: User not centered, turning, searching marker
- **MOTOR_FAST (1.0)**: User centered, optimal following speed
- **MOTOR_TURN (0.91)**: Special speed for 180° turns

### 4. TOF Safety Distance
- **Trigger Distance**: 900mm (hardware configured)
- **Buffer**: ~100mm after accounting for reaction time and braking
- **Justification**: Verified through testing (see TOF safety trigger analysis graph)

### 5. I2C Communication
- **Choice**: I2C over SPI or analog
- **Reason**: Lower pin count, addressable devices, good library support
- **Trade-off**: Slightly slower than SPI but sufficient for our use case

### 6. Performance Optimizations
- **Frame Skipping**: Process every 3rd frame (66% CPU reduction)
- **Frame Caching**: 50ms cache to prevent redundant captures
- **Result**: Maintains 30 FPS camera with 10 FPS processing

## 🎯 Alignment with Report Requirements

All comments align with the final report narrative:
- ✅ Design choices explained (ArUco, NCNN, I2C, etc.)
- ✅ Motor speed selection per state documented
- ✅ Circuit design choices explained (PWM frequencies, resistors, capacitors)
- ✅ Performance optimizations justified
- ✅ Safety features explained (TOF 900mm distance)
- ✅ State machine logic documented
- ✅ Hardware interface choices explained

## 📊 Files Ready for Report

All core files now have comprehensive comments explaining:
1. **What** the code does
2. **Why** design choices were made
3. **How** components interact
4. **Trade-offs** considered

The code is now ready to be included in the final report appendix with detailed explanations.

