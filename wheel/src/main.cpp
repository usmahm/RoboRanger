#include <Arduino.h>
#include "env.h"
#include "mecanumModel.h"
#include "wheel.h"

MecanumModel robot_wheels(WHEEL_RADIUS, HALF_LENGTH_X, HALF_LENGTH_Y);

double vx = 1.0;
double vy = 0.0;
double omega_z = 0.0;

WheelVelocities wheel_velocities;

WHEEL wheel_1(12, 26, 13);
WHEEL wheel_2(32, 18, 27);

WHEEL wheel_3(16, 17, 25);
WHEEL wheel_4(19, 23, 33);

void setup() {
  Serial.begin(115200);
  // while (!Serial) {
  //     ; // Wait for Serial to initialize (only needed for some boards)
  // }

  // Initialize motors
  wheel_1.initialize();
  wheel_2.initialize();
  wheel_3.initialize();
  wheel_4.initialize();

  Serial.println("Robot Wheel Initialized.");
  Serial.println();
}

void loop() {
  wheel_velocities = robot_wheels.inverseKinematics(vx, vy, omega_z);
  robot_wheels.displayWheelVelocities(wheel_velocities);

  wheel_1.setVelocity(wheel_velocities.w_1);
  wheel_2.setVelocity(wheel_velocities.w_2);
  wheel_3.setVelocity(wheel_velocities.w_3);
  wheel_4.setVelocity(wheel_velocities.w_4);

  delay(2000);

  // Example: Stop the robot
  Serial.println("Stopping Robot.");
  Serial.println();

  vx = 0.0;
  vy = 0.0;
  omega_z = 0.0;

  wheel_velocities = robot_wheels.inverseKinematics(vx, vy, omega_z);
  robot_wheels.displayWheelVelocities(wheel_velocities);
  
  wheel_1.setVelocity(wheel_velocities.w_1);
  wheel_2.setVelocity(wheel_velocities.w_2);
  wheel_3.setVelocity(wheel_velocities.w_3);
  wheel_4.setVelocity(wheel_velocities.w_4);

  Serial.println();

  delay(2000);

  vx = 0.0;
  vy = 0.0;
  omega_z = 2.0;
}

