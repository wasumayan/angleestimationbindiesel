"""
Time-of-Flight (TOF) Sensor Module
VL53L0X distance sensor for obstacle detection and user proximity
"""

import config
import time

if config.USE_GPIO:
    import RPi.GPIO as GPIO

class ToFSensor:
    def _init_(self, stop_distance_mm=None):
        self.stop_distance_mm = stop_distance_mm

        if config.USE_GPIO:
            GPIO.setmode(GPIO.BCM))
            GPIO.setup(config.ToF_DIGITAL_PIN, GPIO.IN)

        if config.DEBUG_TOF:
            print(f"[ToF] Initialized digital input on pin {config.Tof_DIGITAL_PIN}")

    def _state(self) -> bool:
        if not config.USE_GPIO:
            return False 
        
        val = bool(GPIO.input(config.Tof_DIGITAL_PIN))
        return val if config.ToF_ACTIVE_HIGH else not val 
    
    def detect(self) -> bool: 
        state = self._state()

        if config.DEBUG_TOF:
            print(f"[TOF] detect -> {state}")

        return state 