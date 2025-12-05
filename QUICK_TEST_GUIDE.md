# Quick Testing Guide - Step by Step

Follow this guide to test each component of the Bin Diesel system.

## Prerequisites Check

First, verify your setup:

```bash
# 1. Check if .env file exists and has keys
cat .env
# Should show:
# PICOVOICE_ACCESS_KEY=vVwmRT9zjzQ0UTokr2gLEYe6JpgDd06mfV55a-Gj5rovCZ099RJcA==
# OPENAI_API_KEY=your_key_here

# 2. Check if dependencies are installed
python3 -c "import pvporcupine; print('✓ Picovoice OK')"
python3 -c "import speech_recognition; print('✓ SpeechRecognition OK')"
python3 -c "from ultralytics import YOLO; print('✓ YOLO OK')"
python3 -c "from openai import OpenAI; print('✓ OpenAI OK')"
python3 -c "from picamera2 import Picamera2; print('✓ Picamera2 OK')"

# 3. Check camera
libcamera-hello --list-cameras
```

---

## Test 1: Wake Word Detection ⏱️ ~2 minutes

**What it tests:** Can the system hear "bin diesel"?

**Hardware needed:** Microphone

```bash
python3 test_wake_word.py
```

**What to do:**
1. Wait for: `[WakeWord] Listening for 'bin diesel'...`
2. Say "bin diesel" clearly
3. Should see: `[WakeWord] WAKE WORD DETECTED: 'bin diesel'`
4. Press Ctrl+C to exit

**Expected output:**
```
[WakeWord] Initialized with model: ...
[WakeWord] Listening for 'bin diesel'...
[WakeWord] WAKE WORD DETECTED: 'bin diesel'
✓ Wake word detected! (Count: 1)
```

**Troubleshooting:**
- No detection? Check microphone: `arecord -d 3 test.wav && aplay test.wav`
- Error? Check PICOVOICE_ACCESS_KEY in .env
- Permission error? Check mic permissions

**✅ Pass criteria:** Wake word detected at least 3 times in a row

---

## Test 2: Visual Detection (Person + Arm) ⏱️ ~3 minutes

**What it tests:** Can the camera detect you and your raised arm?

**Hardware needed:** Camera Module 3 Wide

```bash
python3 test_visual_detection.py
```

**What to do:**
1. Window should open showing camera feed
2. Stand in front of camera
3. Raise your arm to the side (90° angle)
4. Should see:
   - Green box around you
   - "ARM RAISED!" text
   - Angle displayed (e.g., "Angle: -15.3°")
5. Press 'd' to toggle debug mode
6. Press 'q' to quit

**Expected output:**
```
[VisualDetector] Camera started: 640x480
[TEST] Person detected: angle=-15.3°, centered=False, arm_raised=True
```

**Troubleshooting:**
- No camera? `libcamera-hello --list-cameras`
- No person detected? Move closer, check lighting
- Arm not detected? Make sure arm is clearly raised to the side
- Slow? Lower resolution in config.py (CAMERA_WIDTH, CAMERA_HEIGHT)

**✅ Pass criteria:** 
- Person detected consistently
- Arm raising detected when you raise arm
- Angle calculated correctly

---

## Test 3: Motor Controller ⏱️ ~1 minute

**What it tests:** Can the motor receive PWM signals?

**Hardware needed:** Motor connected to GPIO 18 (or test in mock mode)

```bash
python3 test_motor.py
```

**What to do:**
1. Watch motor speed change (if connected)
2. Or watch terminal output (mock mode)
3. Should see speed progression: 30% → 50% → 70% → 90% → stop

**Expected output:**
```
[MotorController] Mock mode - GPIO 18 would be used
[TEST] Setting speed to 30% - Slow
[MotorController] Speed set to 30.0% (duty cycle: 30.0%)
[TEST] Setting speed to 50% - Medium
...
[TEST] Motor stopped
```

**Troubleshooting:**
- Motor doesn't move? Check GPIO 18 connection
- Wrong speed? Adjust PWM values in config.py (MOTOR_SLOW, MOTOR_MEDIUM, etc.)
- Permission error? `sudo usermod -a -G gpio $USER` then logout/login

**✅ Pass criteria:** Motor speeds change (or mock output shows correct PWM values)

---

## Test 4: Servo Controller ⏱️ ~1 minute

**What it tests:** Can the servo receive PWM signals for steering?

**Hardware needed:** Servo connected to GPIO 19 (or test in mock mode)

```bash
python3 test_servo.py
```

**What to do:**
1. Watch servo move (if connected)
2. Or watch terminal output (mock mode)
3. Should see: center → left → full left → center → right → full right → center

**Expected output:**
```
[ServoController] Mock mode - GPIO 19 would be used
[TEST] Centering servo...
[TEST] Turning left (25%)...
[ServoController] Position: LEFT 25.0% (duty cycle: 6.88%)
...
[TEST] Centering...
```

**Troubleshooting:**
- Servo doesn't move? Check GPIO 19 connection
- Wrong position? Adjust duty cycle in config.py (SERVO_CENTER, SERVO_LEFT_MAX, etc.)
- Typical servo: 2.5% (0°) to 12.5% (180°)

**✅ Pass criteria:** Servo moves (or mock output shows correct PWM values)

---

## Test 5: TOF Sensor (Distance) ⏱️ ~2 minutes

**What it tests:** Can the distance sensor detect objects?

**Hardware needed:** VL53L0X sensor connected via I2C

```bash
python3 test_tof.py
```

**What to do:**
1. Move your hand toward the sensor
2. Watch distance readings change
3. Should show:
   - `[SAFE]` when > 8cm
   - `[STOP!]` when 7-8cm
   - `[EMERGENCY STOP!]` when < 7cm
