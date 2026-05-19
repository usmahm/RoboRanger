#!/usr/bin/env python3
"""
Keyboard Teleoperation Test
Drive the robot interactively from the keyboard. Toggle motions on/off,
adjust speed, and rotate in place — no ROS2 required.

Usage:
  python3 test_teleop_keyboard.py
  python3 test_teleop_keyboard.py --port /dev/ttyUSB0 --speed 150

Key bindings:
  w / s       Forward / Backward
  a / d       Strafe Left / Strafe Right
  q / e       Rotate CCW / Rotate CW
  Space       Stop
  + or =      Increase speed by 20
  -           Decrease speed by 20
  i           Toggle IMU stream
  Ctrl+C      Quit
"""

import argparse
import sys
import termios
import threading
import time
import tty

import serial

MOTION_MAP = {
    'w': ("Forward",    ("F", "F", "F", "F")),
    's': ("Backward",   ("B", "B", "B", "B")),
    'd': ("Strafe R",   ("F", "B", "B", "F")),
    'a': ("Strafe L",   ("B", "F", "F", "B")),
    'e': ("Rotate CW",  ("F", "B", "F", "B")),
    'q': ("Rotate CCW", ("B", "F", "B", "F")),
}

SPEED_STEP = 20
SPEED_MIN  = 40
SPEED_MAX  = 255
WATCHDOG_INTERVAL = 0.15  # seconds — well under the 500ms watchdog


def set_motors(ser: serial.Serial, dirs: tuple, speed: int):
    for idx, d in enumerate(dirs):
        ser.write(f"MOTOR:{idx}:{d}:{speed}\n".encode())
    time.sleep(0.02)
    while ser.in_waiting:
        ser.readline()


def all_stop(ser: serial.Serial):
    ser.write(b"STOP\n")
    time.sleep(0.05)
    while ser.in_waiting:
        ser.readline()


def print_status(motion_name: str, speed: int, imu_on: bool):
    motion_str = motion_name if motion_name else "STOPPED"
    imu_str    = "IMU:ON" if imu_on else "IMU:OFF"
    hint = "w/s/a/d=move  q/e=rotate  space=stop  +/-=speed  i=IMU  ^C=quit"
    print(f"\r\033[K[{motion_str} | speed={speed}/255 | {imu_str}]  {hint}", end="", flush=True)


def watchdog_thread(ser: serial.Serial, state: dict, stop_event: threading.Event):
    while not stop_event.is_set():
        dirs = state.get("dirs")
        if dirs:
            set_motors(ser, dirs, state["speed"])
        stop_event.wait(WATCHDOG_INTERVAL)


def main():
    ap = argparse.ArgumentParser(description="RoboRanger keyboard teleoperation")
    ap.add_argument("--port",  default="/dev/ttyUSB0")
    ap.add_argument("--baud",  type=int, default=115200)
    ap.add_argument("--speed", type=int, default=150, help="Initial PWM speed (0-255)")
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

    state = {
        "dirs":  None,
        "speed": max(SPEED_MIN, min(SPEED_MAX, args.speed)),
        "name":  "",
        "imu":   False,
    }

    stop_event = threading.Event()
    wdog = threading.Thread(target=watchdog_thread, args=(ser, state, stop_event), daemon=True)
    wdog.start()

    old_tty = termios.tcgetattr(sys.stdin)
    print("\nReady. Use keyboard to drive the robot.\n")
    print_status(state["name"], state["speed"], state["imu"])

    try:
        tty.setraw(sys.stdin.fileno())
        while True:
            ch = sys.stdin.read(1)

            if ch == '\x03':  # Ctrl+C
                break

            elif ch in MOTION_MAP:
                name, dirs = MOTION_MAP[ch]
                # Toggle off if same key pressed again
                if state["dirs"] == dirs:
                    state["dirs"] = None
                    state["name"] = ""
                    all_stop(ser)
                else:
                    state["name"] = name
                    state["dirs"] = dirs

            elif ch == ' ':
                state["dirs"] = None
                state["name"] = ""
                all_stop(ser)

            elif ch in ('+', '='):
                state["speed"] = min(SPEED_MAX, state["speed"] + SPEED_STEP)

            elif ch == '-':
                state["speed"] = max(SPEED_MIN, state["speed"] - SPEED_STEP)

            elif ch == 'i':
                state["imu"] = not state["imu"]
                cmd = "IMU_START" if state["imu"] else "IMU_STOP"
                ser.write((cmd + "\n").encode())
                time.sleep(0.05)
                while ser.in_waiting:
                    line = ser.readline().decode(errors="replace").strip()
                    if line.startswith("IMU:"):
                        pass  # drop IMU data lines silently
                    # OK responses discarded too

            print_status(state["name"], state["speed"], state["imu"])

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)
        stop_event.set()
        wdog.join(timeout=1.0)
        all_stop(ser)
        ser.close()
        print("\nStopped. Bye.")


if __name__ == "__main__":
    main()
