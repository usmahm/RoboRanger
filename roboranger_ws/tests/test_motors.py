#!/usr/bin/env python3
"""
Test 1: Motor Hardware Test
Verify each of the 4 motors spins in the correct direction at commanded speed.

Requires:
  - Test firmware flashed to ESP32
  - ESP32 connected to this machine via USB
  - pip install pyserial

Usage:
  python3 test_motors.py                    # interactive mode
  python3 test_motors.py --auto             # automated sequence
  python3 test_motors.py --port /dev/ttyUSB1
"""

import serial
import time
import argparse
import sys

MOTOR_NAMES = {0: "FL (Front-Left)", 1: "FR (Front-Right)",
               2: "RL (Rear-Left)",  3: "RR (Rear-Right)"}


def send(ser: serial.Serial, cmd: str, wait: float = 0.05) -> str:
    ser.write((cmd + "\n").encode())
    time.sleep(wait)
    lines = []
    while ser.in_waiting:
        lines.append(ser.readline().decode(errors="replace").strip())
    return " | ".join(lines)


def motor(ser, idx: int, direction: str, speed: int) -> str:
    """direction: 'F' forward, 'B' backward, 'S' stop"""
    return send(ser, f"MOTOR:{idx}:{direction}:{speed}", wait=0.1)


def run_auto(ser: serial.Serial):
    print("\n=== AUTO MOTOR SEQUENCE ===")
    print("Watch each motor spin. Each should move only the labelled wheel.\n")

    for idx, name in MOTOR_NAMES.items():
        print(f"── Motor {idx} — {name} ──")
        for spd, label in [(128, "half"), (220, "fast")]:
            print(f"  Forward  @ {label} speed ({spd})…")
            r = motor(ser, idx, "F", spd)
            print(f"    [{r}]")
            time.sleep(2.5)

        print(f"  Backward @ half speed (128)…")
        r = motor(ser, idx, "B", 128)
        print(f"    [{r}]")
        time.sleep(2.5)

        print(f"  Stop.")
        motor(ser, idx, "S", 0)
        time.sleep(0.8)
        print()

    print("=== DONE — all motors tested ===\n")


def run_interactive(ser: serial.Serial):
    print("\n=== INTERACTIVE MOTOR TEST ===")
    print("Commands:")
    print("  <id> <dir> <speed>   e.g.  '0 F 128'  →  FL motor, forward, half-speed")
    print("  stop                 Stop all motors")
    print("  auto                 Run automatic sequence")
    print("  quit                 Exit")
    print()
    print("  Motor IDs:  0=FL  1=FR  2=RL  3=RR")
    print("  Direction:  F=forward  B=backward  S=stop")
    print("  Speed:      0-255\n")

    while True:
        try:
            raw = input("cmd> ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not raw:
            continue
        low = raw.lower()

        if low == "quit":
            break
        elif low == "stop":
            print(f"  {send(ser, 'STOP')}")
        elif low == "auto":
            run_auto(ser)
        else:
            parts = raw.split()
            if len(parts) != 3:
                print("  Usage: <id 0-3> <dir F/B/S> <speed 0-255>")
                continue
            try:
                idx = int(parts[0])
                d   = parts[1].upper()
                spd = int(parts[2])
            except ValueError:
                print("  Bad values. Example: 0 F 128")
                continue
            if idx not in range(4) or d not in ("F", "B", "S"):
                print("  id must be 0-3, dir must be F/B/S")
                continue
            r = motor(ser, idx, d, spd)
            print(f"  {r}")


def main():
    ap = argparse.ArgumentParser(description="RoboRanger motor hardware test")
    ap.add_argument("--port", default="/dev/ttyUSB0")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--auto", action="store_true", help="Run automated sequence")
    args = ap.parse_args()

    print(f"Connecting to {args.port} @ {args.baud} baud…")
    try:
        ser = serial.Serial(args.port, args.baud, timeout=1.0)
    except serial.SerialException as e:
        print(f"ERROR: {e}")
        print("Check the port with:  ls /dev/ttyUSB*  or  ls /dev/ttyACM*")
        sys.exit(1)

    time.sleep(2.0)       # ESP32 reboot on DTR
    ser.reset_input_buffer()

    # Drain startup messages
    time.sleep(0.3)
    while ser.in_waiting:
        print(f"  [ESP32] {ser.readline().decode(errors='replace').strip()}")

    try:
        if args.auto:
            run_auto(ser)
        else:
            run_interactive(ser)
    finally:
        send(ser, "STOP")
        ser.close()
        print("Port closed.")


if __name__ == "__main__":
    main()
