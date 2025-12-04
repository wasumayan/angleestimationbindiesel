# ReSpeaker Troubleshooting Guide

## Problem: ReSpeaker Not Showing in `lsusb`

If `lsusb` doesn't show your ReSpeaker, it's a hardware/connection issue.

### Step 1: Physical Connection Checks

1. **Check USB Connection**
   - Unplug and replug the USB cable
   - Try a different USB port on the Pi
   - Try a different USB cable (if detachable)
   - Make sure it's fully inserted

2. **Check Power**
   - ReSpeaker should have an LED indicator
   - If LED doesn't light up, it's not getting power
   - Try a powered USB hub if Pi USB port doesn't provide enough power

3. **Check USB Port**
   - Try all USB ports on the Pi
   - USB 2.0 and USB 3.0 ports both should work
   - Avoid USB-C ports if your Pi has them (they may not work the same)

### Step 2: Verify USB Ports Work

```bash
# Check if USB ports are working at all
# Plug in ANY USB device (flash drive, keyboard, etc.)
lsusb

# If nothing shows up, USB subsystem might have issues
```

### Step 3: Check System Logs

```bash
# Check kernel messages for USB devices
dmesg | tail -20

# Watch for USB connection events
dmesg | grep -i usb

# Check if device was detected then disconnected
dmesg | grep -i "disconnect\|connect"
```

Look for messages like:
- `New USB device found`
- `USB disconnect`
- Error messages about the device

### Step 4: ReSpeaker-Specific Checks

**ReSpeaker 4 Mic Array (USB):**
- Should appear as "Seeed" or "ReSpeaker" in lsusb
- LED should light up when connected
- May need to be in a specific mode (check ReSpeaker documentation)

**ReSpeaker 2-Mic Array:**
- Similar to 4-mic, but with 2 microphones
- Should also show as "Seeed" device

**Check ReSpeaker Model:**
- Different models may have different requirements
- Some may need specific drivers
- Check the ReSpeaker product page for your specific model

### Step 5: Test on Another Computer

```bash
# If possible, test ReSpeaker on another computer
# If it works there, issue is with Pi
# If it doesn't work there, issue is with ReSpeaker hardware
```

### Step 6: Check USB Power Issues

Raspberry Pi USB ports sometimes don't provide enough power:

```bash
# Check USB power
vcgencmd get_throttled

# If you see throttling, USB power might be insufficient
# Solution: Use a powered USB hub
```

### Step 7: ReSpeaker Setup (If Detected)

Once ReSpeaker appears in `lsusb`:

```bash
# Should see something like:
# Bus 001 Device 005: ID 2886:0018 ReSpeaker 4 Mic Array

# Then check audio devices
arecord -l
# Should show ReSpeaker as an audio device

# Test recording
arecord -d 5 -D hw:1,0 test.wav
# (Replace hw:1,0 with your ReSpeaker's card/device from arecord -l)
```

### Step 8: Alternative: Use Different Microphone

If ReSpeaker won't work:

1. **USB Microphone** - Any USB microphone should work
2. **USB Sound Card with Mic** - USB audio adapters with microphone input
3. **Bluetooth Headset** - May need additional setup
4. **3.5mm Microphone** - If Pi has audio jack input (most don't)

### Step 9: Check ReSpeaker Documentation

- [ReSpeaker 4 Mic Array Documentation](https://wiki.seeedstudio.com/ReSpeaker_4_Mic_Array_for_Raspberry_Pi/)
- [ReSpeaker 2 Mic Array Documentation](https://wiki.seeedstudio.com/ReSpeaker_2_Mics_Pi_HAT/)
- Check for specific setup requirements for your model

### Step 10: Quick Diagnostic Script

Run this to check everything:

```bash
echo "=== USB Devices ==="
lsusb
echo ""
echo "=== Audio Cards ==="
cat /proc/asound/cards
echo ""
echo "=== ALSA Devices ==="
arecord -l
echo ""
echo "=== Recent USB Events ==="
dmesg | tail -30 | grep -i usb
```

## Common Issues

### Issue: ReSpeaker LED doesn't light up

**Possible causes:**
- Not getting power
- Faulty USB cable
- Faulty ReSpeaker
- USB port not providing power

**Solutions:**
- Try powered USB hub
- Try different USB cable
- Try different USB port
- Test on another computer

### Issue: ReSpeaker appears then disappears

**Possible causes:**
- Power issue (not enough power)
- USB cable issue (loose connection)
- Driver crash

**Solutions:**
- Use powered USB hub
- Check dmesg for error messages
- Try different USB cable

### Issue: ReSpeaker appears but no audio

**This is different** - device is detected but audio doesn't work
- See TROUBLESHOOTING_AUDIO.md for audio-specific issues

## Still Not Working?

1. **Verify ReSpeaker model** - Make sure you have the USB version, not the HAT version
2. **Check ReSpeaker is functional** - Test on another computer
3. **Check Pi USB ports** - Test with other USB devices
4. **Try powered USB hub** - Pi USB ports sometimes have power issues
5. **Check for physical damage** - USB port, cable, or ReSpeaker itself

## For Now: Test Camera Without Wake Word

While troubleshooting ReSpeaker, you can test the camera/flag detection:

```bash
# Test camera and flag detection
python3 camerasimple.py
```

This doesn't require a microphone and will let you verify the camera and color detection are working.

