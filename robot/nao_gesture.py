import qi
import time
import random

IP = raw_input() 
split_sentences = raw_input()
gesture_numbers = raw_input()
gesture_numbers = gesture_numbers.strip('[]').split(', ')
gesture_numbers = [i.strip(' ') for i in gesture_numbers]

time.sleep(1)

session = qi.Session()
session.connect(IP)
behavior = session.service("ALBehaviorManager")

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


for i in gesture_numbers:
    try:
        chosen_behavior = random.choice(animations[i])
        while not behavior.isBehaviorInstalled(chosen_behavior):
                chosen_behavior = random.choice(animations[i])
        behavior.startBehavior(chosen_behavior)
        while behavior.isBehaviorRunning(chosen_behavior):
            time.sleep(0.1)  # Check every 100ms if the behavior is still running
        time.sleep(0.01)
    except (EOFError):
        time.sleep(0.01)
        continue