import qi
import time
import random

session = qi.Session()
session.connect("tcp://192.168.1.110:9559")

tts = session.service("ALTextToSpeech")
tts.setVolume(0.6)
s = raw_input() 
bot_name = raw_input()
# s = "Hello, I am a bot. What is your name?"
# bot_name = "Pepper"
tts.setParameter("pitchShift", 1.1)


if bot_name == "Pepper":
    tts.setParameter("pitchShift", 1.1)
elif bot_name == "Reggie":
    tts.setParameter("pitchShift", 0.75)
elif bot_name == "Kaiyah":
    tts.setParameter("pitchShift", 1.2)
    s = "\\vct=100\\" + s
elif bot_name == "Custom":
    tts.setParameter("pitchShift", 1.1)
    # tts.setParameter("doubleVoice", 1)
    # tts.setParameter("doubleVoiceLevel", 0.5)
    # tts.setParameter("doubleVoiceTimeShift", 0.1)
    


behavior = session.service("ALBehaviorManager")

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
tts.say(s)
tts.setParameter("doubleVoice", 0)
tts.setParameter("pitchShift", 1.1)
