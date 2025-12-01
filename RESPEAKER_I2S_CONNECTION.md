# ReSpeaker Lite I2S Connection to Raspberry Pi GPIO

## Overview

Connecting ReSpeaker Lite via I2S gives you access to **raw microphone channels** (not processed mono), which is what you need for TDOA direction estimation.

## Step 1: Flash I2S Firmware

First, you need to flash I2S firmware instead of USB firmware:

```bash
cd ~/Downloads/ReSpeaker_Lite/xmos_firmwares

# Enter DFU mode (same as before):
# 1. Unplug USB
# 2. Hold button
# 3. Plug in USB while holding
# 4. Release button

# Flash I2S firmware
sudo dfu-util -R -e -a 1 -D respeaker_lite_i2s_dfu_firmware_v1.0.9.bin

# Unplug and replug
```

## Step 2: GPIO Pin Connections

Connect ReSpeaker Lite to Raspberry Pi GPIO pins:

### ReSpeaker Lite I2S Pins → Raspberry Pi GPIO

| ReSpeaker Pin | Function | Raspberry Pi GPIO | Physical Pin |
|---------------|----------|-------------------|--------------|
| **BCLK** | Bit Clock | GPIO 18 (PWM0) | Pin 12 |
| **LRCLK** | Left/Right Clock | GPIO 19 (PCM_FS) | Pin 35 |
| **DIN** | Data In (to Pi) | GPIO 20 (PCM_DIN) | Pin 38 |
| **DOUT** | Data Out (from Pi) | GPIO 21 (PCM_DOUT) | Pin 40 |
| **3.3V** | Power | 3.3V | Pin 1 or 17 |
| **GND** | Ground | GND | Pin 6, 9, 14, 20, 25, 30, 34, or 39 |

### Pin Layout Reference

```
Raspberry Pi GPIO (looking at board):
    3.3V  [1]  [2]  5V
  GPIO 2  [3]  [4]  5V
  GPIO 3  [5]  [6]  GND
  GPIO 4  [7]  [8]  GPIO 14
      GND [9]  [10] GPIO 15
 GPIO 17 [11] [12] GPIO 18 (BCLK) ← Connect here
 GPIO 27 [13] [14] GND
 GPIO 22 [15] [16] GPIO 23
    3.3V [17] [18] GPIO 24
 GPIO 10 [19] [20] GND
  GPIO 9 [21] [22] GPIO 25
 GPIO 11 [23] [24] GPIO 8
      GND [25] [26] GPIO 7
  GPIO 0 [27] [28] GPIO 1
  GPIO 5 [29] [30] GND
  GPIO 6 [31] [32] GPIO 12
 GPIO 13 [33] [34] GND
 GPIO 19 [35] [36] GPIO 16  ← LRCLK here
 GPIO 26 [37] [38] GPIO 20  ← DIN here
      GND [39] [40] GPIO 21  ← DOUT here
```

## Step 3: Enable I2S on Raspberry Pi

```bash
# Edit config file
sudo nano /boot/config.txt

# Add these lines (if not already present):
dtoverlay=i2s-mmap
dtoverlay=googlevoicehat-soundcard

# Or for simpler setup, just:
dtoverlay=i2s-mmap

# Save and reboot
sudo reboot
```

## Step 4: Verify I2S Connection

After reboot, check if I2S is enabled:

```bash
# Check if I2S device appears
arecord -l

# Should show something like:
# card 1: ReSpeaker [ReSpeaker], device 0: I2S [I2S]
```

## Step 5: Test I2S Audio Capture

```bash
# Record from I2S
arecord -D hw:1,0 -f S16_LE -r 16000 -c 2 -d 5 test_i2s.wav

# Check if channels are different (they should be now!)
python3 test_stereo_recording.py
```

## Alternative Pin Connections (if above doesn't work)

Some configurations use different pins. Try this if the above doesn't work:

| ReSpeaker Pin | Raspberry Pi GPIO | Physical Pin |
|---------------|-------------------|--------------|
| BCLK | GPIO 18 | Pin 12 |
| LRCLK | GPIO 19 | Pin 35 |
| DIN | GPIO 20 | Pin 38 |
| DOUT | GPIO 21 | Pin 40 |

Or check ReSpeaker Lite documentation for specific pin assignments.

## Troubleshooting

### No Audio Device Found
- Check GPIO connections
- Verify I2S is enabled: `lsmod | grep snd_soc`
- Check dmesg: `dmesg | tail`

### Still Getting Mono Audio
- Verify I2S firmware is flashed (not USB firmware)
- Check that you're using I2S device, not USB device
- Test with: `arecord -D hw:1,0 ...` (not hw:3,0)

### I2S Not Working
- Verify pin connections with multimeter
- Check for loose connections
- Try different GPIO pins if needed
- Check ReSpeaker Lite documentation for pinout

## Power Considerations

- ReSpeaker Lite needs 3.3V power
- Can draw power from Pi GPIO 3.3V pin
- If power issues occur, use external 3.3V supply

## Next Steps

Once I2S is working and you have stereo channels:
1. Test with `test_tdoa_simple.py` - should now show different channels!
2. Run `test_angles.py` - should show non-zero angles
3. Use the TDOA system for direction estimation

