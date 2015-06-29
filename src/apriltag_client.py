#!/usr/bin/env python
import roslib
import numpy as np
import numpy.matlib
import cv2
import sys
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from tf.transformations import *
from apriltags_ros.msg import AprilTagDetectionArray
from utility import *

from std_msgs.msg import (
    Header,
    UInt16,
)

from geometry_msgs.msg import (
    PoseStamped,
    Pose,
    Point,
    Point32,
    Quaternion,
)

import struct

class AprilTagClient(object):
    def __init__(self, target_marker):
        # Options
        self._show_image=False
        
        self._last_marker=-1
        self._TARGET_MARKER=target_marker

        self.marker_t=None
        self.marker_R=None
        self.corners = None
        self._image = None

        self._bridge = CvBridge()

        # ROS Pubs and Subs
        rospy.on_shutdown(self.__shutdown_hook)
        rospy.Subscriber("/tag_detections",AprilTagDetectionArray,self.__process_detection)
        rospy.Subscriber("/tag_detections_image",Image,self.__get_image)

    def __shutdown_hook(self):
        pass
    
    # Parses an apriltag detection object, and gets the position for the last used marker, or
    # simply the first one found if the last one was not seen. Returns -1 if nothing found.
    def __get_marker(self,detections):
        if (len(detections)==0):
            return None,None
        marker=self.__find_marker(detections,self._last_marker)
        if (marker!=-1):
            return self._last_marker,marker
        else:
            self._last_marker=detections[0].id
            return detections[0].id,0

    def __find_marker(self,detections,marker_num):
        for i in range(0,len(detections)):
            # If marker found
            if detections[i].id==marker_num:
                return i
        return -1
    
    # Dummy function to save incoming images
    def __get_image(self,image):
        #print "Image received!"
        try:
            cv_image=self._bridge.imgmsg_to_cv2(image,"bgr8")
            self._image=cv_image
        except CvBridgeError, e:
            print e

    # Tag detection may have come in
    def __process_detection(self,apriltag_detections):
        if rospy.is_shutdown():
            return
        
        # Get best marker for gripper pose
        (my_marker,marker_pos)=self.__get_marker(apriltag_detections.detections)

        if my_marker is None:
            return

        (self.marker_t,self.marker_R)=get_t_R(apriltag_detections.detections[marker_pos].pose.pose)
        self.corners = np.array(apriltag_detections.detections[marker_pos].corners)
