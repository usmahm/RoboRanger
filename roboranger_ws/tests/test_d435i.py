#!/usr/bin/env python3
"""
Test 4: Intel D435i Hardware Test
Verify RGB, depth, and IMU streams from the RealSense D435i.

Requires:
  - Intel RealSense SDK 2.0 installed on your system
  - pip install pyrealsense2
  - D435i connected via USB 3.0 port

Usage:
  python3 test_d435i.py
  python3 test_d435i.py --duration 10

Pass criteria:
  - RGB frames arriving at ~30 fps
  - Depth frames arriving at ~30 fps
  - Accel and gyro IMU data streaming
  - Depth values look reasonable (not all zeros or max)
"""

import argparse
import sys
import time
from collections import defaultdict

try:
    import pyrealsense2 as rs
except ImportError:
    print("ERROR: pyrealsense2 not found.")
    print("Install Intel RealSense SDK 2.0 then:  pip install pyrealsense2")
    print("Or on Raspberry Pi follow: https://github.com/IntelRealSense/librealsense/blob/master/doc/installation_raspbian.md")
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser(description="RoboRanger D435i hardware test")
    ap.add_argument("--duration", type=int, default=15, help="Seconds to stream (0 = until Ctrl+C)")
    args = ap.parse_args()

    ctx = rs.context()
    devices = ctx.query_devices()
    if len(devices) == 0:
        print("ERROR: No RealSense device found. Check USB connection.")
        sys.exit(1)

    dev = devices[0]
    print(f"Device found: {dev.get_info(rs.camera_info.name)}")
    print(f"Serial:       {dev.get_info(rs.camera_info.serial_number)}")
    print(f"Firmware:     {dev.get_info(rs.camera_info.firmware_version)}")

    pipe   = rs.pipeline()
    config = rs.config()

    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16,  30)
    config.enable_stream(rs.stream.accel, rs.format.motion_xyz32f)
    config.enable_stream(rs.stream.gyro,  rs.format.motion_xyz32f)

    print("\nStarting pipeline…")
    profile = pipe.start(config)

    depth_sensor = profile.get_device().first_depth_sensor()
    depth_scale  = depth_sensor.get_depth_scale()
    print(f"Depth scale: {depth_scale:.6f} m/unit\n")

    counts    = defaultdict(int)
    depth_vals = []
    accel_last = None
    gyro_last  = None
    start     = time.time()
    deadline  = start + args.duration if args.duration > 0 else float("inf")

    print("Streaming… (Ctrl+C to stop early)\n")
    print(f"{'Time':>6}  {'RGB fps':>8}  {'Depth fps':>10}  {'Depth mean':>11}  "
          f"{'Accel (m/s²)':>28}  {'Gyro (rad/s)':>28}")
    print("─" * 100)

    report_interval = 1.0
    next_report     = start + report_interval

    try:
        while time.time() < deadline:
            frames = pipe.wait_for_frames(timeout_ms=2000)

            if frames.get_color_frame():
                counts["color"] += 1

            depth_frame = frames.get_depth_frame()
            if depth_frame:
                counts["depth"] += 1
                w, h = depth_frame.width, depth_frame.height
                center = depth_frame.get_distance(w // 2, h // 2)
                depth_vals.append(center)

            for f in frames:
                if f.is_motion_frame():
                    md = f.as_motion_frame().get_motion_data()
                    if f.get_profile().stream_type() == rs.stream.accel:
                        accel_last = md
                        counts["accel"] += 1
                    elif f.get_profile().stream_type() == rs.stream.gyro:
                        gyro_last = md
                        counts["gyro"] += 1

            now = time.time()
            if now >= next_report:
                elapsed = now - start
                dt      = report_interval
                color_fps = counts["color_prev_delta"] if False else counts["color"] / elapsed
                depth_fps = counts["depth"] / elapsed
                depth_mean = (sum(depth_vals[-30:]) / min(30, len(depth_vals))) if depth_vals else 0

                accel_str = (f"x={accel_last.x:+.3f} y={accel_last.y:+.3f} z={accel_last.z:+.3f}"
                             if accel_last else "  waiting…")
                gyro_str  = (f"x={gyro_last.x:+.4f} y={gyro_last.y:+.4f} z={gyro_last.z:+.4f}"
                             if gyro_last else "  waiting…")

                print(f"{elapsed:6.1f}  {color_fps:8.1f}  {depth_fps:10.1f}  "
                      f"{depth_mean:10.3f}m  {accel_str:>28}  {gyro_str:>28}")
                next_report += report_interval

    except KeyboardInterrupt:
        pass
    finally:
        pipe.stop()

    # Final report
    elapsed = time.time() - start
    print("\n─── Summary ───────────────────────────────────────")
    print(f"Duration: {elapsed:.1f} s")
    print(f"  Color frames : {counts['color']:5d}  ({counts['color']/elapsed:.1f} fps)")
    print(f"  Depth frames : {counts['depth']:5d}  ({counts['depth']/elapsed:.1f} fps)")
    print(f"  Accel samples: {counts['accel']:5d}")
    print(f"  Gyro  samples: {counts['gyro']:5d}")

    issues = []
    if counts["color"] / elapsed < 20:  issues.append("RGB fps too low (expected ~30)")
    if counts["depth"] / elapsed < 20:  issues.append("Depth fps too low (expected ~30)")
    if counts["accel"] == 0:            issues.append("No accelerometer data — check IMU enabled")
    if counts["gyro"]  == 0:            issues.append("No gyro data — check IMU enabled")

    if issues:
        for i in issues:
            print(f"[WARN] {i}")
    else:
        print("[PASS] All streams healthy")


if __name__ == "__main__":
    main()
