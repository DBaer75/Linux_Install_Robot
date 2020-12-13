#delete the robot if it exists and then spawn the robot
rosservice call gazebo/delete_model fourWheeledRobot
rosrun gazebo_ros spawn_model -file /home/user/catkin_ws/src/Linux_Install_Robot/fourWheelRobot/models/model.sdf -sdf -model fourWheeledRobot -y 0.0 -x -0.0 -z 1.0
