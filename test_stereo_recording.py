#!/usr/bin/env python3
"""
Test if ReSpeaker records true stereo or just mono duplicated
"""

import subprocess
import numpy as np
import wave
import os

def test_arecord_stereo():
    """Test recording with arecord and analyze"""
    print("=" * 70)
    print("Testing ReSpeaker Stereo Recording")
    print("=" * 70)
    
    print("\n1. Recording 3 seconds...")
    print("   Please speak near ONE microphone (left or right)")
    print("   Then we'll analyze if channels are different...\n")
    
    # Record
    try:
        result = subprocess.run([
            'arecord', '-D', 'hw:3,0', '-f', 'S16_LE', 
            '-r', '16000', '-c', '2', '-d', '3', 'test_stereo.wav'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"✗ Error recording: {result.stderr}")
            return False
        
        print("✓ Recording complete: test_stereo.wav")
        
    except FileNotFoundError:
        print("✗ arecord not found. Install with: sudo apt-get install alsa-utils")
        return False
    
    # Check file
    print("\n2. Analyzing file...")
    try:
        result = subprocess.run(['file', 'test_stereo.wav'], 
                              capture_output=True, text=True)
        print(f"   {result.stdout.strip()}")
        
        # Check if it says 2 channels
        if '2 channels' in result.stdout or 'stereo' in result.stdout.lower():
            print("   ✓ File is marked as stereo (2 channels)")
        else:
            print("   ⚠ File format doesn't clearly indicate stereo")
    
    except FileNotFoundError:
        print("   ⚠ 'file' command not available")
    
    # Analyze audio data
    print("\n3. Analyzing audio channels...")
    try:
        with wave.open('test_stereo.wav', 'rb') as wf:
            channels = wf.getnchannels()
            sample_rate = wf.getframerate()
            frames = wf.getnframes()
            
            print(f"   Channels: {channels}")
            print(f"   Sample rate: {sample_rate} Hz")
            print(f"   Frames: {frames}")
            
            if channels != 2:
                print(f"\n   ✗ File has {channels} channel(s), not 2!")
                return False
            
            # Read audio data
            audio_data = wf.readframes(frames)
            audio = np.frombuffer(audio_data, dtype=np.int16)
            
            # Reshape for stereo
            audio = audio.reshape(-1, 2)
            left = audio[:, 0].astype(np.float32) / 32768.0
            right = audio[:, 1].astype(np.float32) / 32768.0
            
            # Check if identical
            are_identical = np.array_equal(left, right)
            correlation = np.corrcoef(left, right)[0, 1]
            max_diff = np.abs(left - right).max()
            mean_diff = np.abs(left - right).mean()
            
            print(f"\n   Channel Analysis:")
            print(f"   - Identical: {are_identical}")
            print(f"   - Correlation: {correlation:.6f}")
            print(f"   - Max difference: {max_diff:.6f}")
            print(f"   - Mean difference: {mean_diff:.6f}")
            
            # Levels
            left_level = np.abs(left).max()
            right_level = np.abs(right).max()
            print(f"   - Left max level: {left_level:.4f}")
            print(f"   - Right max level: {right_level:.4f}")
            
            print("\n" + "=" * 70)
            if are_identical or correlation > 0.99:
                print("❌ PROBLEM: Channels are identical!")
                print("   The device is outputting mono to both channels.")
                print("   This confirms the firmware/configuration issue.")
                print("\n   Next steps:")
                print("   1. Install dfu-util: sudo apt-get install dfu-util")
                print("   2. Check firmware: dfu-util -l (device must be in DFU mode)")
                print("   3. Update to USB firmware v2.0.7 if needed")
                return False
            elif correlation > 0.9:
                print("⚠ WARNING: Channels are very similar")
                print("   There may be some difference, but not enough for reliable TDOA")
                return False
            else:
                print("✓ SUCCESS: Channels are different!")
                print("   Stereo recording is working correctly.")
                print("   If TDOA still doesn't work, check:")
                print("   - Microphone spacing constant (should be 0.07m)")
                print("   - Sound source position (try speaking from the side)")
                return True
    
    except Exception as e:
        print(f"✗ Error analyzing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        if os.path.exists('test_stereo.wav'):
            print(f"\n   Test file saved: test_stereo.wav")
            print(f"   You can play it with: aplay test_stereo.wav")

def main():
    result = test_arecord_stereo()
    
    print("\n" + "=" * 70)
    if result:
        print("Stereo recording is working! The issue may be elsewhere.")
    else:
        print("Stereo recording is NOT working. Firmware update likely needed.")
    print("=" * 70)

if __name__ == '__main__':
    main()

