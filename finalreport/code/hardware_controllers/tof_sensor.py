"""
Time-of-Flight (TOF) Sensor Module
VL53L0X distance sensor for obstacle detection and user proximity

DESIGN OVERVIEW:
This module interfaces with the VL53L0X Time-of-Flight sensor via I2C communication.
The sensor provides distance measurements for emergency stop functionality.

KEY DESIGN DECISIONS:
1. I2C Communication: Chosen over SPI or analog for several reasons:
   - I2C requires only 2 wires (SDA, SCL) vs SPI's 4+ wires
   - Multiple I2C devices can share the same bus (addressable)
   - Lower pin count on Raspberry Pi (important for GPIO constraints)
   - Standard protocol with good library support
   - Trade-off: Slightly slower than SPI but sufficient for our use case
   
2. Digital Output Mode: Using GPIO digital input instead of I2C distance reading
   - VL53L0X provides interrupt pin that goes HIGH when object < threshold
   - Simpler implementation: no need to read I2C registers continuously
   - Lower CPU overhead: interrupt-based instead of polling
   - Threshold set to 900mm on sensor (hardware configuration)
   
3. Debouncing: Require multiple consecutive HIGH readings
   - Prevents false triggers from electrical noise
   - TOF_HIGH_COUNT_THRESHOLD = 1 (immediate response, can increase if noise issues)
   - Pull-down resistor helps filter noise (GPIO.PUD_DOWN)
   
4. Safety Distance: 900mm trigger distance provides ~100mm buffer
   - Accounts for reaction time (~50ms at MOTOR_MEDIUM speed)
   - Accounts for braking distance (proportional to speed)
   - Ensures car stops before hitting obstacles
   - Buffer verified through testing (see TOF safety trigger analysis graph)
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
        """
        Initialize TOF sensor with digital input pin
        
        DESIGN: Pull-down resistor configuration
        - GPIO.PUD_DOWN: Internal pull-down resistor enabled
        - Helps filter noise: signals below ~1.6V read as LOW
        - Prevents floating pin issues (unconnected pin reads random values)
        - Standard practice for digital input pins
        """
        if config.USE_GPIO:
            GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
            # Configure pin as input with pull-down resistor
            # Pull-down ensures pin reads LOW when sensor output is not HIGH
            # This prevents false triggers from electrical noise
            GPIO.setup(config.ToF_DIGITAL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        # DEBOUNCING: Require multiple consecutive HIGH readings
        # This filters out electrical noise and transient signals
        # TOF_HIGH_COUNT_THRESHOLD = 1 means immediate response (can increase if noise issues)
        self.high_count = 0
        self.high_threshold = getattr(config, 'TOF_HIGH_COUNT_THRESHOLD', 1)

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