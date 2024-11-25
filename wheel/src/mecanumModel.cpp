#include "mecanumModel.h"

MecanumModel::MecanumModel(double wheel_radius, double half_length_x, double half_length_y)
: r(wheel_radius), lx(half_length_x), ly(half_length_y) {};

WheelVelocities MecanumModel::inverseKinematics(double vx, double vy, double omega_z) {
  WheelVelocities wheel_velocities;

  double l_sum = lx + ly;

  // Inverse Kinematic Equations
  wheel_velocities.w_1  = (vx - vy - (l_sum * omega_z)) / r; 
  wheel_velocities.w_2 = (vx + vy + (l_sum * omega_z)) / r; 
  wheel_velocities.w_3   = (vx + vy - (l_sum * omega_z)) / r; 
  wheel_velocities.w_4  = (vx - vy + (l_sum * omega_z)) / r; 

  return wheel_velocities;
}

void MecanumModel::displayWheelVelocities(const WheelVelocities& wheel_velocities) {
  Serial.println("Wheel Angular Velocities (rad/s):");
  Serial.print("Front-Left:  ");
  Serial.println(wheel_velocities.w_1, 4);
  Serial.print("Front-Right: ");
  Serial.println(wheel_velocities.w_2, 4);
  Serial.print("Rear-Left:   ");
  Serial.println(wheel_velocities.w_3, 4);
  Serial.print("Rear-Right:  ");
  Serial.println(wheel_velocities.w_4, 4);
  Serial.println();
}
