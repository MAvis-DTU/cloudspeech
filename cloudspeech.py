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

from robot.nao_functions import * 
import re
# import sys

from google.cloud import speech

# import pyaudio

import openai
import os
import time
import random
import threading

import argparse

from googlestream import *

from elevenlabs import voices, generate, play, set_api_key
from elevenlabs import set_api_key

import os
import subprocess


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'credentials/chatkey.json'

with open('credentials/openaiKey.txt', 'r') as f:
    os.environ['gpt4key'] = f.read()

api_key = os.getenv("gpt4key")

# Initialise verbose statement
global verbose
verbose = False

# Elevenlab voices
eng_voices = {1: "21m00Tcm4TlvDq8ikWAM", # Rachel
         2: "rU18Fk3uSDhmg5Xh41o4", # Ryan Kurk
         3: "TWGIYqyf4ytM4ctpb0S1", # Pheobe
         4: "nIBoiUir3RAsl7ppOJeu", # Dave - deep and gruff
         5: "zrHiDhphv9ZnVXBqCLjz"} # Mimi

multi_voices = voices()

global voice_select
voice_select = 1

set_api_key("cb4a60d9eaf1ad9514b055a3be1fc3b6")
# get the voices


def elevenLabsSay(text, IP, multi_lingual=False):
    if IP is not None:
        split_sentences, gesture_numbers = getGestures(text, IP)
        gesture_thread = threading.Thread(target=nao_gesture, args=(IP, split_sentences, gesture_numbers))

    if voice_select == 0 and IP is not None:
        assert IP is not None, "IP address is not specified, and thus the robot cannot speak. voice_select 0 is not possible."
        say(IP, text, "Pepper", gesture_thread=gesture_thread)
    else:
        # Verbose output
        if verbose:
            print("-----------------")
            print("Generate Audio: START")
            start = time.time()
        
        if multi_lingual:
            audio = generate(text=text, voice=multi_voices[1], model="eleven_multilingual_v2")
        else:
            audio = generate(text=text, voice=eng_voices[voice_select])
        
        # Verbose output
        if verbose:
            end = time.time()
            print(f"Time taken: {end-start:.2f} s", file=sys.stderr)
            print("Generate Audio: END\n")
        # Create gestures if the robot is connected
        if IP is not None:
            gesture_thread.start()
        play(audio)

def getGestures(IP, text):

    prompt = [
        {
        "role": "system",
        "content": "Given a paragraph of text, annotate every 10 words in that paragraph with the most appropriate tag. You should always give a tag no matter what. The tags are to be placed in square brackets. \n\nFollowing tags are available:\n0. Happy\n1. Sad\n2. Affirmative\n3. Unfamiliar\n4. Thinking\n5. Explain\n\nIt should be on the form:\n\nHi, [5] have you heard about the recent news? They are [1] quite horrific to say the [1] least."
        },
        {
        "role": "user",
        "content": "I am so very sad today. My parents are getting a divorce and I am unsure how to react to it."
        },
        {
        "role": "assistant",
        "content": "I am [5] so very sad [1] today. My parents [2] are getting a divorce [1] and I am unsure how to [5] react to it."
        },
        {
        "role": "user",
        "content": "I just graduated my Masters today! What a thrill it was."
        },
        {
        "role": "assistant",
        "content": "I just graduated my Masters [2] today! What a [0] thrill it [2] was."
        },
        {
        "role": "user",
        "content": "I don't understand what you mean. Let me just think about it."
        },
        {
        "role": "assistant",
        "content": "I don't understand what you [1] mean. Let me just [4] think about [4] it."
        },
        {
        "role": "user",
        "content": {text}
        }
    ]
    if verbose:
        print("Get Gestures: START")
        start = time.time()
    response = getResponse(prompt, temperature=1, max_tokens=256, top_p=1, openaiClient=openaiClient, frequency_penalty=0, presence_penalty=0)
    if verbose:
        end = time.time()
        print("Time taken: ", end-start, file=sys.stderr)
        print("Get Gestures: END\n")
    gesture_numbers = [int(gesture) for gesture in re.findall(r'\[(\d+)\]', response)]
    split_sentences = re.split(r'\[\d+\]', response)
    return split_sentences, gesture_numbers

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

