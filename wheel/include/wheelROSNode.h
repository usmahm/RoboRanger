#pragma once

#include "Arduino.h"
#include "env.h"
#include "mecanumModel.h"
#include "wheels.h"

#include <micro_ros_platformio.h>

#include <geometry_msgs/msg/pose.h>
#include <geometry_msgs/msg/twist.h>


namespace WHEELROSNODE {
  extern geometry_msgs__msg__Pose pose_msg;
  extern geometry_msgs__msg__Twist twist_msg;

  void initialize();
  void executor_spin_some();
}