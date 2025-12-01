#!/usr/bin/env python3
"""
Detailed diagnostic test for ReSpeaker angle estimation
Shows audio levels, correlation values, and step-by-step angle calculation
"""

import numpy as np
import time
from audio_capture import ReSpeakerCapture
from direction_estimator import DirectionEstimator


def test_audio_levels(capture, duration=3):
    """Test if audio is being captured and show levels"""
    print("\n" + "=" * 70)
    print("TEST 1: Audio Input Levels")
    print("=" * 70)
    print("Speak or make noise near the microphones...\n")
    
    max_left = 0
    max_right = 0
    chunk_count = 0
    start_time = time.time()
    
    try:
        while time.time() - start_time < duration:
            left, right = capture.read_chunk()
            chunk_count += 1
            
            left_max = np.abs(left).max()
            right_max = np.abs(right).max()
            
            max_left = max(max_left, left_max)
            max_right = max(max_right, right_max)
            
            # Show levels every 10 chunks
            if chunk_count % 10 == 0:
                left_bars = int(left_max * 50)
                right_bars = int(right_max * 50)
                print(f"Chunk {chunk_count:4d} | "
                      f"Left: {'█' * left_bars:<50} ({left_max:.4f}) | "
                      f"Right: {'█' * right_bars:<50} ({right_max:.4f})")
    
    except KeyboardInterrupt:
        pass
    
    print("\n" + "-" * 70)
    print(f"Summary: {chunk_count} chunks processed")
    print(f"Max Left Level:  {max_left:.4f}")
    print(f"Max Right Level: {max_right:.4f}")
    
    if max_left < 0.001 and max_right < 0.001:
        print("\n⚠️  WARNING: Very low audio levels detected!")
        print("   Microphones may not be receiving input.")
        print("   Check: USB connection, microphone positions, speak louder")
        return False
    elif max_left < 0.01 or max_right < 0.01:
        print("\n⚠️  WARNING: Low audio levels.")
        print("   Try speaking closer or louder.")
        return True
    else:
        print("\n✓ Audio levels look good!")
        return True


def test_correlation(capture, estimator, duration=3):
    """Test cross-correlation and show detailed values"""
    print("\n" + "=" * 70)
    print("TEST 2: Cross-Correlation Analysis")
    print("=" * 70)
    print("Speak from different positions (left, center, right)...\n")
    
    correlations = []
    delays = []
    chunk_count = 0
    start_time = time.time()
    
    try:
        while time.time() - start_time < duration:
            left, right = capture.read_chunk()
            chunk_count += 1
            
            # Normalize signals
            left_norm = left - np.mean(left)
            right_norm = right - np.mean(right)
            
            # Compute correlation
            correlation = np.correlate(left_norm, right_norm, mode='full')
            
            # Find peak
            center = len(correlation) // 2
            max_delay = estimator.max_delay_samples
            search_range = slice(center - max_delay, center + max_delay + 1)
            correlation_window = correlation[search_range]
            peak_index = np.argmax(np.abs(correlation_window))
            delay_samples = peak_index - max_delay
            peak_value = correlation_window[peak_index]
            
            # Normalize correlation
            max_possible = np.sqrt(np.sum(left_norm**2) * np.sum(right_norm**2))
            normalized = abs(peak_value) / (max_possible + 1e-10)
            
            correlations.append(normalized)
            delays.append(delay_samples)
            
            # Show details every 20 chunks
            if chunk_count % 20 == 0:
                left_level = np.abs(left).max()
                right_level = np.abs(right).max()
                print(f"Chunk {chunk_count:4d} | "
                      f"Delay: {delay_samples:4d} samples | "
                      f"Corr: {normalized:.4f} | "
                      f"Levels: L={left_level:.3f} R={right_level:.3f}")
    
    except KeyboardInterrupt:
        pass
    
    if correlations:
        avg_corr = np.mean(correlations)
        max_corr = np.max(correlations)
        min_corr = np.min(correlations)
        avg_delay = np.mean(np.abs(delays))
        
        print("\n" + "-" * 70)
        print(f"Correlation Statistics:")
        print(f"  Average: {avg_corr:.4f}")
        print(f"  Maximum: {max_corr:.4f}")
        print(f"  Minimum: {min_corr:.4f}")
        print(f"  Average |Delay|: {avg_delay:.2f} samples")
        
        if max_corr < 0.1:
            print("\n⚠️  WARNING: Very low correlation values!")
            print("   This suggests:")
            print("   - Signals are too similar (both mics getting same sound)")
            print("   - Very low signal levels")
            print("   - Microphones may not be working independently")
        elif max_corr > 0.9:
            print("\n⚠️  WARNING: Very high correlation!")
            print("   Signals are too similar - microphones may be receiving")
            print("   the same sound (not good for direction estimation)")
        else:
            print("\n✓ Correlation values look reasonable")
    
    return correlations, delays


