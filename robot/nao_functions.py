import subprocess
import threading

def nao_init(IP):
    subprocess.run(['python2', 'robot/nao_init.py'], input=bytes(IP, encoding="utf-8"))

def nao_facetrack(IP):
    subprocess.run(['python2', 'robot/nao_facetrack.py'], input=bytes(IP, encoding="utf-8"))

def say(IP, s, bot_name, split_sentences, gesture_thread):
    gesture_thread.run()
    s = s.replace("\n", " ")
    subprocess.run(['python2', 'robot/nao_say.py'], input=bytes(IP + '\n' + s + '\n' + bot_name, encoding="utf-8"))
    gesture_thread.terminate()

# def nao_gesture(IP, split_sentences, gesture_number):
#     """
#     Non-blocking subprocess call to run in parallel with the main program (elevenlabs).
#     """
#     p = subprocess.Popen(['python2', 'robot/nao_gesture.py'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)    
#     p.communicate(input=bytes(IP + '\n' + str(split_sentences) + '\n' + str(gesture_number), encoding="utf-8"))

