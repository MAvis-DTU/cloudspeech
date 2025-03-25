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
import openai
import os
import argparse

# File imports 
from googlestream import *
from dependencies.helpers import _retrieve_config, _retrieve_prompt_from_file, _init_robot, _init_elevenlabs, _init_yolo_object_detection, _run_pepper_idling
from dependencies.conversation import startConversation, getName
from credentials.set_environment_keys import *

# Get the API key from the environment
openai_api_key = os.getenv("gpt4key")
elevenlabs_api_key = os.getenv("elevenlabs_key")
google_api_key = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

def _start_conversation(args, cloudspeech_config, prompt, naoServices, elevenlabsStream):
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

def _get_args_and_config_setup():
    # get the arguments
    args = getParser()
    
    # load configuration yaml file as a dictionary
    cloudspeech_config = _retrieve_config(path=args.config_path)

    return args, cloudspeech_config

def getParser():
     # initialize argparser 
    parser = argparse.ArgumentParser(description='Process some integers.')
    # write an argparser for all variables 
    parser.add_argument('--name', type=str, default='Human', help='name of the person you are talking to')
    parser.add_argument('--final_read', type=bool, default=False, help='if true the final text will be read out loud by the robot')
    parser.add_argument('--device', type=str, default='cpu', help='The device to run the object-detection on. possible are, cuda, cpu and mps for macos.')
    parser.add_argument('-v', '--verbose', action='store_true', help='increase output verbosity')
    parser.add_argument('--idle', action='store_true', help='Run the robot in idle mode')
    parser.add_argument('--time_between_behaviors', type=int, default=60, help='Time between gestures during idle mode. (in seconds)')
    parser.add_argument('--config_path', type=str, default='cloudspeech_config.yaml', help='Path to the configuration file')
    # parse the arguments
    return parser.parse_args()


if __name__ == "__main__":
    # get the arguments, configuration and prompt
    args, cloudspeech_config = _get_args_and_config_setup()

    # initialize the elevenlabs API
    elevenlabsStream = _init_elevenlabs(cloudspeech_config)
    
    # initialize the robot
    naoServices = _init_robot(cloudspeech_config)
    
    if args.idle:
        # if idle arument is specified we run the nao_idle function
        _run_pepper_idling(naoServices, args.time_between_behaviors)
    elif args.final_read: 
        # TODO: Implement the final read out loud function here. Generate gestures, and read out loud the final text together with the gestures.
        ...
    else:  # otherwise we run the conversation
        # initialize the object detection and vision files
        _init_yolo_object_detection(cloudspeech_config, args)
        
        # get prompt from file 
        initial_prompt = _retrieve_prompt_from_file(cloudspeech_config)
        
        # start the conversation
        _start_conversation(args, cloudspeech_config, initial_prompt, naoServices, elevenlabsStream)
