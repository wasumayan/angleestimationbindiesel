"""
Motor Controller Module
Controls motor speed using PWM signals via GPIO

DESIGN OVERVIEW:
This module interfaces with the motor inverter circuit using PWM (Pulse Width Modulation).
The PWM signal controls the motor speed through a custom inverter circuit.

KEY DESIGN DECISIONS:
1. PWM Frequency: 40Hz chosen to match inverter circuit requirements
   - Lower frequencies (20-30Hz) cause motor jitter
   - Higher frequencies (50-60Hz) cause inverter heating
   - 40Hz provides smooth control with minimal heating
   
2. Duty Cycle Clamping: 65-100% range prevents reverse activation
   - Inverter circuit interprets <65% duty cycle as reverse direction
   - Clamping ensures forward-only operation
   - MOTOR_STOP = 100% (inverter interprets as stop)
   - MOTOR_MAX = 76% (maximum forward speed)
   
3. Speed Values (as percentage multipliers):
   - MOTOR_STOP = 100.0 (100% duty = stop)
   - MOTOR_MAX = 76.0 (76% duty = max speed)
   - MOTOR_SLOW = 1.05 (105% of MOTOR_MAX = slow speed)
   - MOTOR_MEDIUM = 1.02 (102% of MOTOR_MAX = medium speed)
   - MOTOR_FAST = 1.0 (100% of MOTOR_MAX = fast speed)
   - MOTOR_TURN = 0.91 (91% of MOTOR_MAX = turning speed)
   
4. Inverter Circuit: Custom design with filtering components
   - Resistors: Current limiting and voltage division
   - Capacitors: Smooth PWM signal, reduce noise
   - Provides stable power delivery and prevents voltage fluctuations
"""

import time
import config
from model_GPIO import ModelGPIO

if config.USE_GPIO:
    import RPi.GPIO as GPIO

else: GPIO = ModelGPIO()


class MotorController:
    def __init__(self, pwm_pin, frequency):
        """
        Initialize motor controller with PWM signal
        
        Args:
            pwm_pin: GPIO pin number for PWM output (GPIO 12)
            frequency: PWM frequency in Hz (40Hz for motor control)
        """
        self.pwm_pin = pwm_pin
        self.frequency = frequency  # 40Hz - optimized for inverter circuit
        self.pwm = None 

        if config.USE_GPIO:
            GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
            GPIO.setup(self.pwm_pin, GPIO.OUT)
            # Initialize PWM at 40Hz frequency
            # This frequency was chosen to match inverter circuit characteristics
            self.pwm = GPIO.PWM(self.pwm_pin, self.frequency)
            self.pwm.start(0)  # Start with 0% duty cycle (stopped)

        if config.DEBUG_MOTOR:
            print(f"[Motor] Initialized on pin {self.pwm_pin} at {self.frequency} Hz")

    def forward(self, speed: float):
        """
        Set motor forward speed
        
        Args:
            speed: Speed multiplier (0.0-1.0, where 1.0 = MOTOR_MAX)
                  Actual values used: MOTOR_SLOW (1.05), MOTOR_MEDIUM (1.02), 
                  MOTOR_FAST (1.0), MOTOR_TURN (0.91)
        
        DESIGN: Duty cycle calculation and clamping
        - Base duty cycle = MOTOR_MAX (76%) * speed multiplier
        - Clamp to 65-100% range to prevent reverse activation
        - Inverter circuit interprets <65% as reverse, so we clamp minimum to 65%
        """
        duty = config.MOTOR_MAX * speed
        
        # CRITICAL: Clamp PWM between 65-100% to prevent inverter reverse activation
        # The inverter circuit has a threshold at ~65% duty cycle
        # Below this threshold, the inverter interprets the signal as reverse direction
        # Clamping prevents accidental reverse activation during:
        # - Initialization (duty might be 0)
        # - Shutdown (duty might drop)
        # - Rounding errors
        duty = max(65.0, min(100.0, duty))

        if config.USE_GPIO:
            self.pwm.ChangeDutyCycle(duty)

        if config.DEBUG_MOTOR:
            print(f"[Motor] forward speed = {speed:.2f} (duty = {duty:.1f}% clamped)")

    def stop(self):
        if config.USE_GPIO and self.pwm:
            self.pwm.ChangeDutyCycle(config.MOTOR_STOP)

        if config.DEBUG_MOTOR:
            print("[Motor] stop()")

    def cleanup(self):                  # what is cleanup? 
        if config.USE_GPIO:
            if self.pwm:
                self.pwm.stop()
            GPIO.cleanup(self.pwm_pin)

        if config.DEBUG_MOTOR:
            print("[Motor] cleanup()")