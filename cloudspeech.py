#!/usr/bin/env python


# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Cloud Speech API sample application using the streaming API.
NOTE: This module requires the additional dependency `pyaudio`. To install
using pip:
    pip install pyaudio
Example usage:
    python transcribe_streaming_mic.py
"""

# [START speech_transcribe_streaming_mic]
from __future__ import division

import re
import sys

from google.cloud import speech

import pyaudio
from six.moves import queue

import openai
import os
import time
import random

import subprocess
#import pyttsx3

import argparse

from googlestream import *

from elevenlabs import voices, generate, play, set_api_key
from elevenlabs import set_api_key

import os
import subprocess

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'chatkey.json'

with open('openaiKey.txt', 'r') as f:
    os.environ['gpt4key'] = f.read()

api_key = os.getenv("gpt4key")

def nao_init():
    subprocess.run(['python2', 'robot/nao_init.py'],stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)

def nao_facetrack():
    subprocess.run(['python2', 'robot/nao_facetrack.py'],stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)

def say(s, bot_name):
    s = s.replace("\n", " ")
    subprocess.run(['python2', 'robot/nao_say.py'], input=bytes(s + '\n' + bot_name, encoding="utf-8"),stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)

def listen():
    subprocess.run(['python2', 'robot/nao_listen.py'], stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)

def objectDetectionSub():
    # open in a new terminal
    subprocess.Popen(['python3', 'objectMedia.py'])

def talking_gesture():
    subprocess.run(['python2', 'robot/nao_talking.py'],stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)


voices = {1: "21m00Tcm4TlvDq8ikWAM", # Rachel
          2: "rU18Fk3uSDhmg5Xh41o4", # Ryan Kurk
          3: "TWGIYqyf4ytM4ctpb0S1", # Pheobe
          4: "nIBoiUir3RAsl7ppOJeu", # Dave - deep and gruff
          5: "zrHiDhphv9ZnVXBqCLjz"} # Mimi

voice_descriptions = """
     \n0: pepper the robot voice.
     \n1: Female, very soothing, friendly and sophisticated.
     \n2: Male, bright, young, expressive narrative voice. It could soothe, excite, inform, and entertain, all at the same time.
     \n3: Female, young, playful and energetic voice, with a hint of assertiveness.
     \n4: Male, middle-aged, deep and gruff voice, raw and intimidating. 
     \n5: Female, young, light, delicate and sweet. It exudes innocence and charm. 
     \n\n
    """

set_api_key("cb4a60d9eaf1ad9514b055a3be1fc3b6")
# get the voices

def elevenLabsSay(text, latency=1):
    if voice_select == 0:
        say(text, "Pepper")
    else:
        # speak.Speak(text)
        #print("Generate Audio: START")
        #print("Text: ", text, file=sys.stderr)
        audio = generate(text=text, voice=voices[voice_select], latency=latency)
        #talking_gesture()
        #print("Generate Audio: END")
        #gesture_thread.start()
        play(audio)

# run object detection in a new terminal
#objectDetectionSub()
#time.sleep(7)

# we need some space
print('\n\n\n')

introductions = [
    lambda x: f"Hi, my name is {x}! What's your name?",
    lambda x: f"Hello! My name is {x}. May I ask what you are called?",
    lambda x: f"Good day! I am {x}. Would you tell me your name?",
    lambda x: f"Hi! I'm {x}, nice to meet you. What is your name?",
    lambda x: f"Welcome! I am {x}. Would you share your name with me?",
    lambda x: f"Hello! I'm {x}. Will you tell me what you are called?",
    lambda x: f"Hi, my name is {x}! May I ask for your name?",
    lambda x: f"Hi, I am {x}! What should I call you?",
    lambda x: f"Pleased to meet you! I am {x}. What's your name?",
    lambda x: f"Hello! My name is {x}. What's your name, my friend?",
    lambda x: f"Hi, I'm {x}! Would you tell me your name?",
    lambda x: f"Greetings! My name is {x}. What are you called?",
    lambda x: f"Hi, my name is {x}! Would you share your name with me?",
    lambda x: f"Good day, I am {x}! May I have the pleasure of knowing your name?",
    lambda x: f"Hello, I'm {x}! Can you tell me what you are called?"
]

# Some phrases to repeat the name
repeat_name = [
    "Sorry, I didn't catch your name. Could you tell it to me again?",
    "My mistake, I missed your name. Could you repeat it for me, please?",
    "Excuse me, but I didn't quite catch your name. Would you mind sharing it again?",
    "Oops, I didn't understand your reply. Could you tell me your name again, please?",
    "It seems I misunderstood your name. Could you say it one more time, please?",
    "Excuse me, but I didn't get your name right. What was it again?",
    "Sorry, but I didn't catch your name. Can you tell me again, please?",
    "Sorry about that - I didn't quite get your name. Could you repeat it, please?",
    "My apologies, but I didn't hear your name clearly. What was your name again?",
    "I must have misunderstood your response. Could you please tell me your name again?",
    "It appears I didn't quite get your name right. Would you mind telling it to me again?",
    "I apologize for the confusion. Could you please share your name again?",
    "I'm sorry, I didn't quite catch your name. Could you say it again for me, please?",
    "Excuse me, but I didn't understand your name. Could you kindly repeat it?",
    "Excuse me, but I missed your name. Can you let me know what it was again?"
]

def getConfig(language_code = "en-US"):         

    RATE = 16000
    CHUNK = int(RATE / 5)  # 100ms

    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )
    #streaming_config.VoiceActivityTimeout(speech_start_timeout = 10)

    return RATE, CHUNK, client, streaming_config


def getName(temperature, openaiClient, language='en-US', robot_name='Pepper', ): 

    # Some introductory phrases
    introduction = random.choice(introductions)(robot_name)
    print('Pepper: ' + introduction)
    elevenLabsSay(introduction)
    # os.system('say "%s"' % introduction)

    # get the config for the google speech api
    RATE, CHUNK, client, streaming_config = getConfig(language_code=language)

    # loop until the user says his name
    while True:
        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )
            #listen("Start")
            human_response = client.streaming_recognize(streaming_config, requests)
            human_response = listen_print_loop('Human', human_response)
            system_message  = 'What did the human say his name was in the following sentence? \n If the human did not specify write: -nothing, otherwise write ONLY the name of the human.\n\n'            
            
            response = openaiClient.chat.completions.create(
                model="gpt-3.5-turbo-16k-0613",
                messages=[
                        {       
                        "role": "system",
                        "content": system_message
                        },
                        {
                        "role": "user",
                        "content": human_response
                        }
                    ],
                temperature=temperature,
                max_tokens=10,
                top_p=top_p,
                frequency_penalty=1.5,
                presence_penalty=1,
            )
            pepper_response = response.choices[0].message.content

            if '-nothing' in pepper_response.lower():
                pepper_response = random.choice(repeat_name)
                pepper_response = pepper_response.replace('\n\n', '')
                elevenLabsSay(pepper_response)
                print('Pepper: ' + pepper_response)
                
                # os.system('say "%s"' % pepper_response)

            else: 
                name = pepper_response
                pepper_response = 'So your name is ' + pepper_response
                elevenLabsSay(pepper_response)
                print('Pepper: ' + pepper_response)
                
                # os.system('say "%s"' % pepper_response)
                return name, pepper_response
            
def changeVoice(prompt, voice):
    response = openaiClient.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {
                            "role": "user",
                            "content": f"You have the following voices to chose from. They have a number and a description: {voice_descriptions}. Below you will get a sentence said by a human. Your current voice is {voice}. If the human explicitly requests for you to change your voice, write the number that best matches the request: (number), otherwise write: -nothing. Note that it is only if the human asks about another voice, not if the human simply mentions the name of the voice.\\n\\n',\n\n{prompt}\n"
                            },
                            {
                            "role": "assistant",
                            "content": "2"
                            }
                        ],
                        temperature=1,
                        max_tokens=256,
                        top_p=1,
                        frequency_penalty=0,
                        presence_penalty=0
                        )
    response = response.choices[0].message.content
    try:
        voice = int(response)
        global voice_select
        if voice_select != voice:
            voice_select = voice
            print(voice_select)
            return 1
        else:
            return 0
    except:
        return 0
        

def getResponse(prompt, temperature, max_tokens, top_p, openaiClient, model="gpt-4-1106-preview"):

    response = openaiClient.chat.completions.create(
                model=model,
                messages=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=1.75,
                presence_penalty=1.75,
            )
    return response.choices[0].message.content

def startConversation(prompt, speaker, temperature, max_tokens, top_p, openaiClient, language='en-US'):

    # get the config for the google speech api
    RATE, CHUNK, client, streaming_config = getConfig(language_code=language)
    # start the conversation loop 
    while True:
        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )
            
            human_response = client.streaming_recognize(streaming_config, requests)
            
            #print('Human: ')
            human_response = listen_print_loop(speaker, human_response)
            voice_changed = changeVoice('Human:' + human_response, voice=voice_select)

            # fetch the string from objects.txt 
            with open('objects.txt', 'r') as file:
                objects = file.read()

            prompt += [{"role": "user", "content": human_response + '\n\n' + objects}]

            if voice_changed:
                response = "Certainly! I will change my voice. Is it better now?"
            else: 
                response = getResponse(prompt, temperature=temperature, max_tokens=max_tokens, top_p = top_p, openaiClient=openaiClient)

            elevenLabsSay(response)
            print('Pepper: ' + response)

            prompt += [{"role": "assistant", "content": response}]
    return 0

def getParser():

    # get prompt from file 
    with open('prompt.txt', 'r') as file:
        prompt = file.read()

     # initialize argparser 
    parser = argparse.ArgumentParser(description='Process some integers.')

    # write an argparser for all variables 
    parser.add_argument('--name', type=str, default='Human', help='name of the person you are talking to')
    parser.add_argument('--prompt', type=str, default=prompt, help='prompt to start the conversation')
    parser.add_argument('--temperature', type=float, default=0.7, help='temperature for the GPT-3 model, float between 0 and 2')
    parser.add_argument('--max_tokens', type=int, default=300, help='max tokens for the GPT-3 model')
    parser.add_argument('--top_p', type=float, default=1, help='top p for the GPT-3 model')
    parser.add_argument('--language', type=str, default='en-US', help='language for the GPT-3 model: en-US, en-GB, da-DK etc. see https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages for more.')
    parser.add_argument('--final_read', type=bool, default=False, help='if true the final text will be read out loud by the robot')
    parser.add_argument('--init_voice', type=int, default=1, help='init voice for the robot, 0. Robot, 1. Rachel, 2. Ryan Kurk, 3. Pheobe, 4. Dave, 5. Mimi')
    # parse the arguments
    args = parser.parse_args()

    # get the variables from the arguments
    name = args.name
    prompt = args.prompt
    temperature = args.temperature
    max_tokens = args.max_tokens
    top_p = args.top_p
    language = args.language
    final_read = args.final_read
    global voice_select
    voice_select = args.init_voice
    return name, prompt, temperature, max_tokens, top_p, language, final_read

if __name__ == "__main__":
    # get the arguments
    name, prompt, temperature, max_tokens, top_p, language, final_read = getParser()

    if final_read:
        # read the final_read.txt
        with open('final_read.txt', 'r') as file:
            final_read = file.read()
        elevenLabsSay(final_read)

    else:
        #nao_facetrack()
        #objectDetectionSub()
        openaiClient = openai.OpenAI(api_key=api_key)

        # get the name of the human if not specified using argument parser
        if name == 'Human':
            name, pepper_response = getName(temperature=temperature, openaiClient=openaiClient, language=language)
            prompt = [{"role": "system", "content": prompt}, {"role": "assistant", "content": pepper_response}]
        else:
            prompt = [{"role": "system", "content": prompt}, {"role": "assistant", "content": ""}]

        # start the conversation
        startConversation(prompt, name, temperature=temperature, max_tokens=max_tokens, top_p=top_p, language=language, openaiClient=openaiClient)

