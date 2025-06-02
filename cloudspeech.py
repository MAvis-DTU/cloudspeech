#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from concurrent.futures import thread
from __init__ import *

from robot.nao_functions import * 
import re
# import sys

from google.cloud import speech

# import pyaudio

import openai
import os
import time
from threading import Thread
import time
import argparse
import sys
from googlestream import *

from elevenlabs import voices, generate, play, set_api_key
from elevenlabs import set_api_key

import os
import subprocess

import io
from pydub import AudioSegment
import librosa
import soundfile as sf
import io

# # For NLP purposes
# import nltk
# nltk.download('punkt')
# from nltk.tokenize import sent_tokenize


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'credentials/keep/google_key.json'

with open('credentials/keep/openai_key.txt', 'r') as f:
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

# Voice for multi-lingual tts model
multi_voices = voices()

global voice_select
voice_select = 1
with open('credentials/keep/elevenlabs_key.txt', 'r') as f:
    elevenlabs_key = f.read()
    
set_api_key(elevenlabs_key)    
    
class GestureThread(Thread):
    def __init__(self, IP, split_sentences, gesture_numbers):
        Thread.__init__(self)
        self.IP = IP
        self.split_sentences = split_sentences
        self.gesture_numbers = gesture_numbers
        self.p = None
    
    def run(self):
        try:
            self.p = subprocess.Popen(['python2', 'robot/nao_gesture.py'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
            input_data = bytes(self.IP + '\n' + str(self.split_sentences) + '\n' + str(self.gesture_numbers), encoding="utf-8")
            
            # Start a new thread to handle the communicate method
            communicate_thread = Thread(target=self._communicate, args=(input_data,))
            communicate_thread.start()

        except subprocess.CalledProcessError as e:
            print(f"Error : {e.output}")
        
    def _communicate(self, input_data):
        self.p.communicate(input=input_data)

    def terminate(self):
        if self.p:
            self.p.terminate()
            self.p.kill()
            

def change_pitch(audio_bytes, pitch_shift_steps):
    # Step 1: Read MP3 bytes using pydub and convert to WAV format in-memory
    audio_buffer = io.BytesIO(audio_bytes)
    audio = AudioSegment.from_file(audio_buffer, format="mp3")
    
    # Step 2: Convert the audio data to raw samples (WAV format in-memory)
    wav_io = io.BytesIO()
    audio.export(wav_io, format="wav")
    wav_io.seek(0)
    
    # Step 3: Load the audio into librosa
    y, sr = librosa.load(wav_io, sr=None)
    
    # Step 4: Perform pitch shifting using librosa (corrected argument usage)
    shifted_audio = librosa.effects.pitch_shift(y, sr=sr, n_steps=pitch_shift_steps)
    
    # Step 5: Convert the shifted audio back to WAV format
    wav_shifted_io = io.BytesIO()
    sf.write(wav_shifted_io, shifted_audio, samplerate=sr, format='WAV')
    
    # Step 6: Convert the WAV back to MP3 format using pydub
    wav_shifted_io.seek(0)
    shifted_audio_segment = AudioSegment.from_file(wav_shifted_io, format="wav")
    
    # Step 7: Export the shifted audio as MP3 to a byte stream
    mp3_shifted_io = io.BytesIO()
    shifted_audio_segment.export(mp3_shifted_io, format="mp3", bitrate="192k")
    
    # Move to the beginning of the BytesIO object before reading
    mp3_shifted_io.seek(0)
    
    return mp3_shifted_io.read()
set_api_key("cb4a60d9eaf1ad9514b055a3be1fc3b6")

def run_yolo_in_subprocess(verbose, device, vision, vision_freq, camera):
    # Path to the yolo_detection.py script
    script_path = "models/objectYolo.py"

    # Build the command with arguments to pass to the subprocess
    if vision: 
        command = [
            "python",  # or "python" depending on your environment
            script_path,  # The script you want to run
            "--verbose", str(verbose),
            "--vision",
            "--device", device,
            "--vision_freq", str(vision_freq),
            "--camera", str(camera)
        ]
    else:
        command = [
            "python",  # or "python" depending on your environment
            script_path,  # The script you want to run
            "--verbose", str(verbose),
            "--device", device,
            "--vision_freq", str(vision_freq),
            "--camera", str(camera)
        ]
    # run the object detection in a separate subprocess
        
    if sys.platform == "win32":
        process = subprocess.Popen(command)
    else:
        # Set the environment variable for PyTorch MPS fallback
        env = {**os.environ, "PYTORCH_ENABLE_MPS_FALLBACK": "1"}

        # Run the command as a subprocess with the modified environment
        process = subprocess.Popen(command, env=env)


def elevenLabsSay(text, IP, gesture_thread=None, multi_lingual=False, process_audio=False):
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
            audio = generate(text=text, voice=multi_voices[voice_select], model="eleven_multilingual_v2")
        else:
            audio = generate(text=text, voice=eng_voices[voice_select])
        
        if process_audio:
            # Alter audio sound to be more robotic
            audio = change_pitch(audio, pitch_shift_steps=2) 
        
        # Verbose output
        if verbose:
            end = time.time()
            print(f"Time taken: {end-start:.2f} s", file=sys.stderr)
            print("Generate Audio: END\n")
        # Create gestures if the robot is connected
        if gesture_thread is not None:
            gesture_thread.run()
            play(audio)
            gesture_thread.terminate()
        else:
            play(audio)


def get_gestures(text, openaiClient):

    # Few shot prompting for gestures
    # It was found that it improved the output of the models and also increasing the prompting speed.
    prompt = [
        {
        "role": "system",
        "content": "Given a paragraph of text, annotate every 15 words in that paragraph with the most appropriate tag. You should always give a tag no matter what. The tags are to be placed in square brackets. \n\nFollowing tags are available:\n0. Happy\n1. Sad\n2. Affirmative\n3. Unfamiliar\n4. Thinking\n5. Explain\n\nIt should be on the form:\n\nHi, [5] have you heard about the recent news? They are [1] quite horrific to say the least."
        },
        {
        "role": "user",
        "content": [{"type": "text", "text": "I am so very sad today. My parents are getting a divorce and I am unsure how to react to it."}]
        },
        {
        "role": "assistant",
        "content": [{"type": "text", "text": "I am [5] so very sad today. My parents are getting a divorce [1] and I am unsure how to [5] react to it."}]
        },
        {
        "role": "user",
        "content": [{"type": "text", "text": "I just graduated my Masters today! What a thrill it was."}]
        },
        {
        "role": "assistant",
        "content": [{"type": "text", "text": "I just graduated my Masters [2] today! What a thrill it [2] was."}]
        },
        {
        "role": "user",
        "content": [{"type": "text", "text": "I don't understand what you mean. Let me just think about it."}]
        },
        {
        "role": "assistant",
        "content": [{"type": "text", "text": "I don't understand what you [1] mean. Let me justf think about [4] it."}]
        },
        {
        "role": "user",
        "content": [{"type": "text", "text": text}]
        }
    ]
    if verbose:
        print("Get Gestures: START")
        start = time.time()
    response = getResponse(prompt, temperature=1, max_tokens=256, top_p=1, openaiClient=openaiClient, frequency_penalty=0, presence_penalty=0)
    if verbose:
        print(response)
        end = time.time()
        print(f"Time taken: {end-start:.2f} s", file=sys.stderr)
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
        config=config, interim_results=True, single_utterance=False 
    )
    #streaming_config.VoiceActivityTimeout(speech_start_timeout = 10)

    return RATE, CHUNK, client, streaming_config

def getResponse(prompt, temperature, max_tokens, top_p, openaiClient, frequency_penalty=1.75, presence_penalty=1.75, model="gpt-4o"): # was gpt-4-turbo

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
                    "content": [{"type":"text", "text":f"You have the following voices to chose from. They have a number and a description: {voice_descriptions}. Below you will get a sentence said by a human. Your current voice is {voice}. If the human explicitly requests for you to change your voice, write the number that best matches the request: (number), otherwise write: -nothing. Note that it is only if the human asks about another voice, not if the human simply mentions the name of the voice.\\n\\n',\n\n{prompt}\n"
                                }
                                ]
                    },
                    {
                    "role": "assistant",
                    "content": [{"type": "text",
                                 "text": "2"}]
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

# def remove_incomplete_sentence(text):
#     sentences = sent_tokenize(text)
#     if sentences:
#         last_sentence = sentences[-1]
#         if last_sentence.endswith('.') or last_sentence.endswith('!') or last_sentence.endswith('?'):
#             return text
#         else:
#             # Remove the last sentence
#             text = text.rsplit(sentences[-1], 1)[0]
#             return text
#     else:
#         return text
    
def conditional_say(pepper_response, bot_name, IP, openaiClient, multi_lingual, process_audio=False):
    if IP:
        split_sentences, gesture_numbers = get_gestures(pepper_response, openaiClient)
        gesture_thread = GestureThread(IP, split_sentences, gesture_numbers)
        if voice_select == 0 and not multi_lingual:
            say(IP, pepper_response, bot_name, gesture_thread)
        else:
            elevenLabsSay(pepper_response, IP, gesture_thread, multi_lingual=multi_lingual, process_audio=process_audio)
    else:
        elevenLabsSay(pepper_response, IP, multi_lingual=multi_lingual, process_audio=process_audio)


def getName(main_prompt, temperature, openaiClient, IP, language='en-US', robot_name='Pepper', multi_lingual=True, process_audio=False): 
    # Some introductory phrases
    prompt = [{"role": "system", "content": [{"type": "text", "text": main_prompt + '\n\n' + f"You are a robot called Pepper, and you are engaging in a conversation. Briefly introduce yourself in one sentence ask for the other person's name in a fun and engaging way. The language is: {language}"}]}]
    introduction = getResponse(prompt, temperature=temperature, max_tokens=255, top_p=1, openaiClient=openaiClient)
    # elevenLabsSay(introduction, IP, multi_lingual=multi_lingual)
    conditional_say(introduction, robot_name, IP, openaiClient=openaiClient, multi_lingual=multi_lingual, process_audio=process_audio)

    print(f'{robot_name}: ' + introduction)
    if verbose:
        print("-----------------")

    # get the config for the google speech api
    RATE, CHUNK, client, streaming_config = getConfig(language_code=language)

    # loop until the user says their name
    while True:
        with MicrophoneStream(RATE, CHUNK) as stream:
            if verbose: 
                print("-----------------")
                print("Listening: START")
                start = time.time()
            audio_generator = stream.generator()
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )
            #listen("Start")
            human_response = client.streaming_recognize(streaming_config, requests)
            human_response = listen_print_loop('Human', human_response, verbose=verbose)
            if verbose:
                end = time.time()
                print(f"Time taken: {end-start:.2f} s")
                print("Listening: END\n")
                print("-----------------")
            system_message  = 'What did the human say his name was in the following sentence? \n If the human did not specify write: -nothing, otherwise write ONLY the name of the human.\n\n'

            prompt = [{"role": "system", "content": [{"type": "text", "text": system_message}]}, {"role": "user", "content": [{"type": "text", "text": human_response}]}]          
            
            pepper_response = getResponse(prompt, temperature=temperature, max_tokens=255, top_p=top_p, \
                                          openaiClient=openaiClient, frequency_penalty=1.5, presence_penalty=1, \
                                          model="gpt-4-turbo")

            if '-nothing' in pepper_response.lower() or '-ingenting' in pepper_response.lower():
                prompt = [{"role": "system", "content": [{"type": "text", "text": main_prompt + '\n\n' + f"You missed the other person's name, and you should ask again. Be kind and understanding. The response should be in {language}."}]}]
                pepper_response = getResponse(prompt, temperature=temperature, max_tokens=255, top_p=top_p, openaiClient=openaiClient)
                # elevenLabsSay(pepper_response, IP, multi_lingual=multi_lingual)
                conditional_say(pepper_response, robot_name, IP, openaiClient=openaiClient, multi_lingual=multi_lingual, process_audio=process_audio)
                print('Pepper: ' + pepper_response)
                if verbose:
                    print("-----------------")
            else: 
                name = pepper_response
                prompt = [{"role": "system", "content": [{"type": "text", "text": main_prompt + '\n\n' + f"Great! So the human has introduced themselves as {name}. Now acknowledge it. The response should be in {language}."}]}]
                pepper_response = getResponse(prompt, temperature=temperature, max_tokens=255, top_p=top_p, openaiClient=openaiClient)
                # elevenLabsSay(pepper_response, IP, multi_lingual=multi_lingual)
                conditional_say(pepper_response, robot_name, IP, openaiClient=openaiClient, multi_lingual=multi_lingual, process_audio=process_audio)

                print('Pepper: ' + pepper_response)
                if verbose:
                    print("-----------------")
                return name, pepper_response


