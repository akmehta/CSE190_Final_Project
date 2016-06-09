#!/usr/bin/env python

import rospy
import random
import math as m
import numpy as np
from copy import deepcopy
from final_project.msg import PolicyList
import mdp
from std_msgs.msg import Bool
from std_msgs.msg import String
from std_msgs.msg import Float32
from read_config import read_config


class Robot():

    def __init__(self):
        """Read config file and setup ROS things"""
        self.config = read_config()
        rospy.init_node("robot")
        self.mdp_pub = rospy.Publisher("/results/policy_list", PolicyList, queue_size=10)
        self.complete_mess = rospy.Publisher("/map_node/sim_complete", Bool, queue_size=10)
	self.map_size = self.config['map_size']
        mdp_res = ['N']*(self.map_size[0]*self.map_size[1])
        mdp_res = mdp.myFunction(self.config)
        for x in mdp_res:
          rospy.sleep(1)
          self.mdp_pub.publish(x)
        rospy.sleep(1)
        self.complete_mess.publish(True)
        rospy.sleep(2)
        rospy.signal_shutdown("Done.") 
    
if __name__ == '__main__':
    r = Robot()
