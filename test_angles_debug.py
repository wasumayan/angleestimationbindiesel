#!/usr/bin/env python3
"""
Debug version of test_angles.py with detailed diagnostics
Shows what's happening at each step
"""

import time
import numpy as np
from audio_capture import ReSpeakerCapture
from direction_estimator import DirectionEstimator


def main():
    sample_rate = 16000
    history_size = 10

    # Init capture + estimator
    # ReSpeaker Lite has 7cm (0.07m) microphone spacing
    capture = ReSpeakerCapture(sample_rate=sample_rate)
    estimator = DirectionEstimator(sample_rate=sample_rate, mic_spacing=0.07)

    print("Starting ReSpeaker stream...")
    capture.start_stream()
    time.sleep(0.5)

    angle_history = []

    print("\n" + "=" * 70)
    print("DEBUG MODE: Showing detailed information")
    print("=" * 70)
    print("\nMove around the mics and clap / talk.")
    print("Positive angle = sound from the RIGHT")
    print("Negative angle = sound from the LEFT")
    print("Press Ctrl+C to stop.\n")

    chunk_count = 0
    zero_delay_count = 0
    none_count = 0

    try:
        while True:
            # Get a chunk of audio
            left, right = capture.read_chunk()
            chunk_count += 1

            # Show audio levels
            left_level = np.abs(left).max()
            right_level = np.abs(right).max()
            left_energy = np.mean(left ** 2)
            right_energy = np.mean(right ** 2)

            # Calculate correlation manually to see what's happening
            left_norm = left - np.mean(left)
            right_norm = right - np.mean(right)
            correlation = np.correlate(left_norm, right_norm, mode='full')
            
            center = len(correlation) // 2
            max_delay = estimator.max_delay_samples
            search_range = slice(center - max_delay, center + max_delay + 1)
            correlation_window = correlation[search_range]
            peak_index = np.argmax(np.abs(correlation_window))
            delay_samples = peak_index - max_delay
            peak_value = correlation_window[peak_index]
            
            # Normalize correlation
            max_possible = np.sqrt(np.sum(left_norm**2) * np.sum(right_norm**2))
            normalized_corr = abs(peak_value) / (max_possible + 1e-10)

            # Raw angle estimate
            angle = estimator.estimate_angle(left, right, threshold=0.0)

            if delay_samples == 0:
                zero_delay_count += 1

            if angle is None:
                none_count += 1
            else:
                angle_history.append(angle)
                if len(angle_history) > history_size:
                    angle_history.pop(0)

                smoothed = estimator.smooth_angle(angle_history)

                # Print detailed info every chunk
                status = "✓" if angle is not None else "✗"
                print(f"{status} Chunk {chunk_count:4d} | "
                      f"Delay: {delay_samples:4d} samples | "
                      f"Corr: {normalized_corr:.4f} | "
                      f"Levels: L={left_level:.3f} R={right_level:.3f} | "
                      f"Raw: {angle:7.2f}°" if angle is not None else f"Raw: None",
                      end="")
                
                if smoothed is not None:
                    print(f" | Smoothed: {smoothed:7.2f}°")
                else:
                    print(" | Smoothed: N/A")

            # Show statistics every 50 chunks
            if chunk_count % 50 == 0:
                print("\n" + "-" * 70)
                print(f"Statistics after {chunk_count} chunks:")
                print(f"  Zero delay chunks: {zero_delay_count} ({100*zero_delay_count/chunk_count:.1f}%)")
                print(f"  None angles: {none_count} ({100*none_count/chunk_count:.1f}%)")
                if angle_history:
                    print(f"  Angle range: {np.min(angle_history):.2f}° to {np.max(angle_history):.2f}°")
                    print(f"  Angle mean: {np.mean(angle_history):.2f}°")
                print("-" * 70 + "\n")

            # Don't spam too fast
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n" + "=" * 70)
        print("Final Statistics:")
        print("=" * 70)
        print(f"Total chunks: {chunk_count}")
        print(f"Zero delay chunks: {zero_delay_count} ({100*zero_delay_count/chunk_count:.1f}%)")
        print(f"None angles: {none_count} ({100*none_count/chunk_count:.1f}%)")
        
        if zero_delay_count / chunk_count > 0.9:
            print("\n⚠️  DIAGNOSIS: Most chunks have zero delay!")
            print("   This means both microphones are receiving the same signal.")
            print("   Possible causes:")
            print("   1. Sound source is directly in front (0°)")
            print("   2. Microphones are too close together")
            print("   3. Room acoustics causing reflections")
            print("   4. Microphone spacing constant (0.04m) may be wrong")
            print("\n   Try:")
            print("   - Speaking from the SIDE (left or right)")
            print("   - Clapping from different angles")
            print("   - Moving the sound source around")
        
        if angle_history:
            print(f"\nAngle statistics:")
            print(f"  Valid angles: {len(angle_history)}")
            print(f"  Range: {np.min(angle_history):.2f}° to {np.max(angle_history):.2f}°")
            print(f"  Mean: {np.mean(angle_history):.2f}°")
            print(f"  Std Dev: {np.std(angle_history):.2f}°")
        
        capture.cleanup()


if __name__ == "__main__":
    main()

