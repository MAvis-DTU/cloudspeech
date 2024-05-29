import qi
import time
import random


IP = raw_input() 
s = raw_input() 
bot_name = raw_input()
session = qi.Session()
session.connect(IP)

tts = session.service("ALTextToSpeech")
tts.say(s)