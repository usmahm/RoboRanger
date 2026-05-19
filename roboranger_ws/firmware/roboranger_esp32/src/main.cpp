// RoboRanger — Phase 1 Test Firmware
// Tests: motor control, MPU6050 IMU, serial echo
//
// Serial commands (115200 baud, newline-terminated):
//   MOTOR:<id>:<dir>:<speed>   id=0-3, dir=F/B/S, speed=0-255
//   IMU_START                  stream IMU at 50Hz
//   IMU_STOP
//   ECHO:<msg>                 loopback test
//   STOP                       stop all motors
//
// Serial output:
//   IMU:<ax>,<ay>,<az>,<gx>,<gy>,<gz>   (m/s² and rad/s)
//   OK / ERR / INFO / WARN prefixed lines

#include <Arduino.h>
#include <Wire.h>
#include <MPU6050.h>

// ─── Pin Configuration ────────────────────────────────
// Adjust these to match your actual wiring before flashing.
//
// Motor index:  0=FL (front-left)  1=FR (front-right)
//               2=RL (rear-left)   3=RR (rear-right)
//
// Each motor needs: IN1, IN2 (direction) and EN (PWM speed)

#define M_FL_IN1  12
#define M_FL_IN2  26
#define M_FL_EN   13

#define M_FR_IN1  18
#define M_FR_IN2  32
#define M_FR_EN   27

#define M_RL_IN1  16
#define M_RL_IN2  17
#define M_RL_EN   25

#define M_RR_IN1  23
#define M_RR_IN2  19
#define M_RR_EN   33

// MPU6050 I2C — default ESP32 I2C pins
#define MPU_SDA 21
#define MPU_SCL 22

// ─── Globals ──────────────────────────────────────────
struct MotorPins { int in1, in2, en; };

MotorPins motors[4] = {
    {M_FL_IN1, M_FL_IN2, M_FL_EN},
    {M_FR_IN1, M_FR_IN2, M_FR_EN},
    {M_RL_IN1, M_RL_IN2, M_RL_EN},
    {M_RR_IN1, M_RR_IN2, M_RR_EN},
};

MPU6050 mpu;
bool imu_streaming    = false;
bool watchdog_armed   = false;
unsigned long last_cmd_ms = 0;
unsigned long last_imu_ms = 0;

const unsigned long WATCHDOG_MS = 500;
const unsigned long IMU_PERIOD_MS = 20;  // 50 Hz

// ─── Motor Control ────────────────────────────────────
void motorSet(int idx, int dir, int speed) {
    // dir: 1=forward, -1=backward, 0=stop
    speed = constrain(speed, 0, 255);
    if (dir > 0) {
        digitalWrite(motors[idx].in1, HIGH);
        digitalWrite(motors[idx].in2, LOW);
    } else if (dir < 0) {
        digitalWrite(motors[idx].in1, LOW);
        digitalWrite(motors[idx].in2, HIGH);
    } else {
        digitalWrite(motors[idx].in1, LOW);
        digitalWrite(motors[idx].in2, LOW);
        speed = 0;
    }
    analogWrite(motors[idx].en, speed);
}

void allStop() {
    for (int i = 0; i < 4; i++) motorSet(i, 0, 0);
}

// ─── Command Handler ──────────────────────────────────
void handleCommand(const String& raw) {
    String cmd = raw;
    cmd.trim();
    if (cmd.length() == 0) return;

    last_cmd_ms    = millis();
    watchdog_armed = true;

    if (cmd.startsWith("MOTOR:")) {
        // Format: MOTOR:<id>:<dir>:<speed>
        // Example: MOTOR:0:F:128
        int id  = cmd.substring(6, 7).toInt();
        char d  = (cmd.length() > 8) ? cmd.charAt(8) : 'S';
        int spd = (cmd.length() > 10) ? cmd.substring(10).toInt() : 0;
        int dir = (d == 'F') ? 1 : (d == 'B') ? -1 : 0;

        if (id < 0 || id > 3) {
            Serial.println("ERR bad motor id (0-3)");
            return;
        }
        motorSet(id, dir, spd);
        Serial.printf("OK MOTOR %d dir=%c spd=%d\n", id, d, spd);

    } else if (cmd == "IMU_START") {
        imu_streaming = true;
        Serial.println("OK IMU_START");

    } else if (cmd == "IMU_STOP") {
        imu_streaming = false;
        Serial.println("OK IMU_STOP");

    } else if (cmd.startsWith("ECHO:")) {
        Serial.println("ECHO:" + cmd.substring(5));

    } else if (cmd == "STOP") {
        allStop();
        watchdog_armed = false;
        Serial.println("OK STOP");

    } else {
        Serial.println("ERR unknown: " + cmd);
    }
}

// ─── Setup ────────────────────────────────────────────
void setup() {
    Serial.begin(115200);

    // Init motor pins
    for (int i = 0; i < 4; i++) {
        pinMode(motors[i].in1, OUTPUT);
        pinMode(motors[i].in2, OUTPUT);
        pinMode(motors[i].en, OUTPUT);
    }
    allStop();

    // Init MPU6050
    Wire.begin(MPU_SDA, MPU_SCL);
    mpu.initialize();
    if (mpu.testConnection()) {
        Serial.println("INFO MPU6050 OK");
    } else {
        Serial.println("WARN MPU6050 not found — check SDA/SCL and I2C address");
    }

    Serial.println("INFO RoboRanger test firmware ready");
    Serial.println("INFO Commands: MOTOR:<id>:<dir>:<spd> | IMU_START | IMU_STOP | ECHO:<msg> | STOP");
}

// ─── Loop ─────────────────────────────────────────────
void loop() {
    // Watchdog — stop motors if no command received in time
    if (watchdog_armed && (millis() - last_cmd_ms > WATCHDOG_MS)) {
        allStop();
        watchdog_armed = false;
        Serial.println("WARN watchdog triggered — motors stopped");
    }

    // Read incoming command
    if (Serial.available()) {
        String cmd = Serial.readStringUntil('\n');
        handleCommand(cmd);
    }

    // IMU streaming at 50 Hz
    if (imu_streaming && (millis() - last_imu_ms >= IMU_PERIOD_MS)) {
        last_imu_ms = millis();
        int16_t ax, ay, az, gx, gy, gz;
        mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

        // Scale: ±2g default → 16384 LSB/g;  ±250°/s → 131 LSB/(°/s)
        float fax = ax / 16384.0f * 9.81f;
        float fay = ay / 16384.0f * 9.81f;
        float faz = az / 16384.0f * 9.81f;
        float fgx = gx / 131.0f * 0.017453f;  // °/s → rad/s
        float fgy = gy / 131.0f * 0.017453f;
        float fgz = gz / 131.0f * 0.017453f;

        Serial.printf("IMU:%.4f,%.4f,%.4f,%.4f,%.4f,%.4f\n",
                      fax, fay, faz, fgx, fgy, fgz);
    }
}
