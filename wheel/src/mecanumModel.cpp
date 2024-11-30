#include "mecanumModel.h"

MecanumModel robot_wheels(WHEEL_RADIUS, HALF_LENGTH_X, HALF_LENGTH_Y);

MecanumModel::MecanumModel(double wheel_radius, double half_length_x, double half_length_y)
: r(wheel_radius), lx(half_length_x), ly(half_length_y) {};

WheelVelocities MecanumModel::inverseKinematics(double vx, double vy, double omega_z) {
  WheelVelocities calc_wheel_velocities;

  double l_sum = lx + ly;

  // Inverse Kinematic Equations
  calc_wheel_velocities.w_1  = (vx - vy - (l_sum * omega_z)) / r; 
  calc_wheel_velocities.w_2 = (vx + vy + (l_sum * omega_z)) / r; 
  calc_wheel_velocities.w_3   = (vx + vy - (l_sum * omega_z)) / r; 
  calc_wheel_velocities.w_4  = (vx - vy + (l_sum * omega_z)) / r; 

  return calc_wheel_velocities;
}

void MecanumModel::displayWheelVelocities(const WheelVelocities& wheels_v) {
  Serial.println("Wheel Angular Velocities (rad/s):");
  Serial.print("Front-Left:  ");
  Serial.println(wheels_v.w_1, 4);
  Serial.print("Front-Right: ");
  Serial.println(wheels_v.w_2, 4);
  Serial.print("Rear-Left:   ");
  Serial.println(wheels_v.w_3, 4);
  Serial.print("Rear-Right:  ");
  Serial.println(wheels_v.w_4, 4);
  Serial.println();
}
