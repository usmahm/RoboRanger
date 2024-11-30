#include <Arduino.h>
#include "env.h"
// #include "mecanumModel.h"
#include "wheels.h"
#include "wheelROSNode.h"

double vx = 1.0;
double vy = 0.0;
double omega_z = 0.0;

// WHEELROSNODE wheel_ros_node;

void setup() {
  Serial.begin(115200);
  // while (!Serial) {
  //     ; // Wait for Serial to initialize (only needed for some boards)
  // }

  // Initialize motors
  WHEELS::w_1.initialize();
  WHEELS::w_2.initialize();
  WHEELS::w_3.initialize();
  WHEELS::w_4.initialize();

  WHEELROSNODE::initialize();

  Serial.println("Robot Wheel Initialized.");
  Serial.println();
}

void loop() {
  delay(100);

  WHEELROSNODE::executor_spin_some();
}

