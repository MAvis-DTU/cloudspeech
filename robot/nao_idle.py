import qi
import time
import random

IP = raw_input()
time_bewtween_behaviors = float(raw_input()) #seconds
session = qi.Session()
session.connect(IP)

thinking_behaviors = [
        "animations/Stand/Gestures/Thinking_2",
        "animations/Stand/Gestures/Thinking_4",
        "animations/Stand/Gestures/Thinking_8",
]

listening_behaviors = [
        "animations/Stand/BodyTalk/Listening/Listening_1",
        "animations/Stand/BodyTalk/Listening/Listening_2",
        "animations/Stand/BodyTalk/Listening/Listening_3",
        "animations/Stand/BodyTalk/Listening/Listening_4",
        "animations/Stand/BodyTalk/Listening/Listening_5",
        "animations/Stand/BodyTalk/Listening/Listening_6",
        "animations/Stand/BodyTalk/Listening/Listening_7"
]

speaking_behaviors = [
        "animations/Stand/BodyTalk/Speaking/BodyTalk_1",
        "animations/Stand/BodyTalk/Speaking/BodyTalk_10",
        "animations/Stand/BodyTalk/Speaking/BodyTalk_11",
        "animations/Stand/BodyTalk/Speaking/BodyTalk_12",
        "animations/Stand/BodyTalk/Speaking/BodyTalk_13",
        "animations/Stand/BodyTalk/Speaking/BodyTalk_14",
        "animations/Stand/BodyTalk/Speaking/BodyTalk_15",
        "animations/Stand/BodyTalk/Speaking/BodyTalk_16",
        "animations/Stand/BodyTalk/Speaking/BodyTalk_2",
        "animations/Stand/BodyTalk/Speaking/BodyTalk_3",
        "animations/Stand/BodyTalk/Speaking/BodyTalk_4",
        "animations/Stand/BodyTalk/Speaking/BodyTalk_5",
        "animations/Stand/BodyTalk/Speaking/BodyTalk_6",
        "animations/Stand/BodyTalk/Speaking/BodyTalk_7",
        "animations/Stand/BodyTalk/Speaking/BodyTalk_8",
        "animations/Stand/BodyTalk/Speaking/BodyTalk_9"
]

waiting_behaviors = [
        "animations/Stand/Waiting/PlayHands_1",
        "animations/Stand/Waiting/PlayHands_2",
        "animations/Stand/Waiting/PlayHands_3",
        "animations/Stand/Waiting/ShowMuscles_1",
        "animations/Stand/Waiting/ShowMuscles_2",
        "animations/Stand/Waiting/ShowMuscles_3",
]


motion_service = session.service("ALMotion")
posture_service = session.service("ALRobotPosture")
behavior = session.service("ALBehaviorManager")

auto_life = session.service("ALAutonomousLife")

# Wake up robot
motion_service.wakeUp()

# Send robot to Stand Init
posture_service.goToPosture("StandInit", 0.5)

# Start breathing
motion_service.setBreathEnabled('Arms', True)

start = time.time()
while True:
        print(time.time() - start, time.time() - start > time_bewtween_behaviors)
        if time.time() - start > time_bewtween_behaviors:
                start = time.time()
                try:
                        chosen_behavior = random.choice(waiting_behaviors)
                        while not behavior.isBehaviorInstalled(chosen_behavior):
                                chosen_behavior = random.choice(waiting_behaviors)
                        behavior.startBehavior(chosen_behavior)
                        while behavior.isBehaviorRunning(chosen_behavior):
                                time.sleep(0.1)  # Check every 100ms if the behavior is still running
                        time.sleep(0.01)
                except (EOFError):
                        time.sleep(0.01)
                        continue


