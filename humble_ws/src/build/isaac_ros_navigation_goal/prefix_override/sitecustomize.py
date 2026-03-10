import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/ubuntu/IsaacSim-ros_workspaces/humble_ws/src/install/isaac_ros_navigation_goal'
