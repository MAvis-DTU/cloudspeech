import qi
import time
import random
import sys

IP = raw_input() 

session = qi.Session()
session.connect(IP)

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