def test_angle_estimation(capture, estimator, duration=5):
    """Test angle estimation with detailed output"""
    print("\n" + "=" * 70)
    print("TEST 3: Angle Estimation")
    print("=" * 70)
    print("Instructions:")
    print("  - Speak from the LEFT side → should see negative angles")
    print("  - Speak from CENTER → should see ~0°")
    print("  - Speak from the RIGHT side → should see positive angles")
    print("\nStarting test...\n")
    
    angles = []
    chunk_count = 0
    start_time = time.time()
    last_print_time = start_time
    
    try:
        while time.time() - start_time < duration:
            left, right = capture.read_chunk()
            chunk_count += 1
            
            # Estimate angle with different thresholds
            angle_none = estimator.estimate_angle(left, right, threshold=0.0)
            angle_low = estimator.estimate_angle(left, right, threshold=0.1)
            angle_med = estimator.estimate_angle(left, right, threshold=0.3)
            
            if angle_none is not None:
                angles.append(angle_none)
            
            # Print every 0.5 seconds
            if time.time() - last_print_time >= 0.5:
                left_level = np.abs(left).max()
                right_level = np.abs(right).max()
                
                status = "✓" if angle_none is not None else "✗"
                print(f"{status} Chunk {chunk_count:4d} | "
                      f"Angle (th=0.0): {angle_none:7.2f}° | "
                      f"Angle (th=0.1): {angle_low:7.2f}° | "
                      f"Angle (th=0.3): {angle_med:7.2f}° | "
                      f"Levels: L={left_level:.3f} R={right_level:.3f}")
                
                last_print_time = time.time()
    
    except KeyboardInterrupt:
        pass
    
    if angles:
        print("\n" + "-" * 70)
        print(f"Angle Statistics ({len(angles)} valid estimates):")
        print(f"  Mean: {np.mean(angles):.2f}°")
        print(f"  Std Dev: {np.std(angles):.2f}°")
        print(f"  Range: {np.min(angles):.2f}° to {np.max(angles):.2f}°")
        
        if np.std(angles) < 1.0:
            print("\n⚠️  WARNING: Angles are very consistent (low variation)")
            print("   This might indicate:")
            print("   - Sound source is stationary")
            print("   - Algorithm is not detecting direction changes")
        else:
            print("\n✓ Angle estimation is working - angles vary as expected")
    else:
        print("\n⚠️  WARNING: No valid angles estimated!")
        print("   All estimates returned None.")
        print("   Check threshold settings and audio levels.")
    
    return angles


