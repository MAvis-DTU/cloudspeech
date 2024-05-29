import qi
import time
import random
import sys
session = qi.Session()
session.connect("tcp://192.168.1.110:9559")

posture = session.service("ALRobotPosture")

while True:
    try:
        posture.goToPosture("Stand", 0.5)
        # print("in")
    except (EOFError):
        time.sleep(0.01)
        # print("continue")
        continue
    break

