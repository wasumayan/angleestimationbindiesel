"""
Audio capture module for ReSpeaker Lite via I2S interface
Captures raw stereo audio from I2S connection
"""

import numpy as np
from typing import Tuple, Optional
import subprocess
import threading
import queue


class ReSpeakerCaptureI2S:
    """Interface for capturing audio from ReSpeaker Lite via I2S"""
    
    def __init__(self, sample_rate: int = 16000, chunk_size: int = 1024, 
                 device: str = 'hw:1,0'):
        """
        Initialize ReSpeaker I2S audio capture
        
        Args:
            sample_rate: Audio sample rate in Hz (default 16000)
            chunk_size: Number of frames per buffer
            device: ALSA device (default 'hw:1,0' for I2S)
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.device = device
        self.channels = 2
        
        self.process = None
        self.audio_queue = queue.Queue()
        self.running = False
        self.capture_thread = None
        
    def start_stream(self):
        """Start audio capture stream using arecord"""
        if self.running:
            return
        
        # Start arecord process
        cmd = [
            'arecord',
            '-D', self.device,
            '-f', 'S16_LE',
            '-r', str(self.sample_rate),
            '-c', str(self.channels),
            '-'  # Output to stdout
        ]
        
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=self.chunk_size * self.channels * 2  # 2 bytes per sample
        )
        
        self.running = True
        
        # Start capture thread
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        
        print(f"Audio stream started via I2S: {self.sample_rate}Hz, {self.channels} channels")
    
    def _capture_loop(self):
        """Background thread to capture audio"""
        bytes_per_chunk = self.chunk_size * self.channels * 2  # 2 bytes per sample
        
        while self.running and self.process:
            try:
                data = self.process.stdout.read(bytes_per_chunk)
                if len(data) == bytes_per_chunk:
                    self.audio_queue.put(data)
                elif len(data) == 0:
                    break  # Process ended
            except Exception as e:
                print(f"Error reading audio: {e}")
                break
    
    def read_chunk(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Read a chunk of audio data
        
        Returns:
            Tuple of (left_channel, right_channel) as numpy arrays
        """
        if not self.running:
            raise RuntimeError("Stream not started. Call start_stream() first.")
        
        try:
            # Get data from queue (blocking)
            data = self.audio_queue.get(timeout=1.0)
        except queue.Empty:
            raise RuntimeError("No audio data available")
        
        # Convert to numpy array
        audio_data = np.frombuffer(data, dtype=np.int16)
        
        # Reshape for stereo channels
        audio_data = audio_data.reshape(-1, self.channels)
        
        # Return left and right channels separately
        left_channel = audio_data[:, 0].astype(np.float32) / 32768.0
        right_channel = audio_data[:, 1].astype(np.float32) / 32768.0
        
        return left_channel, right_channel
    
    def stop_stream(self):
        """Stop audio capture stream"""
        self.running = False
        
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
        
        if self.capture_thread:
            self.capture_thread.join(timeout=1.0)
    
    def cleanup(self):
        """Clean up audio resources"""
        self.stop_stream()
        # Clear queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

