# ReSpeaker Lite Firmware Download - Alternative Methods

## Problem: Direct Download URL Not Working

The GitHub raw URL may not work directly. Here are alternative methods:

## Method 1: Clone the Repository (Recommended)

```bash
cd ~/Downloads
git clone https://github.com/respeaker/ReSpeaker_Lite.git
cd ReSpeaker_Lite/xmos_firmwares
ls -la
# Look for: respeaker_lite_usb_v2.0.7.bin or similar
```

Then copy the firmware file:
```bash
cp respeaker_lite_usb_v2.0.7.bin ~/Downloads/
cd ~/Downloads
```

## Method 2: Download from GitHub Releases/Releases Page

Check if there's a releases page:
```bash
# Try browsing to: https://github.com/respeaker/ReSpeaker_Lite/releases
# Or download using release tag
```

## Method 3: Use GitHub API

```bash
cd ~/Downloads
# Get the file using GitHub API
curl -L -o respeaker_lite_usb_v2.0.7.bin \
  "https://api.github.com/repos/respeaker/ReSpeaker_Lite/contents/xmos_firmwares/respeaker_lite_usb_v2.0.7.bin" \
  -H "Accept: application/vnd.github.v3.raw"
```

## Method 4: Manual Download

1. Go to: https://github.com/respeaker/ReSpeaker_Lite
2. Navigate to: `xmos_firmwares` folder
3. Click on the firmware file (e.g., `respeaker_lite_usb_v2.0.7.bin`)
4. Click "Download" or "Raw"
5. Transfer to Pi using scp or USB drive

Then on Pi:
```bash
# If using scp from another computer:
# scp respeaker_lite_usb_v2.0.7.bin pi@your-pi-ip:~/Downloads/

# Or copy from USB drive
cp /media/usb/respeaker_lite_usb_v2.0.7.bin ~/Downloads/
```

## Method 5: Check Available Firmware Files

First, see what files are actually available:

```bash
cd ~/Downloads
git clone --depth 1 https://github.com/respeaker/ReSpeaker_Lite.git
cd ReSpeaker_Lite
find . -name "*.bin" -type f
```

This will show all .bin files in the repository. Look for USB firmware files.

## Quick Commands to Try

**Option A: Clone and find file**
```bash
cd ~/Downloads
rm -rf ReSpeaker_Lite  # Clean up if exists
git clone https://github.com/respeaker/ReSpeaker_Lite.git
cd ReSpeaker_Lite/xmos_firmwares
ls -la *.bin
# Copy the USB firmware file you find
cp *usb*.bin ~/Downloads/respeaker_lite_usb_v2.0.7.bin
cd ~/Downloads
```

**Option B: Check if file exists with different name**
```bash
cd ~/Downloads
git clone https://github.com/respeaker/ReSpeaker_Lite.git
cd ReSpeaker_Lite
find . -name "*usb*.bin" -o -name "*2.0*.bin"
```

## Verify File After Download

```bash
cd ~/Downloads
ls -lh *.bin
file respeaker_lite_usb_v2.0.7.bin
# Should show it's a binary file, not empty
```

The file should be several hundred KB to a few MB, not 0 bytes.

