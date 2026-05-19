#!/usr/bin/env python3
"""
Test 6: Full Mecanum Motion Test
Command all 4 motors together through a sequence of mecanum movements.

Requires:
  - Test firmware flashed to ESP32
  - pip install pyserial
  - Robot on the floor with space to move

Usage:
  python3 test_mecanum_motion.py
  python3 test_mecanum_motion.py --speed 100 --duration 2.0

Mecanum wheel direction reference (standard layout, rollers at 45°):
  Forward   : FL=F  FR=F  RL=F  RR=F
  Backward  : FL=B  FR=B  RL=B  RR=B
  Strafe R  : FL=F  FR=B  RL=B  RR=F
  Strafe L  : FL=B  FR=F  RL=F  RR=B
  Rotate CW : FL=F  FR=B  RL=F  RR=B
  Rotate CCW: FL=B  FR=F  RL=B  RR=F

Pass criteria:
  - Robot moves distinctly in each described direction
  - No wheel fighting (vibration/stalling indicates wrong direction on a motor)
  - If a direction is wrong, note which motor and swap IN1/IN2 in the firmware pins.
"""

import serial
import time
import argparse
import sys

# (FL, FR, RL, RR) directions for each motion
MOTIONS = [
    ("Forward",    ("F", "F", "F", "F")),
    ("Backward",   ("B", "B", "B", "B")),
    ("Strafe R",   ("F", "B", "B", "F")),
    ("Strafe L",   ("B", "F", "F", "B")),
    ("Rotate CW",  ("F", "B", "F", "B")),
    ("Rotate CCW", ("B", "F", "B", "F")),
]


def send(ser: serial.Serial, cmd: str):
    ser.write((cmd + "\n").encode())
    time.sleep(0.05)
    while ser.in_waiting:
        ser.readline()  # discard OK responses during motion


def set_motors(ser: serial.Serial, dirs: tuple, speed: int):
    for idx, d in enumerate(dirs):
        ser.write(f"MOTOR:{idx}:{d}:{speed}\n".encode())
    time.sleep(0.05)
    while ser.in_waiting:
        ser.readline()


def all_stop(ser: serial.Serial):
    send(ser, "STOP")


def main():
    ap = argparse.ArgumentParser(description="RoboRanger mecanum motion test")
    ap.add_argument("--port", default="/dev/ttyUSB0")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--speed", type=int, default=150,
                    help="Motor PWM speed (0-255). Start low, increase if needed.")
    ap.add_argument("--duration", type=float, default=2.0,
                    help="Seconds per motion")
    ap.add_argument("--pause", type=float, default=1.0,
                    help="Pause between motions (seconds)")
    args = ap.parse_args()

    print(f"Connecting to {args.port} @ {args.baud} baud…")
    try:
        ser = serial.Serial(args.port, args.baud, timeout=1.0)
    except serial.SerialException as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    time.sleep(2.0)
    ser.reset_input_buffer()
    time.sleep(0.3)
    while ser.in_waiting:
        print(f"  [ESP32] {ser.readline().decode(errors='replace').strip()}")

    print(f"\nSpeed: {args.speed}/255   Duration: {args.duration}s   Pause: {args.pause}s")
    print("CLEAR THE AREA — robot will move!\n")
    print("Press Enter to start, or Ctrl+C to abort.")
    try:
        input()
    except KeyboardInterrupt:
        ser.close()
        sys.exit(0)

    results = []

    try:
        for name, dirs in MOTIONS:
            label = f"FL={dirs[0]}  FR={dirs[1]}  RL={dirs[2]}  RR={dirs[3]}"
            print(f"▶  {name:<12} ({label})  …", end="", flush=True)
            set_motors(ser, dirs, args.speed)
            time.sleep(args.duration)
            all_stop(ser)
            print(" STOP")

            # Ask user to confirm
            try:
                ok = input(f"   Did the robot move {name.lower()}? [y/n/s(skip)]: ").strip().lower()
            except EOFError:
                ok = "s"

            if ok == "y":
                results.append((name, "PASS"))
                print(f"   [PASS]\n")
            elif ok == "n":
                results.append((name, "FAIL"))
                print(f"   [FAIL] — check motor directions in firmware pin config\n")
            else:
                results.append((name, "SKIP"))
                print(f"   [SKIP]\n")

            time.sleep(args.pause)

    except KeyboardInterrupt:
        print("\nAborted.")
    finally:
        all_stop(ser)
        ser.close()

    # Summary
    print("─── Motion Test Results ────────────────────────────")
    for name, status in results:
        icon = "✓" if status == "PASS" else ("✗" if status == "FAIL" else "─")
        print(f"  {icon}  {name:<12}  {status}")

    failed = [n for n, s in results if s == "FAIL"]
    if not results:
        print("\nNo results recorded.")
    elif not failed:
        print("\n[PASS] All tested motions correct — mecanum kinematics working!")
    else:
        print(f"\n[FAIL] {len(failed)} motion(s) incorrect: {', '.join(failed)}")
        print("  To fix: swap IN1/IN2 pins for the offending motor in firmware/roboranger_esp32/src/main.cpp")
        print("  Tip: start with just 'Forward' — all 4 wheels must spin the same direction.")


if __name__ == "__main__":
    main()
