"""
Servo Controller Module
Controls steering servo using PWM signals via GPIO
"""

import time
import config

if config.USE_GPIO:
    import RPi.GPIO as GPIO


class ServoController:
    def _init_(self, pwm_pin, frequency, center, l_max, r_max):
        self.pwm_pin = pwm_pin
        self.frequency = frequency
        self.center_duty = center
        self.left_max_duty = l_max
        self.right_max_duty = r_max
        self.pwm = None

        if config.USE_GPIO:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pwm_pin, GPIO.OUT)
            self.pwm = GPIO.PWM(self.pwm_pin, self.frequency)
            self.pwm.start(self.center_duty)

        if config.DEBUG_SERVO:
            print(f"[Servo] Initialized on pin {self.pwm_pin} at {self.frequency} Hz")

    def _set_duty(self, duty):
        duty = max(min(duty, self.left_max_duty), self.right_max_duty)

        if config.USE_GPIO and self.pwm:
            self.pwm.ChangeDutyCycle(duty)

        if config.DEBUG_SERVO:
            print(f"[Servo] duty = {duty:.2f}%")

    def center(self):
        if config.DEBUG_SERVO:
            print("[Servo] center()")
        self._set_duty(self.center_duty)

    def set_angle(self, angle_deg: float):
        if angle_deg < -45.0:
            angle_deg = -45.0
        if angle_deg > 45.0:
            angle_deg = 45.0 

        if angle_deg >= 0:
            duty = self.center_duty + (self.right_max_duty - self.center_duty) * (angle_deg / 45.0)
        else:
            duty = self.center_duty + (self.left_max_duty - self.center_duty) * (angle_deg / -45.0)

        if config.DEBUG.SERVO:
            print(f"[Servo] set_angle({angle_deg:.1f}) degrees -> duty = {duty:.2f}%")

        self._set_duty(duty)

    def cleanup(self):
        if config.USE_GPIO:
            if self.pwm:
                self.pwm.stop()
            GPIO.cleanup(self.pwm_pin)

        if config.DEBUG_SERVO:
            print("[Servo] cleanup()")

