import qi
import time

IP = raw_input() 
session = qi.Session()
session.connect(IP)
behavior = session.service("ALBehaviorManager")

behavior.stopAllBehaviors()