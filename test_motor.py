#!/usr/bin/env python3
"""
Test script for motor controller
Tests PWM signals for motor speed control
"""

from motor_controller import MotorController
import time
import config

def main():
    print("\n=== Testing Servo Controller ===")
    print(f"USE_GPIO = {config.USE_GPIO}")

    motor = MotorController(
        pwm_pin = config.MOTOR_PWM_PIN,
        frequency = config.PWM_FREQUENCY_MOTOR,
    )

    # Test center position
    print("\nDrive forward")
    motor.forward(0.5)
    time.sleep(1.0)

        # Back to center again
    print("Now stop")
    motor.stop()
    time.sleep(1.0)

    motor.cleanup()
    print("=== Test Finished ===\n")

if __name__ == "__main__":
    main()
