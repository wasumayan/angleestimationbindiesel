#!/bin/bash
# ReSpeaker Lite Firmware Update Commands
# Run these commands on your Raspberry Pi

echo "=========================================="
echo "ReSpeaker Lite Firmware Update"
echo "=========================================="
echo ""

# Step 2: Download USB Firmware v2.0.7
echo "Step 2: Downloading USB firmware v2.0.7..."
echo ""

# Create downloads directory if it doesn't exist
mkdir -p ~/Downloads
cd ~/Downloads

# Download the firmware file
# Note: You may need to check the actual URL from the GitHub repo
echo "Downloading firmware from GitHub..."
wget -O respeaker_lite_usb_v2.0.7.bin \
  https://github.com/respeaker/ReSpeaker_Lite/raw/master/xmos_firmwares/respeaker_lite_usb_v2.0.7.bin

# Check if download was successful
if [ -f "respeaker_lite_usb_v2.0.7.bin" ]; then
    echo "✓ Firmware downloaded successfully"
    ls -lh respeaker_lite_usb_v2.0.7.bin
else
    echo "✗ Download failed. You may need to download manually from:"
    echo "  https://github.com/respeaker/ReSpeaker_Lite/tree/master/xmos_firmwares"
    exit 1
fi

echo ""
echo "=========================================="
echo "Step 3: Enter DFU Mode"
echo "=========================================="
echo ""
echo "MANUAL STEPS (do these now):"
echo "  1. Unplug the USB cable from ReSpeaker Lite"
echo "  2. Hold down the button on ReSpeaker Lite"
echo "  3. While holding button, plug in USB cable"
echo "  4. Release button after 2-3 seconds"
echo ""
read -p "Press Enter after you've put the device in DFU mode..."

echo ""
echo "Checking if device is in DFU mode..."
dfu-util -l

echo ""
echo "If you see 'XMOS DFU' or similar, device is in DFU mode."
echo "If not, try the DFU mode steps again."
echo ""
read -p "Press Enter to continue with firmware flash (or Ctrl+C to cancel)..."

echo ""
echo "=========================================="
echo "Step 4: Flashing Firmware"
echo "=========================================="
echo ""

# Flash the firmware
cd ~/Downloads
sudo dfu-util -a 0 -D respeaker_lite_usb_v2.0.7.bin

echo ""
echo "=========================================="
echo "Step 5: Unplug and Replug Device"
echo "=========================================="
echo ""
echo "MANUAL STEPS:"
echo "  1. Unplug the USB cable"
echo "  2. Wait 2 seconds"
echo "  3. Plug it back in"
echo ""
read -p "Press Enter after you've replugged the device..."

echo ""
echo "=========================================="
echo "Step 6: Verify Update"
echo "=========================================="
echo ""

# Check if device is recognized
echo "Checking if device is recognized..."
arecord -l

echo ""
echo "Testing stereo recording..."
cd ~/angleestimationbindiesel
python3 test_stereo_recording.py

echo ""
echo "=========================================="
echo "Update Complete!"
echo "=========================================="
echo ""
echo "If channels are now different, firmware update was successful!"
echo "You can now test TDOA with: python3 test_tdoa_simple.py"

