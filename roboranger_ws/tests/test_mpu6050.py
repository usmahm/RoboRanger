#!/usr/bin/env python3
"""
Test 2: MPU6050 IMU Test
Stream accelerometer and gyroscope data from the ESP32 and display it live.

Requires:
  - Test firmware flashed to ESP32
  - pip install pyserial

Usage:
  python3 test_mpu6050.py
  python3 test_mpu6050.py --port /dev/ttyUSB1 --duration 30

Pass criteria:
  - accel Z ≈ 9.81 m/s² when robot is flat (gravity vector)
  - accel values change when you tilt the robot
  - gyro values spike when you rotate the robot, return to ~0 when still
"""

import serial
import time
import argparse
import sys
from collections import deque

WINDOW = 20  # samples for rolling stats


def parse_imu(line: str):
    """Parse 'IMU:ax,ay,az,gx,gy,gz' → tuple of floats or None."""
    if not line.startswith("IMU:"):
        return None
    try:
        return tuple(float(v) for v in line[4:].split(","))
    except ValueError:
        return None


def fmt(val: float, unit: str = "") -> str:
    return f"{val:+8.4f}{unit}"


def main():
    ap = argparse.ArgumentParser(description="RoboRanger MPU6050 IMU test")
    ap.add_argument("--port", default="/dev/ttyUSB0")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--duration", type=int, default=60, help="Seconds to run (0 = forever)")
    args = ap.parse_args()

    print(f"Connecting to {args.port} @ {args.baud} baud…")
    try:
        ser = serial.Serial(args.port, args.baud, timeout=1.0)
    except serial.SerialException as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    time.sleep(2.0)
    ser.reset_input_buffer()

    # Drain startup messages
    time.sleep(0.3)
    while ser.in_waiting:
        msg = ser.readline().decode(errors="replace").strip()
        print(f"  [ESP32] {msg}")

    # Start IMU stream
    ser.write(b"IMU_START\n")
    time.sleep(0.1)
    while ser.in_waiting:
        print(f"  [ESP32] {ser.readline().decode(errors='replace').strip()}")

    print(f"\nStreaming IMU data (Ctrl+C to stop)…")
    print(f"{'':4}  {'Accel X':>10}  {'Accel Y':>10}  {'Accel Z':>10}  "
          f"{'Gyro X':>10}  {'Gyro Y':>10}  {'Gyro Z':>10}  {'|a|':>8}")
    print(f"{'':4}  {'(m/s²)':>10}  {'(m/s²)':>10}  {'(m/s²)':>10}  "
          f"{'(rad/s)':>10}  {'(rad/s)':>10}  {'(rad/s)':>10}  {'(m/s²)':>8}")
    print("─" * 90)

    history: deque = deque(maxlen=WINDOW)
    count = 0
    start = time.time()

    try:
        while True:
            if args.duration > 0 and (time.time() - start) > args.duration:
                break

            raw = ser.readline().decode(errors="replace").strip()
            if not raw:
                continue

            parsed = parse_imu(raw)
            if parsed is None:
                # Print non-IMU lines (WARN, INFO etc.) directly
                if raw:
                    print(f"\n  [ESP32] {raw}")
                continue

            ax, ay, az, gx, gy, gz = parsed
            magnitude = (ax**2 + ay**2 + az**2) ** 0.5
            history.append(parsed)
            count += 1

            # Clear line and print live values
            line = (f"{count:4d}  {fmt(ax,' ')} {fmt(ay,' ')} {fmt(az,' ')}  "
                    f"{fmt(gx,' ')} {fmt(gy,' ')} {fmt(gz,' ')}  {magnitude:8.4f}")
            print(f"\r{line}", end="", flush=True)

            # Every WINDOW samples print a stats summary
            if count % WINDOW == 0:
                vals = list(history)
                means = [sum(v[i] for v in vals) / len(vals) for i in range(6)]
                print(f"\n  [avg/{WINDOW}] "
                      f"ax={means[0]:+.3f} ay={means[1]:+.3f} az={means[2]:+.3f}  "
                      f"gx={means[3]:+.3f} gy={means[4]:+.3f} gz={means[5]:+.3f}")
                if abs(means[2] - 9.81) < 2.0:
                    print("  [PASS] Gravity vector on Z looks correct (~9.81 m/s²)")
                else:
                    print(f"  [WARN] Z accel mean {means[2]:.2f} — expected ~9.81 (check orientation)")

    except KeyboardInterrupt:
        pass
    finally:
        ser.write(b"IMU_STOP\n")
        ser.write(b"STOP\n")
        ser.close()
        print(f"\n\nSamples collected: {count}")
        print("Port closed.")


if __name__ == "__main__":
    main()