def startConversation(prompt, speaker, temperature, max_tokens, top_p, openaiClient, IP, language='en-US', multi_lingual=True, vision=True, process_audio=False):
    # get the config for the google speech api
    RATE, CHUNK, client, streaming_config = getConfig(language_code=language)
    voice_changed = 0
    # start the conversation loop 
    while True:
        with MicrophoneStream(RATE, CHUNK) as stream:
            if verbose: 
                print("-----------------")
                print("Listening: START")
                start = time.time()
            audio_generator = stream.generator()
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )
            human_response = client.streaming_recognize(streaming_config, requests)
            
            #print('Human: ')
            try:
                human_response = listen_print_loop(speaker, human_response, verbose=verbose)
            except Exception as e:
                if verbose:
                    print(e)
                continue
                    
            if verbose:
                end = time.time()
                print(f"Time taken: {end-start:.2f} s")
                print("Listening: END\n")
                print("-----------------")
            
            if not multi_lingual:
                voice_changed = changeVoice('Human:' + human_response, voice=voice_select)

            # fetch the string from objects.txt 
            with open('dependencies/vision/objects.txt', 'r') as file:
                objects = file.read()

            # fetch the string from vision.txt if vision is enabled
            if vision:
                with open('dependencies/vision/vision.txt', 'r') as file:
                    vision = file.read()
                prompt += [{"role": "user", "content": [{"type": "text", "text": human_response + '\n\n' + objects + '\n\n' "This is your own descripton of what you see with your eyes: " + vision}]}]
            else:
                prompt += [{"role": "user", "content": [{"type": "text", "text": human_response + '\n\n' + objects}]}]

            if voice_changed:
                # response = "Certainly! I will change my voice. Is it better now?"
                voice_prompt = prompt + [{"role": "system", "content": "You have changed your voice. Showcase the new voice and ask if the human likes it."}]
                response = getResponse(voice_prompt, temperature=temperature, max_tokens=max_tokens, top_p=top_p, openaiClient=openaiClient)
            else: 
                response = getResponse(prompt, temperature=temperature, max_tokens=max_tokens, top_p = top_p, openaiClient=openaiClient)

            # We should now generate some gestures for the robot
            
            
            conditional_say(response, "Pepper", IP, openaiClient=openaiClient, multi_lingual=multi_lingual, process_audio=process_audio)
            # elevenLabsSay(response, IP, multi_lingual=multi_lingual)
            print('Pepper: ' + response)
            if verbose:
                print("-----------------")

            prompt += [{"role": "assistant", "content": response}]
    return 0

