# Phase 1 — Hardware Tests

Verify every hardware component works in isolation before writing any ROS2 code.

## Setup

### 1. Flash the ESP32 test firmware

```bash
cd ../firmware/roboranger_esp32
# Edit src/main.cpp and set the correct pin numbers for your wiring
pio run --target upload
pio device monitor   # verify "INFO RoboRanger test firmware ready"
```

### 2. Install Python dependencies

Create a virtual environment and install dependencies:

```bash
cd roboranger_ws/tests
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run tests from within the activated venv:

```bash
python3 test_motors.py
```

> **Note:** `pyrealsense2` on Raspberry Pi requires installing the Intel RealSense SDK first.
> See [librealsense Raspberry Pi installation guide](https://github.com/IntelRealSense/librealsense/blob/master/doc/installation_raspbian.md).
> Then recreate the venv with `--system-site-packages` so it can access the system-installed bindings:
> ```bash
> python3 -m venv .venv --system-site-packages
> ```

### 3. Find your serial ports

```bash
ls /dev/ttyUSB*   # USB-serial adapters
ls /dev/ttyACM*   # CDC-ACM devices (some ESP32 boards)
```

Unplug and replug the ESP32 to identify which port is which.

---

## Test Order & Pass Criteria

Run tests in this order — earlier tests are prerequisites for later ones.

| # | Script | Hardware needed | PASS condition |
|---|--------|----------------|----------------|
| 1 | `test_motors.py` | ESP32 + L298N + motors | Each motor spins correct direction |
| 2 | `test_mpu6050.py` | ESP32 + MPU6050 | Accel Z ≈ 9.81 m/s², values change on tilt |
| 3 | `test_rplidar.py` | RPLidar | Valid distance measurements, lidar spins |
| 4 | `test_d435i.py` | Intel D435i | RGB/depth ≥ 20fps, IMU streaming |
| 5 | `test_serial_comms.py` | ESP32 | 0 errors over 200 echo rounds, latency < 20ms |
| 6 | `test_mecanum_motion.py` | ESP32 + all 4 motors | Robot moves in correct direction for each command |

---

## Running the Tests

### Test 1 — Motors

```bash
# Interactive (default)
python3 test_motors.py --port /dev/ttyUSB0

# Automated sequence
python3 test_motors.py --port /dev/ttyUSB0 --auto
```

**Troubleshooting:**
- Motor doesn't spin → check IN1/IN2/EN wiring and motor index mapping
- Motor spins wrong direction → swap IN1 and IN2 pins in `firmware/src/main.cpp`
- No response → check serial port and baud rate (115200)

---

### Test 2 — MPU6050 IMU

```bash
python3 test_mpu6050.py --port /dev/ttyUSB0
```

**Expected output:**
```
  [ESP32] INFO MPU6050 OK
  [ESP32] INFO RoboRanger test firmware ready
  ...
   1    +0.0123   +0.0045   +9.8132   +0.0001   -0.0003   +0.0002   9.8133
```

**Troubleshooting:**
- `WARN MPU6050 not found` → check SDA/SCL wiring and I2C address (default 0x68, AD0=LOW)
- Values are all zero → I2C connection issue, check pull-up resistors

---

### Test 3 — RPLidar

```bash
# RPLidar is on a DIFFERENT USB port from the ESP32
python3 test_rplidar.py --port /dev/ttyUSB1 --scans 5
```

**Troubleshooting:**
- `Permission denied` → `sudo chmod a+rw /dev/ttyUSB1`  (or add user to `dialout` group)
- Lidar doesn't spin → check power (some RPLidar models need 5V on a separate pin)

---

### Test 4 — Intel D435i

```bash
python3 test_d435i.py --duration 20
```

**Troubleshooting:**
- `No RealSense device found` → use USB 3.0 port, try different cable
- Low fps → USB bandwidth issue, ensure no other USB 3.0 devices on same controller

---

### Test 5 — Serial Communication

```bash
python3 test_serial_comms.py --port /dev/ttyUSB0 --count 500
```

**Troubleshooting:**
- High latency → check for other processes using the same serial port
- Errors/timeouts → try lower count, check cable quality

---

### Test 6 — Mecanum Motion

```bash
# Start slow (speed 100) to verify directions before going faster
python3 test_mecanum_motion.py --port /dev/ttyUSB0 --speed 100 --duration 2.0
```

**If a direction is wrong:**
The most common issue is a motor spinning the wrong way. Fix it in the firmware:
```cpp
// In firmware/roboranger_esp32/src/main.cpp, swap IN1/IN2 for the bad motor
// Example: if FL motor is reversed, swap M_FL_IN1 and M_FL_IN2 values
#define M_FL_IN1  27   // was 26
#define M_FL_IN2  26   // was 27
```

**Mecanum direction reference:**
```
Motion     | FL  | FR  | RL  | RR
-----------+-----+-----+-----+----
Forward    |  +  |  +  |  +  |  +
Backward   |  -  |  -  |  -  |  -
Strafe R   |  +  |  -  |  -  |  +
Strafe L   |  -  |  +  |  +  |  -
Rotate CW  |  +  |  -  |  +  |  -
Rotate CCW |  -  |  +  |  -  |  +
```

---

## After All Tests Pass

Move on to **Phase 2 — Robot Description** (URDF + RViz visualization).
