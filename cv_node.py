#!/usr/bin/env python
# Software License Agreement (BSD License)
#
# Copyright (c) 2008, Willow Garage, Inc.
# All rights reserved.
#

import rospy
from std_msgs.msg import UInt16
import cv2
import cv2.aruco as aruco
import time
import matplotlib.pyplot as plt

def get_distance(ret,frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    parameters =  aruco.DetectorParameters_create()
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    shape_center_x = 0
    shape_center_y = 0
    dX = 0
    dY = 0

    if len(corners) > 0:
        for i in corners:
            for j in i:
                for k in j:
                    shape_center_x += k[0]
                    shape_center_y += k[1]

        shape_center_x = shape_center_x / 4
        shape_center_y = shape_center_y / 4

        height, width = gray.shape [:2]
        midX = width / 2
        midY = height / 2
        dX = shape_center_x - midX
        dY = shape_center_y - midY

    gray = aruco.drawDetectedMarkers(frame, corners)

    horizontal_img = cv2.flip( gray, 0 )
    cv2.imshow('frame_',horizontal_img)
    cv2.waitKey(1)


    #return [dX,dY]
    return dX

def distanceGenerator():




    # Calculate number of pixels corresponding to 1 degree
    cap = cv2.VideoCapture(0)
    ret,frame = cap.read()
    height, width = frame.shape [:2]
    oneDeg = width/62


    # Initialize ROS msg
    pub = rospy.Publisher('servo', UInt16, queue_size=1)
    rospy.init_node('distanceGenerator', anonymous=True)
    rate = rospy.Rate(5) # wait untill it turns (in hz)

    initialPosition = 90
    actualPosition = initialPosition
    goneToInitial = False

    while not rospy.is_shutdown():
        # Go to initial position
        connections = pub.get_num_connections()
        rospy.loginfo('Connections: %d', connections)
        if connections > 0 and goneToInitial == False:
            rospy.loginfo("Go to initial position")
            goneToInitial = True
            pub.publish(initialPosition)
            rospy.loginfo('Published')

        # Go to aruco position
        elif connections > 0 and goneToInitial == True:
            rospy.loginfo("Go to aruco position")

            # Get position of aruco marker
            ret,frame = cap.read()
            dX = get_distance(ret, frame)
            diffDeg = int(dX/oneDeg)
            arucoPosition = initialPosition + diffDeg
            
            TOL = 2
            
            while not actualPosition == arucoPosition:
                if abs(diffDeg) > TOL:
                    actualPosition = actualPosition + diffDeg/5
                    rospy.loginfo(actualPosition)
                    pub.publish(actualPosition)
                    rate.sleep()

                ret,frame = cap.read()
                dX = get_distance(ret, frame)
                diffDeg = int(dX/oneDeg)
                arucoPosition = initialPosition + diffDeg

if __name__ == '__main__':
    try:
        distanceGenerator()
    except rospy.ROSInterruptException:
        pass
