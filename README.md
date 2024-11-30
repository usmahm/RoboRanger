# ROBORANGER

![project image](https://github.com/user-attachments/assets/b242f7d6-85ef-4041-960a-4850c7081cd4)

[NOT A DOCUMENTATION]
# Command to run code[to setup run script later]

```
ros2 run teleop_twist_keyboard teleop_twist_keyboard

source install/local_setup.bash - In robot_ws

sudo dmesg --follow

ls -l /dev/ttyUSB0

sudo chmod 666 /dev/ttyUSB0

source install/local_setup.bash - In microros_ws

ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0
```
