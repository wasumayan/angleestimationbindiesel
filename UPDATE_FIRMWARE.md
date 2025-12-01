# ReSpeaker Lite Firmware Update Guide

## Problem Confirmed

Your ReSpeaker Lite is outputting **mono audio to both channels**:
- File format: Stereo (2 channels) ✓
- Actual content: Identical on both channels ✗
- Correlation: 1.000000 (perfectly identical)

This prevents TDOA from working because there's no time difference to measure.

## Solution: Update USB Firmware

The device needs **USB firmware v2.0.7** (or at least v2.0.5+) to properly output stereo channels.

## Step-by-Step Update Process

### 1. Install dfu-util

```bash
sudo apt-get update
sudo apt-get install dfu-util
```

### 2. Download USB Firmware

Download the latest USB firmware from:
- **GitHub**: https://github.com/respeaker/ReSpeaker_Lite/tree/master/xmos_firmwares
- **Direct link** (if available): Look for `respeaker_lite_usb_v2.0.7.bin` or similar

You can download it on your Pi:
```bash
cd ~/Downloads
# Use wget or curl to download the firmware file
# Example (check actual URL):
wget https://github.com/respeaker/ReSpeaker_Lite/raw/master/xmos_firmwares/respeaker_lite_usb_v2.0.7.bin
```

### 3. Enter DFU Mode

**Important**: The device must be in DFU (Device Firmware Update) mode to flash firmware.

Steps:
1. **Unplug** the USB cable from ReSpeaker Lite
2. **Hold down** the button on the ReSpeaker Lite (check device documentation for which button - usually there's a reset or boot button)
3. **While holding the button**, plug in the USB cable
4. **Release** the button after 2-3 seconds
5. The device should now be in DFU mode

**Verify DFU mode**:
```bash
dfu-util -l
```

You should see something like:
```
Found DFU: [2886:0019] ver=xxxx, devnum=xx, cfg=1, intf=0, alt=0, name="XMOS DFU"
```

If you don't see this, the device is not in DFU mode. Try the steps again.

### 4. Flash the Firmware

Once in DFU mode:

```bash
# Navigate to where you downloaded the firmware
cd ~/Downloads

# Flash the firmware (replace filename with actual name)
sudo dfu-util -a 0 -D respeaker_lite_usb_v2.0.7.bin
```

**Expected output**:
```
dfu-util 0.x.x

Copyright 2005-2009 Weston Schmidt, Harald Welte and OpenMoko Inc.
...
Opening DFU capable USB device...
ID 2886:0019
Run-time device DFU version 011a
Claiming USB DFU Interface...
Setting Alternate Setting #0 ...
Determining device status: state = dfuIDLE, status = 0
dfuIDLE, continuing
DFU mode device DFU version 011a
Device returned transfer size 64
Copying data from PC to DFU device
Download        [=========================] 100%        xxxxx bytes
Download done.
state(7) = dfuMANIFEST, status(0) = No error condition is present
state(2) = dfuIDLE, status(0) = No error condition is present
Done!
```

### 5. Unplug and Replug

After flashing:
1. **Unplug** the USB cable
2. **Wait 2 seconds**
3. **Plug it back in**
4. The device should now be running the new firmware

### 6. Verify the Update

Test if stereo is now working:

```bash
# Check device
arecord -l
# Should show: ReSpeaker Lite: USB Audio

# Test recording
python3 test_stereo_recording.py
```

**Expected results after update**:
- Channels should be **different** (correlation < 0.9)
- Max difference should be > 0.000000
- TDOA should work!

## Troubleshooting

### Device Not Entering DFU Mode

- Try different USB ports
- Try different USB cable (data cable, not just charging)
- Check if there's a specific button sequence
- Some devices need to be powered on first, then button held while plugging in

### dfu-util Not Finding Device

- Make sure device is in DFU mode
- Try: `sudo dfu-util -l` (with sudo)
- Check USB connection: `lsusb` should show the device

### Firmware Flash Fails

- Make sure you downloaded the correct firmware file (USB firmware, not I2S)
- Check file is not corrupted
- Try re-entering DFU mode
- Some devices may need specific dfu-util flags

### Still Mono After Update

- Verify firmware version: `dfu-util -l` (when in DFU mode)
- Try a different firmware version
- Check if device has hardware switches or jumpers
- Contact Seeed support - may be a hardware issue

## Alternative: Check Current Firmware Version

If you want to check the current version before updating:

1. Enter DFU mode (steps above)
2. Run: `dfu-util -l`
3. Look for version information in the output

## References

- [ReSpeaker Lite GitHub](https://github.com/respeaker/ReSpeaker_Lite/)
- [ReSpeaker Lite Firmware Repository](https://github.com/respeaker/ReSpeaker_Lite/tree/master/xmos_firmwares)
- [DFU Mode Guide](https://github.com/respeaker/ReSpeaker_Lite/#latest-xmos-firmware)

## After Successful Update

Once firmware is updated and stereo is working:

1. Run `python3 test_stereo_recording.py` - should show different channels
2. Run `python3 test_tdoa_simple.py` - should show non-zero delays and angles
3. Run `python3 test_angles.py` - should show varying angles when you move around

Your TDOA system should now work correctly!

