import qi
import time
import random

IP = raw_input() 

session = qi.Session()
session.connect(IP)

motion_service = session.service("ALMotion")
posture_service = session.service("ALRobotPosture")
auto_life = session.service("ALAutonomousLife")

# # Stop breathing
motion_service.killAll()

motion_service.setBreathEnabled('Body', False)
motion_service.setBreathEnabled('Arms', False)
motion_service.setBreathEnabled('Head', False)
motion_service.setBreathEnabled('Legs', False)
motion_service.setBreathEnabled('LArm', False)
motion_service.setBreathEnabled('RArm', False)

# # Go to rest position
# motion_service.rest()
posture_service.goToPosture("StandInit", 0.5)