4. Press Ctrl+C to exit

**Expected output:**
```
[TOFSensor] VL53L0X initialized
[TEST #1] Distance: 45.2cm (452mm) [SAFE]
[TEST #2] Distance: 8.5cm (85mm) [STOP!]
[TEST #3] Distance: 6.8cm (68mm) [EMERGENCY STOP!]
```

**Troubleshooting:**
- Sensor not found? `i2cdetect -y 1` (should see device at 0x29)
- No I2C? Enable in `sudo raspi-config` → Interface Options → I2C
- Check wiring: SDA to GPIO 2, SCL to GPIO 3

**✅ Pass criteria:** Distance readings change as you move hand, thresholds work correctly

---

## Test 6: Voice Commands (Manual Mode) ⏱️ ~3 minutes

**What it tests:** Can the system understand voice commands?

**Hardware needed:** Microphone + Internet (for OpenAI API)

```bash
python3 test_voice_commands.py
```

**What to do:**
1. Wait for: `[TEST] Waiting for command...`
2. When you see `[VoiceRecognizer] Listening... (speak now)`, say a command:
   - "FORWARD"
   - "LEFT"
   - "RIGHT"
   - "STOP"
   - "TURN AROUND"
3. Should see transcription and recognized command
4. Press Ctrl+C to exit

**Expected output:**
```
[VoiceRecognizer] Listening... (speak now)
[VoiceRecognizer] Transcribed: 'forward'
[VoiceRecognizer] Command recognized: FORWARD
✓ Command: FORWARD
[TEST] Simulating: FORWARD
  → Motor would move forward
```

**Troubleshooting:**
- No API key? Check OPENAI_API_KEY in .env
- Transcription fails? Check internet connection
- Wrong command? Speak clearly, wait for "Listening..." prompt
- Test microphone: `arecord -d 3 test.wav && aplay test.wav`

**✅ Pass criteria:** At least 4 out of 5 commands recognized correctly

---

## Test 7: Full System (Simulation) ⏱️ ~1 minute

**What it tests:** Does the state machine logic work?

**Hardware needed:** None (simulation only)

```bash
python3 test_full_system.py
```

**What to do:**
1. Watch state transitions
2. Should see complete workflow simulation
3. Press Ctrl+C to exit

**Expected output:**
```
[TEST Step 1] State: idle (time: 0.0s)
[TEST Step 2] State: idle (time: 1.0s)
  → Wake word detected!
[TEST Step 3] State: active (time: 0.0s)
  → Person detected with raised arm (angle: -15.0°)
[TEST Step 4] State: tracking_user (time: 0.0s)
...
```

**✅ Pass criteria:** State machine transitions through all states correctly

---

## Test 8: Full System (Real Hardware) ⏱️ ~10 minutes

**What it tests:** Everything working together

**Hardware needed:** All components connected

```bash
python3 main.py
```

### Autonomous Mode Test:

1. **Say "bin diesel"** → Should see: `[Main] System activated!`
2. **Raise your arm** → Should see: `[Main] Autonomous mode: User detected with raised arm`
3. **Car should start following you** → Watch it move toward you
4. **Move around** → Car should track and follow
5. **Get close (7-8cm)** → Car should stop: `[Main] User reached (TOF sensor), stopping`
6. **Wait 10 seconds** → Car should return to start
7. **Press Ctrl+C** to exit

### Manual Mode Test:

1. **Say "bin diesel"** → System activates
2. **Say "manual mode"** → Should see: `[Main] Manual mode activated`
3. **Say "FORWARD"** → Car moves forward continuously
4. **Say "LEFT"** → Car turns left continuously
5. **Say "STOP"** → Car stops
6. **Say "automatic mode"** → Returns to autonomous mode
7. **Press Ctrl+C** to exit

**Expected output:**
```
[Main] System activated!
[Main] Autonomous mode: User detected with raised arm
[Main] DEBUG: Person angle: -15.3°, centered: False
[Main] DEBUG: Setting servo angle: -15.3° (position: -0.17)
[Main] User reached (TOF sensor), stopping
[Main] Trash collection complete, returning to start
[Main] Returned to start position
```

**Troubleshooting:**
- Check all individual tests pass first
- Enable debug mode in config.py for detailed output
- Check GPIO connections
- Verify all sensors working

**✅ Pass criteria:** 
- Wake word activates system
- Autonomous mode follows user
- Manual mode responds to commands
- System returns to start correctly

---

## Testing Checklist

Use this checklist to track your progress:

- [ ] Test 1: Wake Word Detection
- [ ] Test 2: Visual Detection (Person + Arm)
- [ ] Test 3: Motor Controller
- [ ] Test 4: Servo Controller
- [ ] Test 5: TOF Sensor
- [ ] Test 6: Voice Commands
- [ ] Test 7: Full System (Simulation)
- [ ] Test 8: Full System (Real Hardware)

---

## Quick Reference

**Enable Debug Mode:**
Edit `config.py`:
```python
DEBUG_MODE = True
DEBUG_VISUAL = True
DEBUG_MOTOR = True
DEBUG_SERVO = True
DEBUG_TOF = True
DEBUG_VOICE = True
```

**Common Commands:**
```bash
# Test individual components
python3 test_wake_word.py
python3 test_visual_detection.py
python3 test_voice_commands.py

# Run full system
python3 main.py

# Check camera
libcamera-hello --list-cameras

# Check I2C devices
i2cdetect -y 1
```

---

## Next Steps

Once all tests pass:
1. Calibrate PWM values in `config.py` for your hardware
2. Adjust TOF thresholds if needed
3. Fine-tune camera resolution for performance
4. Test in real-world scenarios
5. Deploy!