def test_detailed_angle_calculation(capture, estimator):
    """Show step-by-step calculation for one chunk"""
    print("\n" + "=" * 70)
    print("TEST 4: Detailed Angle Calculation (Single Chunk)")
    print("=" * 70)
    print("Speak near the microphones, then press Enter to capture one chunk...")
    input()
    
    left, right = capture.read_chunk()
    
    print("\nAudio Statistics:")
    print(f"  Left channel:  mean={np.mean(left):.6f}, std={np.std(left):.6f}, max={np.abs(left).max():.6f}")
    print(f"  Right channel: mean={np.mean(right):.6f}, std={np.std(right):.6f}, max={np.abs(right).max():.6f}")
    
    # Normalize
    left_norm = left - np.mean(left)
    right_norm = right - np.mean(right)
    
    # Correlation
    correlation = np.correlate(left_norm, right_norm, mode='full')
    center = len(correlation) // 2
    max_delay = estimator.max_delay_samples
    search_range = slice(center - max_delay, center + max_delay + 1)
    correlation_window = correlation[search_range]
    peak_index = np.argmax(np.abs(correlation_window))
    delay_samples = peak_index - max_delay
    peak_value = correlation_window[peak_index]
    
    print(f"\nCross-Correlation:")
    print(f"  Correlation window size: {len(correlation_window)}")
    print(f"  Peak index: {peak_index} (relative to center)")
    print(f"  Delay: {delay_samples} samples")
    print(f"  Peak correlation value: {peak_value:.6f}")
    
    # Normalize
    max_possible = np.sqrt(np.sum(left_norm**2) * np.sum(right_norm**2))
    normalized = abs(peak_value) / (max_possible + 1e-10)
    print(f"  Normalized correlation: {normalized:.6f}")
    
    # Angle calculation
    delay_time = delay_samples / estimator.sample_rate
    sin_angle = (delay_time * estimator.speed_of_sound) / estimator.mic_spacing
    sin_angle = np.clip(sin_angle, -1.0, 1.0)
    angle_rad = np.arcsin(sin_angle)
    angle_deg = np.degrees(angle_rad)
    
    if delay_samples < 0:
        angle_deg = -angle_deg
    
    print(f"\nAngle Calculation:")
    print(f"  Delay time: {delay_time*1000:.3f} ms")
    print(f"  sin(angle) = ({delay_time:.6f} * {estimator.speed_of_sound}) / {estimator.mic_spacing}")
    print(f"  sin(angle) = {sin_angle:.6f}")
    print(f"  angle = {angle_deg:.2f}°")
    
    if delay_samples == 0:
        print("\n⚠️  NOTE: Zero delay detected - sound is directly in front")
    elif abs(delay_samples) > max_delay:
        print(f"\n⚠️  WARNING: Delay ({delay_samples}) exceeds max expected ({max_delay})")
        print("   This might indicate an issue with the calculation")


def main():
    print("=" * 70)
    print("ReSpeaker Angle Estimation Diagnostic Test")
    print("=" * 70)
    print("\nThis script will help identify issues with:")
    print("  1. Audio capture (are microphones receiving input?)")
    print("  2. Cross-correlation (are signals different enough?)")
    print("  3. Angle estimation (is the algorithm working?)")
    print("  4. Detailed calculation (step-by-step analysis)")
    
    input("\nPress Enter to start...")
    
    # Initialize
    print("\nInitializing ReSpeaker...")
    capture = ReSpeakerCapture(sample_rate=16000)
    capture.start_stream()
    time.sleep(0.5)
    
    estimator = DirectionEstimator(sample_rate=16000, mic_spacing=0.07)
    
    try:
        # Test 1: Audio levels
        audio_ok = test_audio_levels(capture, duration=3)
        if not audio_ok:
            print("\n❌ Audio input test failed. Fix audio issues before continuing.")
            return
        
        input("\nPress Enter to continue to correlation test...")
        
        # Test 2: Correlation
        correlations, delays = test_correlation(capture, estimator, duration=3)
        
        input("\nPress Enter to continue to angle estimation test...")
        
        # Test 3: Angle estimation
        angles = test_angle_estimation(capture, estimator, duration=5)
        
        input("\nPress Enter for detailed calculation...")
        
        # Test 4: Detailed calculation
        test_detailed_angle_calculation(capture, estimator)
        
        print("\n" + "=" * 70)
        print("Diagnostic Complete!")
        print("=" * 70)
        print("\nSummary:")
        print(f"  Audio input: {'✓ Working' if audio_ok else '✗ Not working'}")
        print(f"  Correlation: {'✓ OK' if correlations and np.max(correlations) > 0.1 else '✗ Low'}")
        print(f"  Angle estimation: {'✓ Working' if angles else '✗ No angles'}")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    finally:
        capture.cleanup()
        print("\nCleanup complete.")


if __name__ == '__main__':
    main()

