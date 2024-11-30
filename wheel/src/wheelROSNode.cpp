#include "wheelROSNode.h"

#include <stdio.h>
#include <rcl/rcl.h>
#include <rcl/error_handling.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>

rcl_subscription_t cmd_vel_subscriber;
rcl_publisher_t robot_pose_publisher;
rclc_executor_t executor;
rclc_support_t support;
rcl_allocator_t allocator;
rcl_node_t node;
rcl_timer_t timer;

void error_loop() {
  while (1)
  {
    digitalWrite(ROS_ERROR_LED_PIN, !digitalRead(ROS_ERROR_LED_PIN));
    delay(100);
  }
}

void RCCHECK(rcl_ret_t fn_ret, String error_id) {
  if(fn_ret != RCL_RET_OK)
  {
    Serial.println("BREAKING ERROR ID: " + error_id);
    error_loop();
  }
}

void RCSOFTCHECK(rcl_ret_t fn_ret, String error_id) {
  if (fn_ret != RCL_RET_OK)
  {
    Serial.println("WARNING ERROR ID: " + error_id);
  }
}


// SUBSCRIBERS AND PUBLISHERS CALLBACK
void cmd_vel_sub_callback(const void *msgin) {
  const geometry_msgs__msg__Twist * msg = (const geometry_msgs__msg__Twist *) msgin;

  // DELETE AFTER INSPECTION
  Serial.println("Wheel Linear Velocities (m/s):");
  Serial.print("X:  ");
  Serial.println(msg->linear.x, 4);
  Serial.print("Y:  ");
  Serial.println(msg->linear.y, 4);
  Serial.print("Z:  ");
  Serial.println(msg->linear.z, 4);
  Serial.println("Wheel Angular Velocities (rad/s):");
  Serial.print("X:  ");
  Serial.println(msg->angular.x, 4);
  Serial.print("Y:  ");
  Serial.println(msg->angular.y, 4);
  Serial.print("Z:  ");
  Serial.println(msg->angular.z, 4);

  Serial.println();

  // Calculate each wheel rotational speed based on mecanum kinematics model
  WheelVelocities wheel_velocities = robot_wheels.inverseKinematics(msg->linear.x, msg->linear.y, msg->angular.z);
  robot_wheels.displayWheelVelocities(wheel_velocities);

  WHEELS::w_1.set_velocity(wheel_velocities.w_1);
  WHEELS::w_2.set_velocity(wheel_velocities.w_2);
  WHEELS::w_3.set_velocity(wheel_velocities.w_3);
  WHEELS::w_4.set_velocity(wheel_velocities.w_4);
}

namespace WHEELROSNODE {
  geometry_msgs__msg__Pose pose_msg;
  geometry_msgs__msg__Twist twist_msg;

  void initialize()
  {
    // set_microros_transports();
    set_microros_serial_transports(Serial);  

    pinMode(ROS_ERROR_LED_PIN, OUTPUT);
    digitalWrite(ROS_ERROR_LED_PIN, HIGH);

    delay(2000);

    allocator = rcl_get_default_allocator();

    Serial.println("oooooooooooo");

    RCCHECK(rclc_support_init(&support, 0, NULL, &allocator), "support init");

    RCCHECK(rclc_node_init_default(&node, "wheels", "", &support), "node init");

    // Create publisher and subscriber
    RCCHECK(rclc_subscription_init_default(
      &cmd_vel_subscriber,
      &node,
      ROSIDL_GET_MSG_TYPE_SUPPORT(geometry_msgs, msg, Twist),
      "cmd_vel_subscriber"), "cmd subscription init");
    
    RCCHECK(rclc_publisher_init_default(
      &robot_pose_publisher,
      &node,
      ROSIDL_GET_MSG_TYPE_SUPPORT(geometry_msgs, msg, Pose),
      "robot_pose_publisher"), "robot pose subscription init");


    RCCHECK(rclc_executor_init(&executor, &support.context, 1, &allocator), "executor init");
    RCCHECK(rclc_executor_add_subscription(&executor, &cmd_vel_subscriber, &twist_msg, &cmd_vel_sub_callback, ON_NEW_DATA), "add cmd_vel sub");
  }

  void executor_spin_some() {
    RCSOFTCHECK(rclc_executor_spin_some(&executor, RCL_MS_TO_NS(100)), "ros node spin");
  }
}