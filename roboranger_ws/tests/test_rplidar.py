#!/usr/bin/env python3
"""
Test 3: RPLidar Hardware Test
Verify the RPLidar is scanning and returning sensible distance measurements.

Requires:
  - pip install rplidar-roboticia
  - RPLidar connected via USB (NOT the ESP32 port)

Usage:
  python3 test_rplidar.py
  python3 test_rplidar.py --port /dev/ttyUSB1 --scans 5

Pass criteria:
  - Lidar spins and reports valid distances
  - Min/max range values look sensible for the room (~0.15 m – 12 m for A1)
  - No zero-quality measurements dominate the scan
"""

import argparse
import sys
import time

try:
    from rplidar import RPLidar, RPLidarException
except ImportError:
    print("ERROR: rplidar package not found.")
    print("Install with:  pip install rplidar-roboticia")
    sys.exit(1)


def quality_label(q: int) -> str:
    if q == 0:   return "invalid"
    if q < 10:   return "low"
    if q < 30:   return "medium"
    return "good"


def main():
    ap = argparse.ArgumentParser(description="RoboRanger RPLidar test")
    ap.add_argument("--port", default="/dev/ttyUSB0")
    ap.add_argument("--scans", type=int, default=3, help="Number of full scans to collect")
    args = ap.parse_args()

    print(f"Connecting to RPLidar on {args.port}…")
    try:
        lidar = RPLidar(args.port)
    except RPLidarException as e:
        print(f"ERROR: {e}")
        print("Check the port with:  ls /dev/ttyUSB*")
        sys.exit(1)

    try:
        info = lidar.get_info()
        health = lidar.get_health()
        print(f"\nDevice info:  {info}")
        print(f"Health:       {health}")

        if health[0] != "Good":
            print(f"WARNING: Lidar health is not 'Good' — {health}")

        print(f"\nCollecting {args.scans} scan(s)… (lidar should start spinning)\n")

        all_distances = []
        quality_counts = {"invalid": 0, "low": 0, "medium": 0, "good": 0}

        for i, scan in enumerate(lidar.iter_scans(max_buf_meas=5000)):
            distances = [m[2] for m in scan if m[2] > 0]
            qualities = [m[0] for m in scan]

            for q in qualities:
                quality_counts[quality_label(q)] += 1
            all_distances.extend(distances)

            valid   = len(distances)
            total   = len(scan)
            mn      = min(distances) / 1000 if distances else 0
            mx      = max(distances) / 1000 if distances else 0
            mean    = (sum(distances) / len(distances) / 1000) if distances else 0

            print(f"Scan {i+1:2d}: {total:4d} points  valid={valid:4d}  "
                  f"min={mn:.3f}m  max={mx:.3f}m  mean={mean:.3f}m")

            if i + 1 >= args.scans:
                break

        # Summary
        print("\n─── Summary ───────────────────────────────────────")
        if all_distances:
            mn   = min(all_distances) / 1000
            mx   = max(all_distances) / 1000
            mean = sum(all_distances) / len(all_distances) / 1000
            print(f"Total valid measurements : {len(all_distances)}")
            print(f"Range                    : {mn:.3f} m — {mx:.3f} m")
            print(f"Mean distance            : {mean:.3f} m")
            print(f"Quality counts           : {quality_counts}")

            bad_ratio = quality_counts["invalid"] / max(1, sum(quality_counts.values()))
            if bad_ratio > 0.3:
                print(f"[WARN] {bad_ratio*100:.0f}% invalid measurements — check for obstructions or power issues")
            else:
                print("[PASS] Scan quality looks acceptable")

            if mn < 0.1:
                print("[WARN] Very close measurement — check nothing is blocking the lidar")
            if mx > 12.0:
                print("[WARN] Very large measurement — A1 range is typically ≤ 12 m")
        else:
            print("[FAIL] No valid distance measurements received")

    except KeyboardInterrupt:
        pass
    finally:
        print("\nStopping lidar…")
        lidar.stop()
        time.sleep(3.0)
        print("AHHHH")
        lidar.stop_motor()
        lidar.disconnect()
        print("Done.")


if __name__ == "__main__":
    main()
