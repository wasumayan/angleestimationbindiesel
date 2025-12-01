"""
Direction estimation module using Time Difference of Arrival (TDOA)
for 2-microphone array configuration
"""

import numpy as np
from scipy import signal
from typing import Tuple, Optional


class DirectionEstimator:
    """
    Estimates sound source direction using TDOA between two microphones
    """
    
    def __init__(self, mic_spacing: float = 0.04, sample_rate: int = 16000, 
                 speed_of_sound: float = 343.0):
        """
        Initialize direction estimator
        
        Args:
            mic_spacing: Distance between microphones in meters (default 4cm)
            sample_rate: Audio sample rate in Hz
            speed_of_sound: Speed of sound in m/s (default 343 m/s at 20°C)
        """
        self.mic_spacing = mic_spacing
        self.sample_rate = sample_rate
        self.speed_of_sound = speed_of_sound
        self.max_delay_samples = int((mic_spacing / speed_of_sound) * sample_rate) + 1
        
    def cross_correlate(self, signal1: np.ndarray, signal2: np.ndarray) -> Tuple[float, float]:
        """
        Compute cross-correlation between two signals to find time delay
        
        Args:
            signal1: First microphone signal
            signal2: Second microphone signal
            
        Returns:
            Tuple of (delay_in_samples, correlation_peak_value)
        """
        # Normalize signals
        signal1 = signal1 - np.mean(signal1)
        signal2 = signal2 - np.mean(signal2)
        
        # Compute cross-correlation
        correlation = np.correlate(signal1, signal2, mode='full')
        
        # Find the peak (excluding edges)
        search_range = slice(
            len(correlation) // 2 - self.max_delay_samples,
            len(correlation) // 2 + self.max_delay_samples + 1
        )
        correlation_window = correlation[search_range]
        peak_index = np.argmax(np.abs(correlation_window))
        
        # Convert to delay relative to center
        delay_samples = peak_index - self.max_delay_samples
        peak_value = correlation_window[peak_index]
        
        return delay_samples, peak_value
    
    def estimate_angle(self, left_channel: np.ndarray, right_channel: np.ndarray,
                      threshold: float = 0.0) -> Optional[float]:
        """
        Estimate angle of sound source relative to microphone array
        
        Args:
            left_channel: Audio from left microphone
            right_channel: Audio from right microphone
            threshold: Minimum correlation peak to consider valid (0-1)
            
        Returns:
            Angle in degrees (-90 to +90), None if signal too weak
            Positive angle = sound from right, Negative = from left
        """
        # Compute time delay
        delay_samples, peak_value = self.cross_correlate(left_channel, right_channel)
        
        # Normalize peak value for threshold check
        max_possible_correlation = np.sqrt(
            np.sum(left_channel**2) * np.sum(right_channel**2)
        )
        normalized_peak = abs(peak_value) / (max_possible_correlation + 1e-10)
        
        if normalized_peak < threshold:
            return None  # Signal too weak or noise
        
        # Convert delay to time
        delay_time = delay_samples / self.sample_rate
        
        # Calculate angle using TDOA formula
        # sin(angle) = (delay_time * speed_of_sound) / mic_spacing
        sin_angle = (delay_time * self.speed_of_sound) / self.mic_spacing
        
        # Clamp to valid range [-1, 1]
        sin_angle = np.clip(sin_angle, -1.0, 1.0)
        
        # Convert to degrees
        angle_rad = np.arcsin(sin_angle)
        angle_deg = np.degrees(angle_rad)
        
        # Determine sign based on which channel leads
        # If right channel leads (positive delay), sound is from right (positive angle)
        # If left channel leads (negative delay), sound is from left (negative angle)
        if delay_samples < 0:
            angle_deg = -angle_deg
        
        return angle_deg
    
    def smooth_angle(self, angles: list, window_size: int = 5) -> Optional[float]:
        """
        Apply moving average filter to smooth angle estimates
        
        Args:
            angles: List of recent angle estimates
            window_size: Size of smoothing window
            
        Returns:
            Smoothed angle in degrees
        """
        if not angles:
            return None
        
        # Filter out None values
        valid_angles = [a for a in angles if a is not None]
        
        if not valid_angles:
            return None
        
        # Use median filter for robustness against outliers
        window = valid_angles[-window_size:]
        return np.median(window)

