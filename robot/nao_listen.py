import qi
import time
import random

session = qi.Session()
session.connect("tcp://192.168.1.152:9559")

tts = session.service("ALTextToSpeech")
behavior = session.service("ALBehaviorManager")
posture = session.service("ALRobotPosture")

posture.goToPosture("Stand", 0.5)
animations = [
    "animations/Stand/Gestures/Explain_1",
    "animations/Stand/Gestures/Explain_2",
    "animations/Stand/Gestures/Explain_3",
    "animations/Stand/Gestures/Explain_4",
    "animations/Stand/Gestures/Explain_5",
    "animations/Stand/Gestures/Explain_6",
    "animations/Stand/Gestures/Explain_7",
    "animations/Stand/Gestures/Explain_8",
    "animations/Stand/Gestures/Explain_10",
    "animations/Stand/Gestures/Explain_11"
]

while True:
    try:
        behavior.startBehavior(random.choice(animations))
    except (EOFError):
        time.sleep(0.01)
        continue
    break
