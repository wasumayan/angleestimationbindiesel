#!/usr/bin/env python3
"""
Test script for TOF sensor
Tests VL53L0X distance measurement
"""

import time
from tof_sensor import ToFSensor
import config

def main():
    print("\n === Testing Tof Sensor ===")
    print(f"USE_GPIO = {config.USE_GPIO}")

    tof = ToFSensor()

    print(f"ToF initial state", tof.detect())


if __name__ == '__main__':
    main()

