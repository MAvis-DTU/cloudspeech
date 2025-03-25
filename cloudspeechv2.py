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
from __future__ import division
from __init__ import *

# Library imports
import re
import signal
import openai
import os
import time
import argparse
import sys
import subprocess
import io
import librosa
import yaml
import threading
import soundfile as sf
from flask import g
from sympy import N, Q
from torch import ge
from threading import Thread
from pydub import AudioSegment

# from elevenlabs import voices, play
# from elevenlabs import set_api_key
from elevenlabs.client import ElevenLabs

from concurrent.futures import thread, ThreadPoolExecutor
from google.cloud import speech

# File imports 
from googlestream import *
from dependencies.helpers import _retrieve_config, _retrieve_main_prompt, _initialize_vision_files, _init_robot, _init_elevenlabs, _init_yolo_object_detection, _run_pepper_idling, run_yolo_in_subprocess
from dependencies.helpers import ElevenLabsStream
from dependencies.conversation import startConversation, getName
# from dependencies.robot.nao_functions import NaoServices
from credentials.set_environment_keys import *

# Get the API key from the environment
openai_api_key = os.getenv("gpt4key")
elevenlabs_api_key = os.getenv("elevenlabs_key")
google_api_key = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

def _start_conversation(args, cloudspeech_config, prompt, nao_services, elevenlabsStream):
    openaiClient = openai.OpenAI(api_key=openai_api_key)
    
    # get the name of the human if not specified using argument parser
    if args.name == 'Human':
        name, pepper_response = getName(main_prompt=prompt,
                                        temperature=cloudspeech_config["openai_gpt"]["temperature"], 
                                        openaiClient=openaiClient,
                                        naoServices=naoServices,
                                        elevenlabsStream=elevenlabsStream,
                                        max_tokens=cloudspeech_config["openai_gpt"]["max_tokens"],
                                        top_p=cloudspeech_config["openai_gpt"]["top_p"],
                                        language=cloudspeech_config["elevenlabs"]["init_language"],
                                        verbose=args.verbose,
                                        gpt_model=cloudspeech_config["openai_gpt"]["model"])
        
        prompt = [{"role": "system", "content": prompt}, {"role": "assistant", "content": [{"type": "text", "text": pepper_response}]}]
    else:
        prompt = [{"role": "system", "content": prompt + '\n\n' + 'The person you are talking to is called, ' + args.name}, {"role": "assistant", "content": [{"type": "text", "text": ""}]}]

    startConversation(prompt=prompt, 
                      speaker=args.name, 
                      temperature=cloudspeech_config["openai_gpt"]["temperature"], 
                      max_tokens=cloudspeech_config["openai_gpt"]["max_tokens"], 
                      top_p=cloudspeech_config["openai_gpt"]["top_p"], 
                      openaiClient=openaiClient,
                      naoServices=naoServices,
                      elevenlabsStream=elevenlabsStream,
                      language=cloudspeech_config["elevenlabs"]["init_language"], 
                      vision=cloudspeech_config["openai_gpt"]["enable_vision"],
                      gpt_model=cloudspeech_config["openai_gpt"]["model"], 
                      verbose=args.verbose)
    print("Successfully exited...")
    
def getParser():
     # initialize argparser 
    parser = argparse.ArgumentParser(description='Process some integers.')
    # write an argparser for all variables 
    parser.add_argument('--name', type=str, default='Human', help='name of the person you are talking to')
    parser.add_argument('--final_read', type=bool, default=False, help='if true the final text will be read out loud by the robot')
    parser.add_argument('--device', type=str, default='cpu', help='The device to run the od on.')
    parser.add_argument('-v', '--verbose', action='store_true', help='increase output verbosity')
    parser.add_argument('--idle', action='store_true', help='Run the robot in idle mode')
    parser.add_argument('--time_between_behaviors', type=int, default=60, help='Time between gestures during idle mode. (in seconds)')
    # parse the arguments
    return parser.parse_args()

def _get_setup():
    # get the arguments
    # IP, name, prompt, temperature, max_tokens, top_p, language, final_read, multi_lingual, vision, process_audio, idle, time_between_behaviors = getParser()
    args = getParser()
    
    # load configuration yaml file as a dictionary
    cloudspeech_config = _retrieve_config(path='cloudspeech_config.yaml')
    
    # get prompt from file 
    prompt = _retrieve_main_prompt(cloudspeech_config)

    # initialize the vision and object detection files if they do not exist and reset them if they do
    _initialize_vision_files(cloudspeech_config)
            
    return args, cloudspeech_config, prompt

if __name__ == "__main__":
    # get the arguments, configuration and prompt
    args, cloudspeech_config, prompt = _get_setup()

    # initialize the elevenlabs API
    elevenlabsStream = _init_elevenlabs(cloudspeech_config)
    
    # initialize the object detection
    _init_yolo_object_detection(cloudspeech_config, args)
    
    # initialize the robot
    naoServices = _init_robot(cloudspeech_config)
    
    # if idle arument is specified we run the nao_idle function
    if args.idle:
        _run_pepper_idling(naoServices, args.time_between_behaviors)
    else: # otherwise we run the conversation
        _start_conversation(args, cloudspeech_config, prompt, naoServices, elevenlabsStream)
