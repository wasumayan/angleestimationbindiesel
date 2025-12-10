"""
Time-of-Flight (TOF) Sensor Module
VL53L0X distance sensor for obstacle detection and user proximity
"""

import config
import time
from model_GPIO import ModelGPIO

if config.USE_GPIO:
    import RPi.GPIO as GPIO

else: 
    GPIO = ModelGPIO()

class ToFSensor:
    def __init__(self):
        if config.USE_GPIO:
            GPIO.setmode(GPIO.BCM)
            # Use pull-down resistor to help with noisy signals (anything below ~1.6V will read as LOW)
            GPIO.setup(config.ToF_DIGITAL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        # Simple debouncing: require multiple consecutive HIGH readings
        self.high_count = 0
        self.high_threshold = getattr(config, 'TOF_HIGH_COUNT_THRESHOLD', 3)

        if config.DEBUG_TOF:
            print(f"[ToF] Initialized digital input on pin {config.ToF_DIGITAL_PIN} with pull-down resistor")

    def state(self) -> bool:
        if config.USE_GPIO:    
           raw_val = GPIO.input(config.ToF_DIGITAL_PIN)
           # Filter noise: require multiple consecutive HIGH readings
           if raw_val:
               self.high_count += 1
           else:
               self.high_count = 0
           # Only return HIGH if we have enough consecutive HIGH readings
           val = (self.high_count >= self.high_threshold)
        else: 
            val = False
        
        if config.DEBUG_TOF:
            print(f"[ToF] State -> {val} (raw={raw_val if config.USE_GPIO else 'N/A'}, count={self.high_count})")

        return val
    
    def detect(self) -> bool: 
        state = self.state()

        if config.DEBUG_TOF:
            print(f"[TOF] detect -> {state}")

        return state 