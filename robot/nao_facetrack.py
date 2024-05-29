#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Example: Modify Face Tracking policy on the robot."""

import qi
import sys

IP = raw_input() 
session = qi.Session()
session.connect(IP)

posture = session.service("ALRobotPosture")

"""
This example shows how to use ALTracker with face.
"""
# Get the services ALTracker and ALMotion.

motion_service = session.service("ALMotion")
tracker_service = session.service("ALTracker")

# First, wake up.
motion_service.wakeUp()

# Add target to track.
targetName = "Face"
faceWidth = 0.1
tracker_service.registerTarget(targetName, faceWidth)

# Then, start tracker.
tracker_service.track(targetName)

