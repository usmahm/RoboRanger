#pragma once

#include <Arduino.h>
#include "env.h"

struct WheelVelocities {
  double w_1; // Front-Left Wheel
  double w_2; // Front-Right Wheel
  double w_3; // Rear-Left Wheel
  double w_4; // Rear-Right Wheel
};

class MecanumModel {
  private:
    double r; //Radius of th ewheels (m)
    double lx; // Half the distance between front and rear wheels (meters)
    double ly; // Half the distance between left and right wheels (meters)

  public:
    MecanumModel(double wheel_radius, double half_length_x, double half_length_y);

    WheelVelocities inverseKinematics(double vx, double vy, double omega_z);

    void displayWheelVelocities(const WheelVelocities& wheel_velocities);
};

extern MecanumModel robot_wheels;
// WheelVelocities wheel_velocities;