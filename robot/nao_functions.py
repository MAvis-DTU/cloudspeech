import subprocess
import threading
import qi
import time
import random

animations =   {'0': ["animations/Stand/Gestures/Enthusiastic_4",    # Happy
                        "animations/Stand/Gestures/Enthusiastic_5",
                        "animations/Stand/Gestures/Hysterical_1"],
                '1': ["animations/Stand/Gestures/Desperate_1",       # Sad
                        "animations/Stand/Gestures/Desperate_2",
                        "animations/Stand/Gestures/Desperate_4",
                        "animations/Stand/Gestures/Desperate_5"], 
                '2': ["animations/Stand/Gestures/Yes_1",             # Affirmative
                        "animations/Stand/Gestures/Yes_2",
                        "animations/Stand/Gestures/Yes_3"],
                '3': ["animations/Stand/Gestures/IDontKnow_1",       # Unfamiliar
                        "animations/Stand/Gestures/IDontKnow_2",
                        "animations/Stand/Gestures/IDontKnow_3"],
                '4': ["animations/Stand/Gestures/Think_1",           # Thinking
                        "animations/Stand/Gestures/Think_2",
                        "animations/Stand/Gestures/Think_3",
                        "animations/Stand/Gestures/Thinking_1",
                        "animations/Stand/Gestures/Thinking_3",
                        "animations/Stand/Gestures/Thinking_4",
                        "animations/Stand/Gestures/Thinking_6",
                        "animations/Stand/Gestures/Thinking_8"],
                '5': ["animations/Stand/Gestures/Explain_2",         # Explaining
                    "animations/Stand/Gestures/Explain_3", 
                    "animations/Stand/Gestures/Explain_4", 
                    "animations/Stand/Gestures/Explain_5", 
                    "animations/Stand/Gestures/Explain_6", 
                    "animations/Stand/Gestures/Explain_7", 
                    "animations/Stand/Gestures/Explain_8", 
                    "animations/Stand/Gestures/Explain_10", 
                    "animations/Stand/Gestures/Explain_11",    
                    "animations/Stand/Gestures/YouKnowWhat_1",
                    "animations/Stand/Gestures/YouKnowWhat_2",
                    "animations/Stand/Gestures/YouKnowWhat_3"]
                }

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


class NaoServices:
    def __init__(self, IP):        
        session = qi.Session()
        session.connect(IP)
        self._load_services()
    
    def _load_services(self):
        self.posture_service = self.session.service("ALRobotPosture")
        self.motion_service = self.session.service("ALMotion")
        self.tracker_service = self.session.service("ALTracker")
        self.behavior_service = self.session.service("ALBehaviorManager")
        self.auto_life_service = self.session.service("ALAutonomousLife")

    def nao_init(self):
        while True:
            try:
                self.posture_service.goToPosture("Stand", 0.5)
            except (EOFError):
                time.sleep(0.01)
                continue
            break

    def nao_facetrack(self):
        self.motion_service.wakeUp()
        targetName = "Face"
        faceWidth = 0.1
        self.tracker_service.registerTarget(targetName, faceWidth)
        self.tracker_service.track(targetName)

    def nao_gestures(self, gesture_numbers):
        for i in gesture_numbers:
            try:
                chosen_behavior = random.choice(animations[i])
                while not self.behavior_service.isBehaviorInstalled(chosen_behavior):
                        chosen_behavior = random.choice(animations[i])
                self.behavior_service.startBehavior(chosen_behavior)
                while self.behavior_service.isBehaviorRunning(chosen_behavior):
                    time.sleep(0.1)  # Check every 100ms if the behavior is still running
                time.sleep(0.01)
            except (EOFError):
                time.sleep(0.01)
                continue
    
    def nao_listen(self):
        ...
    
    def nao_say(self, text):
        ...
        
    def nao_stop_behavior(self):
        ...
    
    def nao_talking(self):
        ...
    
    def nao_idle(self, time_bewtween_behaviors, b_type=waiting_behaviors):
        # Wake up robot
        self.motion_service.wakeUp()

        # Send robot to Stand Init
        self.posture_service.goToPosture("StandInit", 0.5)

        # Start breathing
        self.motion_service.setBreathEnabled('Arms', True)
        
        start = time.time()
        while True:
            print(time.time() - start, time.time() - start > time_bewtween_behaviors)
            if time.time() - start > time_bewtween_behaviors:
                start = time.time()
                try:
                    chosen_behavior = random.choice(b_type)
                    while not self.behavior_service.isBehaviorInstalled(chosen_behavior):
                        chosen_behavior = random.choice(b_type)
                    self.behavior_service.startBehavior(chosen_behavior)
                    while self.behavior_service.isBehaviorRunning(chosen_behavior):
                        time.sleep(0.1)  # Check every 100ms if the behavior is still running
                    time.sleep(0.01)
                except (EOFError):
                    time.sleep(0.01)
                    continue
    
    def nao_terminate_idle(self):
        # # Stop breathing
        self.motion_service.killAll()

        self.motion_service.setBreathEnabled('Body', False)
        self.motion_service.setBreathEnabled('Arms', False)
        self.motion_service.setBreathEnabled('Head', False)
        self.motion_service.setBreathEnabled('Legs', False)
        self.motion_service.setBreathEnabled('LArm', False)
        self.motion_service.setBreathEnabled('RArm', False)

        # # Go to rest position
        # motion_service.rest()
        self.posture_service.goToPosture("StandInit", 0.5)