#!/usr/bin/env python3
"""
Test I2S connection and verify stereo channels are different
"""

import numpy as np
import subprocess
import time

def test_i2s_device():
    """Check if I2S device is available"""
    print("=" * 70)
    print("Testing I2S Connection")
    print("=" * 70)
    
    # List audio devices
    print("\n1. Checking audio devices...")
    result = subprocess.run(['arecord', '-l'], capture_output=True, text=True)
    print(result.stdout)
    
    # Look for I2S device
    if 'I2S' in result.stdout or 'ReSpeaker' in result.stdout:
        print("✓ I2S/ReSpeaker device found")
    else:
        print("⚠ I2S device not found")
        print("  Make sure:")
        print("  1. I2S firmware is flashed")
        print("  2. GPIO connections are correct")
        print("  3. I2S is enabled in /boot/config.txt")
        return False
    
    return True

def test_i2s_recording():
    """Test recording from I2S and check if channels are different"""
    print("\n" + "=" * 70)
    print("Testing I2S Recording")
    print("=" * 70)
    
    print("\nRecording 3 seconds from I2S...")
    print("Speak near ONE microphone (left or right)")
    
    # Record from I2S
    cmd = [
        'arecord',
        '-D', 'hw:1,0',  # Try I2S device
        '-f', 'S16_LE',
        '-r', '16000',
        '-c', '2',
        '-d', '3',
        'test_i2s.wav'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"✗ Recording failed: {result.stderr}")
        print("\nTrying alternative device...")
        # Try hw:0,0 or other devices
        cmd[2] = 'hw:0,0'
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"✗ Recording failed: {result.stderr}")
            return False
    
    print("✓ Recording complete: test_i2s.wav")
    
    # Analyze the file
    print("\nAnalyzing channels...")
    try:
        import wave
        with wave.open('test_i2s.wav', 'rb') as wf:
            channels = wf.getnchannels()
            frames = wf.getnframes()
            audio_data = wf.readframes(frames)
            
            print(f"  Channels: {channels}")
            print(f"  Frames: {frames}")
            
            if channels != 2:
                print(f"✗ Expected 2 channels, got {channels}")
                return False
            
            # Convert to numpy
            audio = np.frombuffer(audio_data, dtype=np.int16)
            audio = audio.reshape(-1, 2)
            left = audio[:, 0].astype(np.float32) / 32768.0
            right = audio[:, 1].astype(np.float32) / 32768.0
            
            # Check if different
            are_identical = np.array_equal(left, right)
            correlation = np.corrcoef(left, right)[0, 1]
            max_diff = np.abs(left - right).max()
            
            print(f"\n  Channel Analysis:")
            print(f"  - Identical: {are_identical}")
            print(f"  - Correlation: {correlation:.6f}")
            print(f"  - Max difference: {max_diff:.6f}")
            
            if are_identical or correlation > 0.99:
                print("\n  ✗ Channels are still identical!")
                print("  This might mean:")
                print("    - Still using USB firmware (need I2S firmware)")
                print("    - Wrong device selected")
                print("    - I2S not properly configured")
                return False
            else:
                print("\n  ✓ SUCCESS! Channels are different!")
                print("  I2S is working correctly - you can now use TDOA!")
                return True
                
    except Exception as e:
        print(f"✗ Error analyzing: {e}")
        return False

def main():
    print("=" * 70)
    print("ReSpeaker Lite I2S Connection Test")
    print("=" * 70)
    
    if not test_i2s_device():
        print("\nFix I2S connection issues first.")
        return
    
    if test_i2s_recording():
        print("\n" + "=" * 70)
        print("I2S Connection Successful!")
        print("=" * 70)
        print("\nYou can now:")
        print("  1. Use audio_capture_i2s.py for I2S audio capture")
        print("  2. Run test_tdoa_simple.py - should work now!")
        print("  3. Use the TDOA system for direction estimation")
    else:
        print("\n" + "=" * 70)
        print("I2S Connection Issues")
        print("=" * 70)
        print("\nCheck:")
        print("  1. I2S firmware is flashed (not USB)")
        print("  2. GPIO connections are correct")
        print("  3. I2S is enabled in /boot/config.txt")
        print("  4. Device is powered (3.3V connected)")

if __name__ == '__main__':
    main()