def getResponse(prompt, temperature, max_tokens, top_p, openaiClient, frequency_penalty=1.75, presence_penalty=1.75, model="gpt-4-1106-preview"):

    response = openaiClient.chat.completions.create(
                model=model,
                messages=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
            )
    return response.choices[0].message.content

def changeVoice(prompt, voice):

    voice_prompt = [
                    {
                    "role": "user",
                    "content": f"You have the following voices to chose from. They have a number and a description: {voice_descriptions}. Below you will get a sentence said by a human. Your current voice is {voice}. If the human explicitly requests for you to change your voice, write the number that best matches the request: (number), otherwise write: -nothing. Note that it is only if the human asks about another voice, not if the human simply mentions the name of the voice.\\n\\n',\n\n{prompt}\n"
                    },
                    {
                    "role": "assistant",
                    "content": "2"
                    }
                    ]
    response = getResponse(voice_prompt, temperature=1, max_tokens=256, top_p=1, openaiClient=openaiClient, frequency_penalty=0, presence_penalty=0)
    try:
        voice = int(response)
        global voice_select
        if voice_select != voice:
            voice_select = voice
            if verbose:
                print("Voice changed to: ", voice_select)
            return 1
        else:
            if verbose:
                print("Voice not changed")
            return 0
    except:
        if verbose:
            print("Voice not changed")
        return 0

def getName(temperature, openaiClient, IP, language='en-US', robot_name='Pepper', multi_lingual=True): 
    # Some introductory phrases
    prompt = [{"role": "system", "content": f"You are a robot called Pepper, and you are engaging in a conversation. Briefly introduce yourself in one or two sentences and ask for the other person's name in a fun and engaging way."}]
    introduction = getResponse(prompt, temperature=temperature, max_tokens=255, top_p=1, openaiClient=openaiClient)
    elevenLabsSay(introduction, IP, multi_lingual=multi_lingual)
    print('Pepper: ' + introduction)
    if verbose:
        print("-----------------")

    # get the config for the google speech api
    RATE, CHUNK, client, streaming_config = getConfig(language_code=language)

    # loop until the user says their name
    while True:
        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )
            #listen("Start")
            human_response = client.streaming_recognize(streaming_config, requests)
            human_response = listen_print_loop('Human', human_response, verbose=verbose)
            system_message  = 'What did the human say his name was in the following sentence? \n If the human did not specify write: -nothing, otherwise write ONLY the name of the human.\n\n'

            prompt = [{"role": "system","content": system_message}, {"role": "user", "content": human_response}]          
            
            pepper_response = getResponse(prompt, temperature=temperature, max_tokens=10, top_p=top_p, \
                                          openaiClient=openaiClient, frequency_penalty=1.5, presence_penalty=1, \
                                          model="gpt-3.5-turbo-16k-0613")

            if '-nothing' in pepper_response.lower():
                prompt = [{"role": "system", "content": f"You missed the other person's name, and you should ask again. Be kind and understanding."}]
                pepper_response = getResponse(prompt, temperature=temperature, max_tokens=10, top_p=top_p, openaiClient=openaiClient)
                elevenLabsSay(pepper_response, IP, multi_lingual=multi_lingual)
                print('Pepper: ' + pepper_response)
                if verbose:
                    print("-----------------")
            else: 
                name = pepper_response
                prompt = [{"role": "system", "content": f"Great! So the human has introduced themselves as {name}. Now acknowledge it."}]
                pepper_response = getResponse(prompt, temperature=temperature, max_tokens=255, top_p=top_p, openaiClient=openaiClient)
                elevenLabsSay(pepper_response, IP, multi_lingual=multi_lingual)
                print('Pepper: ' + pepper_response)
                if verbose:
                    print("-----------------")
                return name, pepper_response

