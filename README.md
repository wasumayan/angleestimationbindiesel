# ReSpeaker Direction Estimation for Car Steering Control

This project implements a sound source direction estimation system using a ReSpeaker Lite 2-mic array, which estimates the angle of incoming sound and sends steering commands to a PSoC for servo control.

## System Overview

```
ReSpeaker Mic Array → Raspberry Pi 4 → Signal Processing → Angle Estimation → PSoC → PWM → Servo
```

1. **Audio Capture**: ReSpeaker Lite captures stereo audio from 2-microphone array
2. **Direction Estimation**: Raspberry Pi processes audio using TDOA (Time Difference of Arrival) to estimate sound source angle
3. **Angle Transmission**: Estimated angle is sent to PSoC via UART/Serial
4. **Servo Control**: PSoC generates PWM signal to control steering servo

## Hardware Requirements

- ReSpeaker Lite (2-mic array) - USB connected
- Raspberry Pi 4
- PSoC (for PWM generation)
- Servo motor for steering
- USB-to-Serial adapter (if PSoC doesn't have direct USB serial)

## Software Requirements

- Python 3.7+
- Raspberry Pi OS (or compatible Linux distribution)

## Installation

1. **Install system dependencies** (on Raspberry Pi):
```bash
sudo apt-get update
sudo apt-get install -y python3-pip portaudio19-dev python3-pyaudio
```

2. **Install Python packages**:
```bash
pip3 install -r requirements.txt
```

3. **Verify audio device**:
```bash
# List audio devices
python3 -c "import pyaudio; p = pyaudio.PyAudio(); [print(f'{i}: {p.get_device_info_by_index(i)[\"name\"]}') for i in range(p.get_device_count())]"
```

4. **Find PSoC serial port**:
```bash
# List serial ports
python3 main.py --list-ports

# Or manually check
ls /dev/ttyUSB* /dev/ttyACM*
```

## Usage

### Basic Usage

```bash
python3 main.py
```

### With Custom Settings

```bash
python3 main.py --port /dev/ttyACM0 --baudrate 115200 --update-rate 10
```

### Command Line Arguments

- `--port`: Serial port for PSoC communication (default: `/dev/ttyUSB0`)
- `--baudrate`: Serial baud rate (default: `115200`)
- `--sample-rate`: Audio sample rate in Hz (default: `16000`)
- `--update-rate`: Control loop update rate in Hz (default: `10.0`)
- `--list-ports`: List available serial ports and exit

## Configuration

### Microphone Spacing

The default microphone spacing is set to 4cm (0.04m). If your ReSpeaker has a different spacing, modify `direction_estimator.py`:

```python
self.direction_estimator = DirectionEstimator(mic_spacing=0.04)  # Adjust as needed
```

### Angle Range

The system estimates angles from -90° to +90°:
- **Positive angles**: Sound source from the right
- **Negative angles**: Sound source from the left
- **0°**: Sound source directly ahead

### PSoC Communication Protocol

Two protocols are available:

1. **Simple Text Protocol** (default):
   - Format: `ANGLE:XX.XX\n`
   - Example: `ANGLE:45.23\n`

2. **Binary Protocol**:
   - Format: `[0xAA header byte][float32 angle]`
   - Use `send_angle()` instead of `send_angle_simple()` in `main.py`

## PSoC Code Requirements

Your PSoC should:
1. Receive angle data via UART at the configured baud rate
2. Parse the angle value (either text or binary format)
3. Convert angle to appropriate PWM duty cycle for servo
4. Output PWM signal to servo control pin

### Example PSoC Pseudocode:
```
- Initialize UART at 115200 baud
- Initialize PWM for servo control
- Loop:
  - Read angle from UART
  - Map angle (-90 to +90) to PWM duty cycle (e.g., 1ms to 2ms pulse width)
  - Update PWM output
```

## Troubleshooting

### Audio Device Not Found
- Check USB connection: `lsusb`
- Verify device appears in audio list
- Try specifying device index manually in `audio_capture.py`

### No Angle Estimates
- Check microphone levels: speak near the microphones
- Adjust threshold in `direction_estimator.py` (lower for more sensitivity)
- Verify both microphones are working (check stereo channels)

### PSoC Communication Issues
- Verify serial port: `python3 main.py --list-ports`
- Check baud rate matches PSoC configuration
- Verify wiring (TX from Pi to RX on PSoC, GND connected)
- Check permissions: `sudo usermod -a -G dialout $USER` (may need to logout/login)

### Poor Direction Accuracy
- Ensure microphones are properly spaced and aligned
- Reduce background noise
- Increase smoothing window size in `direction_estimator.py`
- Verify microphone spacing constant matches hardware

## Project Structure

```
.
├── main.py                 # Main control script
├── audio_capture.py        # ReSpeaker audio capture module
├── direction_estimator.py  # TDOA-based direction estimation
├── psoc_communicator.py   # PSoC serial communication
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Technical Details

### Direction Estimation Algorithm

The system uses **Time Difference of Arrival (TDOA)** method:

1. Cross-correlation between left and right microphone signals
2. Find time delay (which microphone received sound first)
3. Convert delay to angle using formula:
   ```
   sin(angle) = (delay_time × speed_of_sound) / microphone_spacing
   ```

### Signal Processing

- **Sample Rate**: 16 kHz (configurable)
- **Chunk Size**: 1024 samples
- **Smoothing**: Moving median filter over last 10 estimates
- **Threshold**: Minimum correlation peak of 0.3 for valid detection

## License

This project is for educational/research purposes.

## Notes

- The system assumes the microphone array is mounted on the car facing forward
- Angle 0° corresponds to sound directly ahead
- Positive angles indicate sound from the right side (car should turn right)
- The PSoC should handle the mapping from angle to servo PWM duty cycle based on your servo specifications

