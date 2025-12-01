"""
Audio capture module for ReSpeaker Lite 2-mic array
Captures audio from USB microphone array and provides raw audio data
"""

import pyaudio
import numpy as np
from typing import Tuple, Optional


class ReSpeakerCapture:
    """Interface for capturing audio from ReSpeaker Lite microphone array"""
    
    def __init__(self, sample_rate: int = 16000, chunk_size: int = 1024, 
                 channels: int = 2, device_index: Optional[int] = None):
        """
        Initialize ReSpeaker audio capture
        
        Args:
            sample_rate: Audio sample rate in Hz (default 16000)
            chunk_size: Number of frames per buffer
            channels: Number of audio channels (2 for stereo mic array)
            device_index: Specific audio device index (None for auto-detect)
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.channels = channels
        self.device_index = device_index
        
        self.audio = pyaudio.PyAudio()
        self.stream = None
        
    def find_respeaker_device(self) -> Optional[int]:
        """Find ReSpeaker device index by searching for device name"""
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            device_name = info.get('name', '').lower()
            if 'respeaker' in device_name or 'seeed' in device_name:
                print(f"Found ReSpeaker device: {info['name']} at index {i}")
                return i
        print("Warning: ReSpeaker device not found, using default input device")
        return None
    
    def start_stream(self):
        """Start audio capture stream"""
        if self.device_index is None:
            self.device_index = self.find_respeaker_device()
        
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            input_device_index=self.device_index,
            frames_per_buffer=self.chunk_size
        )
        self.stream.start_stream()
        print(f"Audio stream started: {self.sample_rate}Hz, {self.channels} channels")
    
    def read_chunk(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Read a chunk of audio data
        
        Returns:
            Tuple of (left_channel, right_channel) as numpy arrays
        """
        if self.stream is None:
            raise RuntimeError("Stream not started. Call start_stream() first.")
        
        data = self.stream.read(self.chunk_size, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        
        # Reshape for stereo channels
        audio_data = audio_data.reshape(-1, self.channels)
        
        # Return left and right channels separately
        left_channel = audio_data[:, 0].astype(np.float32) / 32768.0
        right_channel = audio_data[:, 1].astype(np.float32) / 32768.0
        
        return left_channel, right_channel
    
    def stop_stream(self):
        """Stop audio capture stream"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
    
    def cleanup(self):
        """Clean up audio resources"""
        self.stop_stream()
        self.audio.terminate()