def startConversation(prompt, speaker, temperature, max_tokens, top_p, openaiClient, IP, language='en-US', multi_lingual=True):
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
            human_response = listen_print_loop(speaker, human_response, verbose=verbose)
            voice_changed = changeVoice('Human:' + human_response, voice=voice_select)

            # fetch the string from objects.txt 
            with open('objects.txt', 'r') as file:
                objects = file.read()

            prompt += [{"role": "user", "content": human_response + '\n\n' + objects}]

            if voice_changed:
                # response = "Certainly! I will change my voice. Is it better now?"
                voice_prompt = [{"role": "system", "content": "You have changed your voice. Showcase the new voice and ask if the human likes it. Everything you do say will be in {language}."}]
                response = getResponse(voice_prompt, temperature=temperature, max_tokens=max_tokens, top_p=top_p, openaiClient=openaiClient)
            else: 
                response = getResponse(prompt, temperature=temperature, max_tokens=max_tokens, top_p = top_p, openaiClient=openaiClient)

            elevenLabsSay(response, IP, multi_lingual=multi_lingual)
            print('Pepper: ' + response)
            if verbose:
                print("-----------------")

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
    parser.add_argument('--ip', type=str, default=None, help='IP address of the robot. (default: %(default)s)')
    parser.add_argument('--prompt', type=str, default=prompt, help='prompt to start the conversation')
    parser.add_argument('--temperature', type=float, default=0.7, help='temperature for the GPT-3 model, float between 0 and 2')
    parser.add_argument('--max_tokens', type=int, default=300, help='max tokens for the GPT-3 model')
    parser.add_argument('--top_p', type=float, default=1, help='top p for the GPT-3 model')
    parser.add_argument('--language', type=str, default='da-DK', help='language for the GPT-3 model: en-US, en-GB, da-DK etc. see https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages for more.')
    parser.add_argument('--final_read', type=bool, default=False, help='if true the final text will be read out loud by the robot')
    parser.add_argument('--init_voice', type=int, default=2, help='init voice for the robot, 0. Robot, 1. Rachel, 2. Ryan Kurk, 3. Pheobe, 4. Dave, 5. Mimi')
    parser.add_argument('--od', type=bool, default=False, help='if true the object detection will be run')
    parser.add_argument('-v', '--verbose', action='store_true', help='increase output verbosity')
    parser.add_argument('-ml', '--multi_lingual', action='store_true', help='use the multi-lingual model')
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
    global verbose
    verbose = args.verbose

    multi_lingual = args.multi_lingual

    if args.od:
        if verbose:
            print("Running object detection")
        # Run the objectMedia.py script
        subprocess.run(['python3', 'models/objectMedia.py'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    IP = args.ip

    return IP, name, prompt, temperature, max_tokens, top_p, language, final_read, multi_lingual

if __name__ == "__main__":
    # get the arguments
    IP, name, prompt, temperature, max_tokens, top_p, language, final_read, multi_lingual = getParser()
    global voice_descriptions
    
    if IP is not None:
        IP = f"tcp://{IP}:9559"
        nao_init(IP)
        nao_facetrack(IP)
        voice_descriptions = """
        \n0: pepper the robot voice.
        \n1: Female, very soothing, friendly and sophisticated.
        \n2: Male, bright, young, expressive narrative voice. It could soothe, excite, inform, and entertain, all at the same time.
        \n3: Female, young, playful and energetic voice, with a hint of assertiveness.
        \n4: Male, middle-aged, deep and gruff voice, raw and intimidating. 
        \n5: Female, young, light, delicate and sweet. It exudes innocence and charm. 
        \n\n
        """
    else:
        voice_descriptions = """
        \n1: Female, very soothing, friendly and sophisticated.
        \n2: Male, bright, young, expressive narrative voice. It could soothe, excite, inform, and entertain, all at the same time.
        \n3: Female, young, playful and energetic voice, with a hint of assertiveness.
        \n4: Male, middle-aged, deep and gruff voice, raw and intimidating. 
        \n5: Female, young, light, delicate and sweet. It exudes innocence and charm. 
        \n\n
        """

    openaiClient = openai.OpenAI(api_key=api_key)
    # get the name of the human if not specified using argument parser
    if name == 'Human':
        name, pepper_response = getName(temperature=temperature, openaiClient=openaiClient, language=language, IP=IP, multi_lingual=multi_lingual)
        prompt = [{"role": "system", "content": prompt}, {"role": "assistant", "content": pepper_response}]
    else:
        prompt = [{"role": "system", "content": prompt}, {"role": "assistant", "content": ""}]

    # start the conversation
    startConversation(prompt, name, temperature=temperature, max_tokens=max_tokens, top_p=top_p, language=language, openaiClient=openaiClient, IP=IP, multi_lingual=multi_lingual)

