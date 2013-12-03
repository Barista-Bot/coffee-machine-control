coffee-machine-control
======================

ROS node for controlling our modified Krups Pixie Nespresso machine via a Raspberry Pi.

To run the node on the Pi, run the following commands;

- `sudo su` (As the Pi GPIO can only be controlled by root)

- `source ~/catkin_ws/devel/setup.bash` (Sources the ROS setup script)

- `export ROS_IP=<IP Address of Raspberry Pi>` (Sets the IP that ROS uses for this device)

- `export ROS_MASTER_URI=http://<IP Address of Host>:11311` (Points this ROS node to use a remote master - note that `roscore` must be running on the remote host)

- `rosrun coffee-machine-control coffee-machine-server.py` (Runs the ROS node itself)

