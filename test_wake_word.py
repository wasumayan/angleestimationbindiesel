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

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("[DEBUG] python-dotenv not installed, .env file won't be loaded automatically")
    print("Install with: pip3 install --break-system-packages python-dotenv")

# Suppress ALSA warnings (they're harmless but noisy)
os.environ['PYTHONWARNINGS'] = 'ignore'
import warnings
warnings.filterwarnings('ignore')


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
        input_devices = []
        default_input = None
        try:
            default_input = audio.get_default_input_device_info()
            print(f"  [DEFAULT] {default_input['name']} (index: {default_input['index']})")
        except:
            print("  [DEFAULT] No default input device found")
        
        for i in range(audio.get_device_count()):
            try:
                info = audio.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    input_devices.append((i, info))
                    marker = " ← DEFAULT" if default_input and i == default_input['index'] else ""
                    print(f"  [{i}] {info['name']} - {info['maxInputChannels']} channels{marker}")
            except:
                pass
        
        if not input_devices:
            print("✗ No audio input devices found!")
            print("\nTroubleshooting:")
            print("1. Check microphone is connected: lsusb")
            print("2. Check audio devices: arecord -l")
            print("3. Check permissions: sudo usermod -a -G audio $USER (then logout/login)")
            audio.terminate()
            porcupine.delete()
            return False
        
        # Try to open audio stream
        device_index = None
        if default_input:
            device_index = default_input['index']
        
        # If no default, try first available input device
        if device_index is None and input_devices:
            device_index = input_devices[0][0]
            print(f"\n[DEBUG] No default device, using device index {device_index}")
        
        try:
            stream = audio.open(
                rate=porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=porcupine.frame_length
            )
            device_name = input_devices[0][1]['name'] if input_devices else "Unknown"
            print(f"✓ Audio stream opened")
            print(f"  Using device [{device_index}]: {device_name}")
        except Exception as stream_error:
            print(f"✗ Error opening audio stream: {stream_error}")
            print("\nTrying to find working device...")
            # Try each input device
            stream = None
            for dev_idx, dev_info in input_devices:
                try:
                    stream = audio.open(
                        rate=porcupine.sample_rate,
                        channels=1,
                        format=pyaudio.paInt16,
                        input=True,
                        input_device_index=dev_idx,
                        frames_per_buffer=porcupine.frame_length
                    )
                    print(f"✓ Audio stream opened with device [{dev_idx}]: {dev_info['name']}")
                    break
                except:
                    continue
            
            if stream is None:
                print("✗ Could not open any audio input device")
                print("\nTroubleshooting:")
                print("1. Check microphone is connected: lsusb")
                print("2. Check audio devices: arecord -l")
                print("3. Test microphone: arecord -d 5 test.wav && aplay test.wav")
                print("4. Check permissions: sudo usermod -a -G audio $USER (then logout/login)")
                audio.terminate()
                porcupine.delete()
                return False
                
    except Exception as e:
        print(f"✗ Error initializing audio: {e}")
        print("\nTroubleshooting:")
        print("1. Check microphone is connected: lsusb")
        print("2. Check audio devices: arecord -l")
        print("3. Check permissions: sudo usermod -a -G audio $USER (then logout/login)")
        print("4. Test microphone: arecord -d 5 test.wav && aplay test.wav")
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

