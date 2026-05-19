#!/usr/bin/env python3
"""
Test 5: Serial Communication Loopback Test
Verify reliable serial communication between the Raspberry Pi and ESP32.

Requires:
  - Test firmware flashed to ESP32
  - pip install pyserial

Usage:
  python3 test_serial_comms.py
  python3 test_serial_comms.py --port /dev/ttyUSB1 --count 500

Pass criteria:
  - All ECHO messages returned correctly (0 errors)
  - Round-trip latency consistently < 20ms
  - No garbled messages
"""

import serial
import time
import argparse
import sys
import statistics


def main():
    ap = argparse.ArgumentParser(description="RoboRanger serial comms loopback test")
    ap.add_argument("--port", default="/dev/ttyUSB0")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--count", type=int, default=200, help="Number of echo rounds")
    args = ap.parse_args()

    print(f"Connecting to {args.port} @ {args.baud} baud…")
    try:
        ser = serial.Serial(args.port, args.baud, timeout=0.5)
    except serial.SerialException as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    time.sleep(2.0)
    ser.reset_input_buffer()
    time.sleep(0.3)
    while ser.in_waiting:
        ser.readline()  # drain startup messages silently

    print(f"Running {args.count} echo round-trips…\n")

    latencies = []
    errors    = 0
    timeouts  = 0

    for i in range(args.count):
        payload = f"hello_{i:04d}"
        cmd     = f"ECHO:{payload}\n"

        t0 = time.monotonic()
        ser.write(cmd.encode())

        response = ser.readline().decode(errors="replace").strip()
        t1 = time.monotonic()

        rtt_ms = (t1 - t0) * 1000

        if not response:
            timeouts += 1
            errors   += 1
            if timeouts <= 5:  # only print first few
                print(f"  [TIMEOUT] round {i} — no response")
            continue

        expected = f"ECHO:{payload}"
        if response != expected:
            errors += 1
            if errors <= 5:
                print(f"  [MISMATCH] round {i}: sent '{expected}', got '{response}'")
            continue

        latencies.append(rtt_ms)

        # Progress every 50 rounds
        if (i + 1) % 50 == 0:
            recent = latencies[-50:]
            print(f"  {i+1:4d}/{args.count}  "
                  f"last 50 avg={statistics.mean(recent):.1f}ms  "
                  f"max={max(recent):.1f}ms  errors_so_far={errors}")

    ser.close()

    # Final report
    total = args.count
    ok    = len(latencies)
    print(f"\n─── Results ────────────────────────────────────────")
    print(f"  Total rounds   : {total}")
    print(f"  Successful     : {ok}  ({100*ok/total:.1f}%)")
    print(f"  Errors/timeouts: {errors}")

    if latencies:
        print(f"  Latency min    : {min(latencies):.2f} ms")
        print(f"  Latency mean   : {statistics.mean(latencies):.2f} ms")
        print(f"  Latency p95    : {sorted(latencies)[int(0.95*len(latencies))]:.2f} ms")
        print(f"  Latency max    : {max(latencies):.2f} ms")

    if errors == 0 and latencies and statistics.mean(latencies) < 20:
        print("\n[PASS] Serial communication is reliable")
    else:
        if errors > 0:
            print(f"\n[FAIL] {errors} errors — check cable, baud rate, or firmware")
        if latencies and statistics.mean(latencies) >= 20:
            print(f"\n[WARN] Mean latency {statistics.mean(latencies):.1f}ms — expected < 20ms")


if __name__ == "__main__":
    main()
