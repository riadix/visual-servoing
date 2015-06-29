#!/usr/bin/env python

import numpy as np

import roslib
from std_msgs.msg import (
    Header,
)
from geometry_msgs.msg import (
    PoseStamped,
    Pose,
    Quaternion,
)
from tf.transformations import *

# Get the translation vector (4x1) and rotation matrix (4x4) from a pose message
def get_t_R(pose):
    t=np.transpose(np.matrix([pose.position.x,pose.position.y,pose.position.z,1]))
    quat=[pose.orientation.x, pose.orientation.y, pose.orientation.z, pose.orientation.w]
    R_full=quaternion_matrix(quat)
    R=R_full
    return t,R

# Generates a pose stamped message from a translation vector and rotation matrix for publishing.
# NOTE: Does not set the target frame.
def make_pose_stamped_msg(t,R):
    pose_stamped_msg=PoseStamped()
    pose_stamped_msg.header=Header()
    pose_stamped_msg.header.stamp=rospy.Time.now()
    pose_msg=Pose()
    pose_msg.position.x=t[0]
    pose_msg.position.y=t[1]
    pose_msg.position.z=t[2]
    quat=quaternion_from_matrix(R)
    pose_msg.orientation.x=quat[0]
    pose_msg.orientation.y=quat[1]
    pose_msg.orientation.z=quat[2]
    pose_msg.orientation.w=quat[3]
    pose_stamped_msg.pose=pose_msg
    return pose_stamped_msg

def generate_skew_mat(v):
    skew_matrix=np.matrix([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]])
    return skew_matrix

# Generate the transformation between frames for a twist (v,w)
def generate_frame_transform(t,R,isarm):
    r_t=-np.dot(np.transpose(R),t)
    skew_matrix=generate_skew_mat(r_t)
    if isarm:
        transform_top=np.concatenate((R,np.zeros((3,3))),axis=1)
    else:
        transform_top=np.concatenate((R,-np.dot(R,skew_matrix)),axis=1)
        
    transform_bottom=np.concatenate((np.zeros((3,3)),R),axis=1)
    transform=np.concatenate((transform_top,transform_bottom),axis=0)
    return transform
