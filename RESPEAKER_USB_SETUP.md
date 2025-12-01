# ReSpeaker Lite USB Setup for Raspberry Pi 4

Based on: https://wiki.seeedstudio.com/respeaker_lite_pi5/ (adapted for Pi 4)

## Quick Setup for Voice Commands

### 1. Install Required Libraries

```bash
sudo apt update
sudo apt install python3-pip python3-dev
sudo apt install portaudio19-dev
pip3 install pyaudio
pip3 install SpeechRecognition
```

### 2. Configure ReSpeaker for Raspberry Pi 4

**Note**: Pi 4 uses ALSA (not PipeWire like Pi 5), so no special configuration needed!

The ReSpeaker should work out of the box. Just verify it's detected:

```bash
# Check if ReSpeaker is detected
arecord -l
# Should show: ReSpeaker Lite: USB Audio

# Test recording
arecord -D hw:3,0 -f S16_LE -r 16000 -c 2 -d 5 test.wav
aplay test.wav
```

### 3. Adjust Volume

```bash
alsamixer
# Select ReSpeaker device (F6), adjust capture volume
```

### 4. Test ReSpeaker

```bash
# List audio devices
arecord -l
# Should show: ReSpeaker Lite: USB Audio

# Test recording
arecord -D hw:3,0 -f S16_LE -r 16000 -c 2 -d 5 test.wav
aplay test.wav
```

### 5. Verify in Python

```python
import speech_recognition as sr
r = sr.Recognizer()
mic = sr.Microphone()

# List available microphones
for i, microphone_name in enumerate(sr.Microphone.list_microphone_names()):
    print(f"Microphone {i}: {microphone_name}")

# Find ReSpeaker
for i, name in enumerate(sr.Microphone.list_microphone_names()):
    if 'respeaker' in name.lower() or 'seeed' in name.lower():
        print(f"Found ReSpeaker at index {i}: {name}")
        # Use this index when creating Microphone
```

## Using ReSpeaker in Code

The speech recognition library will automatically use the default microphone, which should be the ReSpeaker if it's the only USB audio device. To explicitly use ReSpeaker:

```python
import speech_recognition as sr

r = sr.Recognizer()

# Find ReSpeaker device index
mic_index = None
for i, name in enumerate(sr.Microphone.list_microphone_names()):
    if 'respeaker' in name.lower():
        mic_index = i
        break

# Use ReSpeaker
if mic_index is not None:
    mic = sr.Microphone(device_index=mic_index)
else:
    mic = sr.Microphone()  # Use default

# Now use mic for voice recognition
with mic as source:
    r.adjust_for_ambient_noise(source)
    audio = r.listen(source)
    text = r.recognize_google(audio)
```

## Notes

- **Raspberry Pi 4**: Uses ALSA - no special configuration needed, works out of the box!
- **Raspberry Pi 5**: Would require PipeWire configuration (not applicable here)
- **Sample Rate**: ReSpeaker Lite works at 16kHz
- **Channels**: ReSpeaker provides 2 channels (stereo), speech recognition uses mono (auto-converted)

## Troubleshooting

### ReSpeaker Not Detected
```bash
# Check USB connection
lsusb | grep -i seeed

# Check audio devices
arecord -l

# Check if device is in use
lsof /dev/snd/*
```

### No Audio Input
```bash
# Check volume
alsamixer

# Test recording
arecord -D hw:3,0 -f S16_LE -r 16000 -c 2 -d 5 test.wav
# Check file size
ls -lh test.wav
```

### Speech Recognition Not Working
- Verify microphone is working: `arecord -l` and test recording
- Check permissions: `sudo usermod -a -G audio $USER` (logout/login)
- Test with simple script first

