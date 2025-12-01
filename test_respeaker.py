#!/usr/bin/env python3
"""
Test script to verify ReSpeaker connection and audio capture
Run this to check if ReSpeaker is properly connected and working
"""

import sys
import numpy as np

def test_audio_devices():
    """List all available audio devices"""
    try:
        import pyaudio
        print("=" * 60)
        print("Available Audio Devices:")
        print("=" * 60)
        
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        
        if device_count == 0:
            print("ERROR: No audio devices found!")
            return None
        
        respeaker_index = None
        
        for i in range(device_count):
            try:
                info = p.get_device_info_by_index(i)
                name = info.get('name', 'Unknown')
                max_input_channels = info.get('maxInputChannels', 0)
                
                # Check if this is the ReSpeaker
                is_respeaker = 'respeaker' in name.lower() or 'seeed' in name.lower()
                
                if is_respeaker:
                    respeaker_index = i
                    print(f"\n>>> FOUND RESPEAKER <<<")
                
                print(f"\nDevice {i}: {name}")
                print(f"  Max Input Channels: {max_input_channels}")
                print(f"  Sample Rate: {info.get('defaultSampleRate', 'N/A')} Hz")
                
                if is_respeaker:
                    print(f"  ✓ This appears to be your ReSpeaker!")
            
            except Exception as e:
                print(f"Device {i}: Error reading info - {e}")
        
        p.terminate()
        
        if respeaker_index is None:
            print("\n" + "=" * 60)
            print("WARNING: ReSpeaker not found in device list!")
            print("=" * 60)
            print("\nTroubleshooting:")
            print("1. Check USB connection: lsusb")
            print("2. Check if device is recognized: arecord -l")
            print("3. Try unplugging and replugging the USB cable")
        else:
            print("\n" + "=" * 60)
            print(f"✓ ReSpeaker found at device index {respeaker_index}")
            print("=" * 60)
        
        return respeaker_index
        
    except ImportError:
        print("ERROR: pyaudio not installed!")
        print("Install with: pip3 install pyaudio")
        print("Or: sudo apt-get install python3-pyaudio")
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def test_audio_capture(device_index=None, duration=3):
    """Test capturing audio from ReSpeaker"""
    try:
        from audio_capture import ReSpeakerCapture
        import time
        
        print("\n" + "=" * 60)
        print("Testing Audio Capture")
        print("=" * 60)
        
        # Create capture object
        if device_index is not None:
            print(f"Using device index: {device_index}")
            capture = ReSpeakerCapture(device_index=device_index)
        else:
            print("Auto-detecting ReSpeaker...")
            capture = ReSpeakerCapture()
        
        # Start stream
        print("\nStarting audio stream...")
        capture.start_stream()
        
        print(f"\nRecording for {duration} seconds...")
        print("Please speak or make noise near the microphones!")
        print("(You should see audio levels below)\n")
        
        # Capture audio and show levels
        start_time = time.time()
        chunk_count = 0
        max_levels = []
        
        try:
            while time.time() - start_time < duration:
                left_channel, right_channel = capture.read_chunk()
                chunk_count += 1
                
                # Calculate audio levels
                left_level = np.abs(left_channel).max()
                right_level = np.abs(right_channel).max()
                max_levels.append((left_level, right_level))
                
                # Show progress every 10 chunks
                if chunk_count % 10 == 0:
                    avg_left = np.mean([l for l, r in max_levels[-10:]])
                    avg_right = np.mean([r for l, r in max_levels[-10:]])
                    
                    # Simple bar graph
                    left_bars = int(avg_left * 50)
                    right_bars = int(avg_right * 50)
                    
                    print(f"Chunk {chunk_count:4d} | "
                          f"Left: {'█' * left_bars:<50} ({avg_left:.3f}) | "
                          f"Right: {'█' * right_bars:<50} ({avg_right:.3f})")
        
        except KeyboardInterrupt:
            print("\n\nStopped by user")
        
        finally:
            capture.cleanup()
        
        # Summary
        if max_levels:
            max_left = max([l for l, r in max_levels])
            max_right = max([r for l, r in max_levels])
            avg_left = np.mean([l for l, r in max_levels])
            avg_right = np.mean([r for l, r in max_levels])
            
            print("\n" + "=" * 60)
            print("Capture Summary:")
            print("=" * 60)
            print(f"Chunks captured: {chunk_count}")
            print(f"Left channel - Max: {max_left:.3f}, Avg: {avg_left:.3f}")
            print(f"Right channel - Max: {max_right:.3f}, Avg: {avg_right:.3f}")
            
            if max_left > 0.01 or max_right > 0.01:
                print("\n✓ SUCCESS: Audio is being captured!")
                print("  Both microphones appear to be working.")
            else:
                print("\n⚠ WARNING: Very low audio levels detected.")
                print("  Try speaking louder or checking microphone positions.")
        
        return True
        
    except ImportError as e:
        print(f"ERROR: Could not import audio_capture module: {e}")
        print("Make sure audio_capture.py is in the same directory")
        return False
    except Exception as e:
        print(f"ERROR during capture: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_stereo_separation():
    """Test that left and right channels are different (for direction estimation)"""
    try:
        from audio_capture import ReSpeakerCapture
        import time
        
        print("\n" + "=" * 60)
        print("Testing Stereo Channel Separation")
        print("=" * 60)
        print("\nThis test checks if left and right microphones are working independently.")
        print("Speak closer to ONE microphone at a time.\n")
        
        capture = ReSpeakerCapture()
        capture.start_stream()
        
        print("Capturing 2 seconds of audio...")
        time.sleep(2)
        
        # Capture several chunks
        left_samples = []
        right_samples = []
        
        for _ in range(20):
            left, right = capture.read_chunk()
            left_samples.extend(left)
            right_samples.extend(right)
        
        capture.cleanup()
        
        # Analyze
        left_samples = np.array(left_samples)
        right_samples = np.array(right_samples)
        
        left_energy = np.mean(left_samples ** 2)
        right_energy = np.mean(right_samples ** 2)
        
        # Cross-correlation to check if channels are different
        correlation = np.corrcoef(left_samples, right_samples)[0, 1]
        
        print("\n" + "=" * 60)
        print("Stereo Analysis:")
        print("=" * 60)
        print(f"Left channel energy:  {left_energy:.6f}")
        print(f"Right channel energy: {right_energy:.6f}")
        print(f"Channel correlation:  {correlation:.3f}")
        
        if abs(correlation) < 0.95:
            print("\n✓ SUCCESS: Channels are independent (good for direction estimation)")
        else:
            print("\n⚠ WARNING: Channels are very similar.")
            print("  This might indicate both mics are receiving the same signal.")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("ReSpeaker Connection Test")
    print("=" * 60)
    print("\nThis script will test if your ReSpeaker is properly connected.")
    print("Make sure the ReSpeaker is plugged into the Raspberry Pi USB port.\n")
    
    input("Press Enter to continue...")
    
    # Test 1: List devices
    respeaker_index = test_audio_devices()
    
    if respeaker_index is None:
        print("\n" + "=" * 60)
        print("Cannot proceed - ReSpeaker not found.")
        print("=" * 60)
        print("\nTry these commands manually:")
        print("  lsusb                    # Check USB devices")
        print("  arecord -l               # List audio recording devices")
        print("  dmesg | tail            # Check system messages")
        sys.exit(1)
    
    # Test 2: Capture audio
    print("\n" + "=" * 60)
    response = input("Test audio capture? (y/n): ").strip().lower()
    if response == 'y':
        test_audio_capture(respeaker_index, duration=3)
    
    # Test 3: Stereo separation
    print("\n" + "=" * 60)
    response = input("Test stereo channel separation? (y/n): ").strip().lower()
    if response == 'y':
        test_stereo_separation()
    
    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("=" * 60)
    print("\nIf all tests passed, your ReSpeaker is ready to use!")
    print("You can now run: python3 main.py")


if __name__ == '__main__':
    main()

