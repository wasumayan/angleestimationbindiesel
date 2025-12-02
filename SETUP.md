# Setup Guide for Bin Diesel Project

Simple setup instructions for the Bin Diesel wake word + flag detection system.

## Prerequisites

- Raspberry Pi (Zero, 3, 4, or 5)
- Raspberry Pi Camera Module 3 Wide (or compatible camera)
- Microphone (USB or built-in)
- PSoC connected via serial (optional, for car control)

## Installation

### 1. Install Dependencies

Run the automated installation script:

```bash
chmod +x install_dependencies.sh
./install_dependencies.sh
```

Or install manually:

```bash
# System packages (includes libcamera support)
sudo apt-get update
sudo apt-get install -y python3-pip python3-opencv libopencv-dev \
    portaudio19-dev python3-pyaudio python3-numpy python3-serial \
    libcamera-apps v4l-utils

# Python packages
pip3 install --break-system-packages -r requirements.txt
```

### 1.5. Enable Camera (Raspberry Pi)

Enable the camera interface:

```bash
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
# Reboot after enabling
```

Test libcamera:

```bash
libcamera-hello
# Should show camera preview for 5 seconds
```

### 2. Get Picovoice AccessKey

1. Sign up at [Picovoice Console](https://console.picovoice.ai/)
2. Get your free AccessKey
3. Set it as an environment variable:

```bash
export PICOVOICE_ACCESS_KEY='your-access-key-here'
```

To make it permanent, add to `~/.bashrc`:

```bash
echo 'export PICOVOICE_ACCESS_KEY="your-access-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### 3. Verify Wake Word File

Make sure the custom wake word file is in place:

```bash
ls bin-diesel_en_raspberry-pi_v3_0_0/bin-diesel_en_raspberry-pi_v3_0_0.ppn
```

If missing, download it from [Picovoice Console](https://console.picovoice.ai/) after creating a custom "bin diesel" wake word.

### 4. Run the System

```bash
python3 bindieselsimple.py
```

## How It Works

1. **Wake Word Detection**: Uses Picovoice Porcupine to detect "bin diesel"
2. **Flag Detection**: Once wake word is detected, camera starts looking for a red colored flag
3. **Angle Calculation**: Calculates angle of flag relative to car center (using 102° FOV for Camera Module 3 Wide)
4. **PSoC Communication**: Sends angle to PSoC for car control

## Configuration

### Change Flag Color

Edit `bindieselsimple.py`:

```python
flag_detector = ColorFlagDetector(color='green', camera_index=0)  # Change 'red' to 'green', 'blue', or 'yellow'
```

### Change Camera Index

```python
flag_detector = ColorFlagDetector(color='red', camera_index=1)  # Use camera index 1 instead of 0
```

### Change PSoC Port

Edit `bindieselsimple.py`:

```python
psoc = PSoCCommunicator(port='/dev/ttyACM0', baudrate=115200)  # Change port if needed
```

## Troubleshooting

### "PICOVOICE_ACCESS_KEY environment variable not set"

**Solution**: Set the AccessKey:
```bash
export PICOVOICE_ACCESS_KEY='your-key-here'
```

### "Wake word file not found"

**Solution**: Make sure the `bin-diesel_en_raspberry-pi_v3_0_0` folder is in the project directory.

### "Could not open camera"

**Solutions**:
1. Enable camera: `sudo raspi-config` → Interface Options → Camera → Enable (then reboot)
2. Test libcamera: `libcamera-hello` (should show preview)
3. Check permissions: `sudo usermod -a -G video $USER` (then logout/login)
4. Check video devices: `ls /dev/video*` (should show /dev/video0 or similar)
5. Check camera detection: `vcgencmd get_camera` (should show supported=1 detected=1)
6. Verify libcamera: `libcamera-hello --list-cameras` (lists available cameras)

### "Error opening microphone"

**Solutions**:
1. Check microphone: `arecord -l`
2. Check permissions: `sudo usermod -a -G audio $USER` (then logout/login)
3. Test microphone: `arecord -d 5 test.wav && aplay test.wav`

### "Could not connect to PSoC"

**Solutions**:
1. Check serial port: `ls /dev/tty*`
2. Update port in code if different from `/dev/ttyUSB0`
3. Check permissions: `sudo usermod -a -G dialout $USER` (then logout/login)

## Files

- `bindieselsimple.py` - Main program
- `camerasimple.py` - Camera test tool (for testing flag detection)
- `psoc_communicator.py` - PSoC communication module
- `requirements.txt` - Python dependencies
- `install_dependencies.sh` - Automated installation script

## Resources

- [Picovoice Porcupine Documentation](https://picovoice.ai/docs/quick-start/porcupine-python/)
- [Picovoice Console](https://console.picovoice.ai/)
- [Porcupine GitHub](https://github.com/Picovoice/porcupine)

