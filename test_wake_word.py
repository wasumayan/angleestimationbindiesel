#!/usr/bin/env python3
"""
Simple test script for wake word detection using Picovoice Porcupine
Tests the wake word without camera or other components
"""

import pvporcupine
import pyaudio
import numpy as np
import os
import sys


def test_wake_word():
    """Test wake word detection"""
    print("=" * 70)
    print("Wake Word Detection Test")
    print("=" * 70)
    
    # Configuration
    PICOVOICE_ACCESS_KEY = os.getenv('PICOVOICE_ACCESS_KEY', '')
    KEYWORD_PATH = 'bin-diesel_en_raspberry-pi_v3_0_0/bin-diesel_en_raspberry-pi_v3_0_0.ppn'
    
    # Check AccessKey
    if not PICOVOICE_ACCESS_KEY:
        print("ERROR: PICOVOICE_ACCESS_KEY environment variable not set!")
        print("Get your AccessKey from: https://console.picovoice.ai/")
        print("Then set it with: export PICOVOICE_ACCESS_KEY='your-key-here'")
        return False
    
    # Check wake word file
    if not os.path.exists(KEYWORD_PATH):
        print(f"ERROR: Wake word file not found: {KEYWORD_PATH}")
        print("Make sure the bin-diesel_en_raspberry-pi_v3_0_0 folder is in the project directory")
        return False
    
    print(f"AccessKey: {PICOVOICE_ACCESS_KEY[:10]}... (hidden)")
    print(f"Wake word file: {KEYWORD_PATH}")
    print()
    
    # Initialize Porcupine
    print("[DEBUG] Initializing Porcupine wake word engine...")
    try:
        porcupine = pvporcupine.create(
            access_key=PICOVOICE_ACCESS_KEY,
            keyword_paths=[KEYWORD_PATH]
        )
        print(f"✓ Porcupine initialized successfully")
        print(f"  Sample rate: {porcupine.sample_rate} Hz")
        print(f"  Frame length: {porcupine.frame_length} samples")
        print(f"  Keyword: bin diesel")
    except Exception as e:
        print(f"✗ Error initializing Porcupine: {e}")
        print("\nTroubleshooting:")
        print("1. Check your AccessKey is correct")
        print("2. Verify the wake word file exists")
        print("3. Make sure pvporcupine is installed: pip3 install --break-system-packages pvporcupine")
        return False
    
    # Initialize PyAudio
    print("\n[DEBUG] Initializing PyAudio...")
    try:
        audio = pyaudio.PyAudio()
        
        # List available audio input devices
        print("\nAvailable audio input devices:")
        for i in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"  [{i}] {info['name']} - {info['maxInputChannels']} channels")
        
        # Open audio stream
        stream = audio.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )
        print(f"✓ Audio stream opened")
        print(f"  Using default input device")
    except Exception as e:
        print(f"✗ Error initializing audio: {e}")
        print("\nTroubleshooting:")
        print("1. Check microphone is connected")
        print("2. Check permissions: sudo usermod -a -G audio $USER (then logout/login)")
        print("3. Test microphone: arecord -d 5 test.wav && aplay test.wav")
        porcupine.delete()
        return False
    
    # Start listening
    print("\n" + "=" * 70)
    print("Listening for wake word: 'bin diesel'")
    print("=" * 70)
    print("Say 'bin diesel' to test...")
    print("Press Ctrl+C to exit")
    print()
    
    detection_count = 0
    
    try:
        while True:
            # Read audio frame
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm_array = np.frombuffer(pcm, dtype=np.int16)
            
            # Process with Porcupine
            keyword_index = porcupine.process(pcm_array)
            
            if keyword_index >= 0:
                detection_count += 1
                print(f"\n{'='*70}")
                print(f"✓ WAKE WORD DETECTED! (#{detection_count})")
                print(f"{'='*70}\n")
    
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("Test stopped by user")
        print("=" * 70)
        if detection_count > 0:
            print(f"✓ Successfully detected wake word {detection_count} time(s)")
        else:
            print("⚠ No wake word detections")
        print()
    
    except Exception as e:
        print(f"\n✗ Error during detection: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("[DEBUG] Cleaning up...")
        stream.stop_stream()
        stream.close()
        audio.terminate()
        porcupine.delete()
        print("✓ Cleanup complete")
    
    return True


if __name__ == "__main__":
    success = test_wake_word()
    sys.exit(0 if success else 1)

