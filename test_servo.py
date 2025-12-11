"""
Test script for ServoController without hardware
"""

from servo_controller import ServoController
from motor_controller import MotorController
import time
import config

def main():
    print("\n=== Testing Servo Controller ===")
    print(f"USE_GPIO = {config.USE_GPIO}")

    servo = ServoController(
        pwm_pin = config.SERVO_PWM_PIN,
        frequency = config.PWM_FREQUENCY_SERVO,
        center_duty = config.SERVO_CENTER,
        left_max_duty = config.SERVO_LEFT_MAX,
        right_max_duty = config.SERVO_RIGHT_MAX
    )

    motor = MotorController(
            pwm_pin=config.MOTOR_PWM_PIN,
            frequency=config.PWM_FREQUENCY
        )
    
    motor.stop()

    # Test center position
    print("\nCentering servo")
    servo.center()
    time.sleep(3.0 )

    motor.forward(config.MOTOR_SLOW)


# Turn left
    print("Turning left to -30°...")
    servo.set_angle(-30.0)
    time.sleep(3.0)



        # Back to center again
    print("Back to center again...")
    servo.center()
    time.sleep(1.0)

    servo.cleanup()
    print("=== Test Finished ===\n")

if __name__ == "__main__":
    main()