def getParser():
     # initialize argparser 
    parser = argparse.ArgumentParser(description='Process some integers.')

    # write an argparser for all variables 
    parser.add_argument('--name', type=str, default='Human', help='name of the person you are talking to')
    parser.add_argument('--ip', type=str, default=None, help='IP address of the robot. (default: %(default)s)')
    parser.add_argument('--prompt', type=str, default="prompt.txt", help='Path to prompt to start the conversation')
    parser.add_argument('--temperature', type=float, default=0.7, help='temperature for the GPT model, float between 0 and 2')
    parser.add_argument('--max_tokens', type=int, default=300, help='max tokens for the GPT model')
    parser.add_argument('--top_p', type=float, default=1, help='top p for the GPT model')
    parser.add_argument('--language', type=str, default='da-DK', help='language for the GPT-3 model: en-US, en-GB, da-DK etc. see https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages for more.')
    parser.add_argument('--final_read', type=bool, default=False, help='if true the final text will be read out loud by the robot')
    parser.add_argument('--init_voice', type=int, default=2, help='NOTE, if -ml is not specified init voice containes the following, 0. Robot, 1. Rachel, 2. Ryan Kurk, 3. Pheobe, 4. Dave, 5. Mimi. Otherwise, it is an index in the dictonary of multi-lingual voices.')
    parser.add_argument('--device', type=str, default='cpu', help='The device to run the od on.')
    parser.add_argument('-od', '--object_detection', action='store_true', help='if true the object detection will be run')
    parser.add_argument('--camera', type=int, default=0, help='Camera index to use for object detection')
    parser.add_argument('-v', '--verbose', action='store_true', help='increase output verbosity')
    parser.add_argument('-ml', '--multi_lingual', action='store_true', help='use the multi-lingual model')
    parser.add_argument('--vision', action='store_true', help='Enable vision model to analyze the image')
    parser.add_argument('-vf', '--visionfreq', type=int, default=5, help='Time betwee frame captures for the OpenAI vision model')
    parser.add_argument('-pa', '--process_audio', action='store_true', help='Process the audio to sound more robotic.')
    # parse the arguments
    args = parser.parse_args()

    
    # get prompt from file 
    with open(args.prompt, 'r') as file:
        prompt = file.read()
        
    # let us create the two text files vision.txt and objects.txt if they do not already exist
    if args.vision:
        if not os.path.exists('dependencies/vision/vision.txt'):
            with open('dependencies/vision/vision.txt', 'w') as file:
                file.write("This is what you see through your robot eyes:\n\n Nothing")
        if not os.path.exists('dependencies/vision/objects.txt'):
            with open('dependencies/vision/objects.txt', 'w') as file:
                file.write("No objects detected")
        
    # get the variables from the arguments
    name = args.name
    temperature = args.temperature
    max_tokens = args.max_tokens
    top_p = args.top_p
    language = args.language
    final_read = args.final_read
    global voice_select
    voice_select = args.init_voice
    global verbose
    verbose = args.verbose
    device = args.device
    vision = args.vision
    multi_lingual = args.multi_lingual
    vision_freq = args.visionfreq
    process_audio = args.process_audio
    camera = args.camera
    
    # if not multi-lingual, we need to make sure that init_voice is within the correct range
    if not multi_lingual:
        assert voice_select in eng_voices.keys(), "The voice you have selected is not available. Please select a voice from the following list: 0. Robot, 1. Rachel, 2. Ryan Kurk, 3. Pheobe, 4. Dave, 5. Mimi."
    
    if language != 'en-UK' or language != 'en-US':
        multi_lingual = True
        
    if args.object_detection:
        if args.verbose:
            print("Running object detection")
        
        # We need to run the object detection in a separate thread to avoid blocking the main thread
        run_yolo_in_subprocess(verbose, device, vision, vision_freq, camera)   
    IP = args.ip

    return IP, name, prompt, temperature, max_tokens, top_p, language, final_read, multi_lingual, vision, process_audio

if __name__ == "__main__":
    # get the arguments
    IP, name, prompt, temperature, max_tokens, top_p, language, final_read, multi_lingual, vision, process_audio = getParser()
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
        name, pepper_response = getName(main_prompt=prompt, temperature=temperature, openaiClient=openaiClient, language=language, IP=IP, multi_lingual=multi_lingual, process_audio=process_audio)
        prompt = [{"role": "system", "content": prompt}, {"role": "assistant", "content": [{"type": "text", "text": pepper_response}]}]
    else:
        
        prompt = [{"role": "system", "content": prompt + '\n\n' + 'The person you are talking to is called, ' + name}, {"role": "assistant", "content": [{"type": "text", "text": ""}]}]

    startConversation(prompt, name, temperature=temperature, max_tokens=max_tokens, top_p=top_p, language=language, openaiClient=openaiClient, IP=IP, multi_lingual=multi_lingual, vision=vision, process_audio=process_audio)
    print("Successfully exited...")
