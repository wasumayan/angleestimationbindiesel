#!/usr/bin/env python3
"""
Bin Diesel Minimal Main Control System
Version: camera + wake word + TOF digital + PWM out
"""

import time
import os
import sys
from pathlib import Path

# Add parent directory to path if needed
sys.path.insert(0, str(Path(__file__).parent))

import config
from state_machine import StateMachine, State
from wake_word_detector import WakeWordDetector
from visual_detector import VisualDetector
from motor_controller import MotorController
from servo_controller import ServoController
from tof_sensor import TOFSensor


class BinDieselSystem:
    def __init__(self):
        print("=" * 60)
        print("Bin Diesel (minimal) starting up...")
        print("=" * 60)

        # State machine
        self.sm = StateMachine()

        # Wake word
        print("[Main] Initializing wake word detector...")
        wake_word_model_path = config.WAKE_WORD_MODEL_PATH if hasattr(config, "WAKE_WORD_MODEL_PATH") else \
            os.path.join(os.path.dirname(__file__), "bin-diesel_en_raspberry-pi_v3_0_0", "bin-diesel_en_raspberry-pi_v3_0_0.ppn")
        self.wake = WakeWordDetector(
            model_path=wake_word_model_path,
            access_key=getattr(config, "WAKE_WORD_ACCESS_KEY", None)
        )
        self.wake.start_listening()

        # Visual detector (angle + person detection)
        print("[Main] Initializing visual detector...")
        self.visual = VisualDetector(
            model_path=getattr(config, "YOLO_MODEL", "yolo11n.pt"),
            width=getattr(config, "CAMERA_WIDTH", 640),
            height=getattr(config, "CAMERA_HEIGHT", 480),
            confidence=getattr(config, "YOLO_CONFIDENCE", 0.25)
        )

        # Motor + servo
        print("[Main] Initializing motor + servo...")
        self.motor = MotorController(
            pwm_pin=config.MOTOR_PWM_PIN,
            frequency=config.PWM_FREQUENCY_MOTOR
        )
        self.servo = ServoController(
            pwm_pin=config.SERVO_PWM_PIN,
            frequency=config.PWM_FREQUENCY_SERVO,
            center_duty=config.SERVO_CENTER_DUTY,
            left_max_duty=config.SERVO_LEFT_MAX_DUTY,
            right_max_duty=config.SERVO_RIGHT_MAX_DUTY
        )

        # TOF (digital input from Arduino)
        print("[Main] Initializing TOF (digital input)...")
        self.tof = TOFSensor(
            stop_distance_mm=None,
            emergency_distance_mm=None
        )

        # For forward/return timing
        self.forward_start_time = None
        self.forward_duration   = 0.0

        print("=" * 60)
        print("System ready. Say 'bin diesel' to start.")
        print("=" * 60)

    # ---------------- STATE HANDLERS ----------------

    def handle_idle(self):
        """
        IDLE: wait for wake word.
        """
        if self.wake.detect():
            print("[Main] Wake word detected; starting forward drive.")
            self.servo.center()
            self.motor.forward(config.MOTOR_FORWARD_SPEED)

            self.forward_start_time = time.time()
            self.sm.transition_to(State.DRIVING_TO_USER)

    def handle_driving_to_user(self):
        """
        DRIVING_TO_USER: follow the person using camera angle.
        Stop when TOF digital says "close enough".
        """
        # Update vision
        result = self.visual.update()

        if result["person_detected"]:
            angle = result["angle"] or 0.0
            # Option: clamp angle to [-45, +45]
            if angle < -45.0:
                angle = -45.0
            if angle > 45.0:
                angle = 45.0
            self.servo.set_angle(angle)
        else:
            # If we lose the person, you might just center servo
            self.servo.center()

        # Check TOF
        if self.tof.is_too_close():
            print("[Main] TOF triggered - stopping at user.")
            self.motor.stop()
            self.servo.center()

            # Record how long we drove forward
            if self.forward_start_time is not None:
                self.forward_duration = time.time() - self.forward_start_time
            else:
                self.forward_duration = 0.0

            print(f"[Main] Forward duration = {self.forward_duration:.2f}s")

            self.sm.transition_to(State.STOPPED_AT_USER)

    def handle_stopped_at_user(self):
        """
        STOPPED_AT_USER: wait fixed time, then start returning.
        """
        t = self.sm.get_time_in_state()
        if t == 0:
            # just entered
            print("[Main] Waiting for trash drop-off...")
        if t >= config.STOP_HOLD_SECONDS:
            print("[Main] Done waiting; returning to start.")
            # Turn 180°: crude version: servo hard left/right + motor forward a bit.
            self.servo.set_angle(45.0)  # for example
            self.motor.forward(config.MOTOR_FORWARD_SPEED)
            time.sleep(1.5)  # tune this later
            self.motor.stop()
            self.servo.center()

            # Now drive back for same duration as forward
            self.return_start_time = time.time()
            self.motor.forward(config.MOTOR_RETURN_SPEED)
            self.sm.transition_to(State.RETURNING)

    def handle_returning(self):
        """
        RETURNING: drive back for same time we drove forward (plus margin),
        then stop and go to IDLE.
        """
        elapsed = time.time() - self.return_start_time
        total = self.forward_duration + config.RETURN_EXTRA_MARGIN

        if elapsed >= total:
            print("[Main] Return complete, entering IDLE.")
            self.motor.stop()
            self.servo.center()
            self.sm.transition_to(State.IDLE)

    # ---------------- MAIN LOOP ----------------

    def run(self):
        try:
            while True:
                state = self.sm.get_state()

                if state == State.IDLE:
                    self.handle_idle()

                elif state == State.DRIVING_TO_USER:
                    self.handle_driving_to_user()

                elif state == State.STOPPED_AT_USER:
                    self.handle_stopped_at_user()

                elif state == State.RETURNING:
                    self.handle_returning()

                time.sleep(0.01)

        except KeyboardInterrupt:
            print("\n[Main] Interrupted by user.")
        finally:
            self.cleanup()

    def cleanup(self):
        print("[Main] Cleaning up...")
        self.motor.stop()
        self.servo.center()

        self.wake.stop()
        self.visual.stop()
        self.motor.cleanup()
        self.servo.cleanup()
        print("[Main] Cleanup complete.")


if __name__ == "__main__":
    # you can also load .env here if needed
    system = BinDieselSystem()
    system.run()
