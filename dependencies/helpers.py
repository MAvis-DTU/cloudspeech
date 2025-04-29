from __init__ import *
import threading
import subprocess
import time
from threading import Thread
from elevenlabs import stream
from elevenlabs.client import ElevenLabs
import yaml
import os
import re
from google.cloud import speech
# from dependencies.robot.nao_functions import NaoServices

def _init_elevenlabs(cloudspeech_config):
    if cloudspeech_config["elevenlabs"]["use_elevenlabs"]:
        elevenlabs_api_key = os.getenv("elevenlabs_key")
        # based on the settings, choose the right language model for the elevenlabs API
        if cloudspeech_config["elevenlabs"]["init_language"] in ['en-UK', 'en-US'] and not cloudspeech_config["elevenlabs"]["multi_lingual"]:
            model_id = cloudspeech_config["elevenlabs"]["english_only_model_id"]
        else:
            model_id = cloudspeech_config["elevenlabs"]["multi_lingual_model_id"]
        
        # get the voice dictionary from the configuration file
        voice_dict = cloudspeech_config["elevenlabs"]["voices"]
        # initialize the elevenlabs API with the API key, model id and voice ids
        elevenlabsStream = ElevenLabsStream(api_key=elevenlabs_api_key, 
                                            model_id=model_id, 
                                            voice_dict=voice_dict, 
                                            default_language=cloudspeech_config["elevenlabs"]["init_language"], 
                                            use_robot=cloudspeech_config["robot"]["use_robot"],
                                            process_audio=cloudspeech_config["general"]["robotic_voice"],
                                            multi_lingual=cloudspeech_config["elevenlabs"]["multi_lingual"],
                                            init_voice=cloudspeech_config["elevenlabs"]["init_voice"],
                                            enable_voice_change=cloudspeech_config["elevenlabs"]["enable_voice_change"])
    else:
        elevenlabsStream = None
    
    return elevenlabsStream

def _init_yolo_object_detection(cloudspeech_config, args):
    if cloudspeech_config["general"]["object_detection"]:
        # initialize the vision and object detection files if they do not exist and reset them if they do
        _initialize_vision_files(cloudspeech_config)  
        
        if args.verbose:
            print("Running object detection")
            
        # We need to run the object detection in a separate thread to avoid blocking the main thread
        run_yolo_in_subprocess(args.verbose, 
                               args.device, 
                               cloudspeech_config["openai_gpt"]["enable_vision"], 
                               cloudspeech_config["openai_gpt"]["vision_frequency"], 
                               cloudspeech_config["general"]["camera_device_index"])   

def _init_robot(cloudspeech_config):
    if cloudspeech_config["robot"]["use_robot"]:
        ip = cloudspeech_config["robot"]["ip"]
        port = cloudspeech_config["robot"]["port"]
        NAO_IP = f"tcp://{ip}:{port}"
        naoServices = NaoServices(NAO_IP)
        naoServices.nao_init()
        naoServices.nao_facetrack()
    else:
        naoServices = None
    return naoServices

def _run_pepper_idling(naoServices, time_between_behaviors):
    if naoServices is not None:
        naoServices.nao_idle(time_between_behaviors=time_between_behaviors)
        try:
            while True:
                pass
        except KeyboardInterrupt:
            naoServices.nao_idle_terminate()
            sys.exit(0)
    else:
        print("Robot is not enabled. Please enable the robot in the configuration file to run the idle mode.")
        sys.exit(0)
        
        
def _retrieve_config(path='cloudspeech_config.yaml'):
    # load configuration yaml file as a dictionary
    with open(path) as file:
        cloudspeech_config = yaml.load(file, Loader=yaml.FullLoader)    
    return cloudspeech_config

def _retrieve_prompt_from_file(cloudspeech_config):
    with open(cloudspeech_config["general"]["main_prompt_path"], 'r') as file:
        main_prompt = file.read()
    return main_prompt

def _initialize_vision_files(cloudspeech_config):
    # let us create the two text files vision.txt and objects.txt if they do not already exist
    if cloudspeech_config["openai_gpt"]["enable_vision"]:
        with open('dependencies/vision/vision.txt', 'w') as file:
            file.write("This is what you see through your robot eyes:\n\n Nothing")
        with open('dependencies/vision/objects.txt', 'w') as file:
            file.write("No objects detected")
 
def run_yolo_in_subprocess(verbose, device, vision, vision_freq, camera):
    # Path to the yolo_detection.py script
    script_path = "models/objectYolo.py"

    # Build the command with arguments to pass to the subprocess
    if vision: 
        command = [
            "python",  # or "python3" depending on your environment
            script_path,  # The script you want to run
            "--verbose", str(verbose),
            "--vision",
            "--device", device,
            "--vision_freq", str(vision_freq),
            "--camera", str(camera)
        ]
    else:
        command = [
            "python",  # or "python3" depending on your environment
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

def getResponse(prompt: list, 
                temperature: float, 
                max_tokens: int, 
                top_p: float, 
                openaiClient, 
                frequency_penalty: float =1.75, 
                presence_penalty: float = 1.75, 
                model: str ="gpt-4o", 
                verbose=False,
                response_type="default"):
    if verbose:
        print("-----------------")
        print(f"Get Response ({response_type}): START")
        start = time.time()
    response = openaiClient.chat.completions.create(
                model=model,
                messages=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
            )
    if verbose:
        end = time.time()
        print(f"Time taken: {end-start:.2f} s", file=sys.stderr)
        print(f"Get Response ({response_type}): END")
        print("-----------------")

    return response.choices[0].message.content

def get_gestures(text, openaiClient, verbose=False):

    # Few shot prompting for gestures
    # It was found that it improved the output of the models and also increasing the prompting speed.
    prompt = [
        {
        "role": "system",
        "content": "Given a paragraph of text, annotate every 10 words in that paragraph with the most appropriate tag. You should always give a tag no matter what. The tags are to be placed in square brackets. \n\nFollowing tags are available:\n0. Happy\n1. Sad\n2. Affirmative\n3. Unfamiliar\n4. Thinking\n5. Explain\n\nIt should be on the form:\n\nHi, [5] have you heard about the recent news? They are [1] quite horrific to say the least."
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
        "content": [{"type": "text", "text": "I don't understand what you [1] mean. Let me just think about [4] it."}]
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

def changeVoice(prompt, openaiClient, elevenlabsStream, verbose, model):
    voice_prompt = [
                    {
                    "role": "user",
                    "content": [{"type":"text", "text":f"You have the following voices to chose from. They have a name and a description: {elevenlabsStream.voice_descriptions}. Below you will get a sentence said by a human. Your current voice is {elevenlabsStream.voice_select}. If the human explicitly requests for you to change your voice, write the ID that best matches the request: (ID), otherwise write: -nothing. Note that it is only if the human asks about another voice, not if the human simply mentions the name of the voice.\\n\\n',\n\n{prompt}\n"
                                }
                                ]
                    }
                    ]
    if verbose:
        print("Change Voice: START")
        start = time.time()
    response = getResponse(voice_prompt, temperature=1, max_tokens=256, top_p=1, openaiClient=openaiClient, frequency_penalty=0, presence_penalty=0, model=model)
    if verbose:
        print(f"{response} (current: {elevenlabsStream.voice_select})")
        end = time.time()
        print(f"Time taken: {end-start:.2f} s", file=sys.stderr)
        print("Change Voice: END")
    try:
        if elevenlabsStream.voice_select != response and response != "-nothing":
            if int(response) in elevenlabsStream.voice_idx_to_id:
                elevenlabsStream.voice_select = int(response)
                return 1
            else:
                return 0
        else:
            return 0
    except ValueError as e:
        if verbose:
            print(f"ValueError: {e}")
        return 0

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

class ElevenLabsStream:
    def __init__(self, api_key, voice_dict, model_id, default_language, use_robot, process_audio, multi_lingual, init_voice, enable_voice_change):
        self.client_elevenlabs = ElevenLabs(api_key=api_key)
        self.model_id = model_id
        
        # Variables stored to contain information about the voices and the selected voice
        self.voice_dict = voice_dict
        self.voice_id_to_idx = {voice_dict[key]['id']: key for key in voice_dict.keys()}
        self.voice_idx_to_id = {}
        self.voice_descriptions = self._get_voice_descriptions(use_robot)
        self.voice_select = init_voice
        self.enable_voice_change = enable_voice_change

        # Variables to store information about the language
        self.multi_lingual = multi_lingual
        self.default_language = default_language
        self.process_audio = process_audio

    def _get_voice_descriptions(self, use_robot):
        all_voices = self.client_elevenlabs.voices.get_all().voices
        voice_ids = self.voice_id_to_idx.keys()
        sorted_voice_ids = [voice for voice in all_voices if voice.voice_id in voice_ids]
        
        self.voice_idx_to_id = {}
        voice_descriptions = {}
        for voice in sorted_voice_ids:
            self.voice_idx_to_id[self.voice_id_to_idx[voice.voice_id]] = voice.voice_id
            saved_voice_description = self.voice_dict[self.voice_id_to_idx[voice.voice_id]]['description']
            if saved_voice_description is None:
                voice_descriptions[self.voice_id_to_idx[voice.voice_id]] = voice.description
            else:
                voice_descriptions[self.voice_id_to_idx[voice.voice_id]] = saved_voice_description
                
        if use_robot:
            self.voice_idx_to_id[0] = "Pepper"
            voice_descriptions[0] = "Pepper's own robot voice."
        return voice_descriptions
        
    def _generate_stream(self, text):
        return self.client_elevenlabs.text_to_speech.convert_as_stream(text=text, 
                                                                       voice_id=self.voice_idx_to_id[self.voice_select], 
                                                                       model_id=self.model_id)

    def _play_stream(self, result):
        stream(result)

class GestureThread(Thread):
    def __init__(self, naoServices, split_sentences, gesture_numbers):
        Thread.__init__(self)
        self.naoServices = naoServices
        self.split_sentences = split_sentences
        self.gesture_numbers = gesture_numbers
        self.p = None
    
    def run(self):
        self.naoServices.nao_gestures(self.gesture_numbers)

    def terminate(self):
        self.naoServices.nao_stop_behavior()
   
class AudioGestureGeneratorThread:
    def __init__(self, 
                 verbose,
                 text,
                 openaiClient,
                 elevenlabsStream):
        """
        Initialize the class with two functions and their respective arguments.

        Parameters:
            func1_args (tuple): Arguments for audio as a tuple.
            func2_args (tuple): Arguments for gesture as a tuple.
        """
        self.verbose = verbose
        self.text = text
        self.openaiClient = openaiClient
        self.elevenlabsStream = elevenlabsStream
        self.result1 = None
        self.result2 = None
        self.end1 = None
        self.end2 = None

    def _run_audio(self):
        # Run func1 with its arguments and store the result
        # TODO Look into text_to_speech.convert_as_stream() which returns an audio stream.
        # https://api.elevenlabs.io/v1/text-to-speech/:voice_id/stream
        result = self.elevenlabsStream._generate_stream(self.text)
        if self.elevenlabsStream.process_audio:
            # TODO: Alter audio sound to be more robotic but it has to run in tandem with the audio generation
            # Alter audio sound to be more robotic
            # result = change_pitch(self.result1, pitch_shift_steps=2)
            ...
        self.result1 = result
        self.end1 = time.time()
        
    def _run_gesture(self):
        # Run func2 with its arguments and store the result
        self.result2 = get_gestures(text=self.text, openaiClient=self.openaiClient, verbose=self.verbose)
        self.end2 = time.time()

    def run(self):
        if self.verbose:
            print("Audio and Gesture generation: START")
            start = time.time()
        # Create two threads, one for each function
        thread1 = threading.Thread(target=self._run_audio)
        thread2 = threading.Thread(target=self._run_gesture)

        # Start both threads
        thread1.start()
        thread2.start()

        # Wait for both threads to finish
        thread1.join()
        thread2.join()
        if self.verbose:
            end = time.time()
            print(f"Audio time:       {self.end1-start:.2f} s\n"
                  f"Gesture Time:     {self.end2-start:.2f} s\n"
                  f"Bottleneck Time:  {end-start:.2f} s")
            print("Audio and Gesture generation: END")
        # Return the results of both functions
        return self.result1, self.result2


class SubprocessHandler:
    def __init__(self, main_command, cleanup_command, IP, time_between_behaviors=60):
        self.main_command = main_command
        self.cleanup_command = cleanup_command
        self.process = None
        self.IP = IP
        self.time_between_behaviors = time_between_behaviors

    def run_main(self):
        self.process = subprocess.Popen(self.main_command, shell=True, stdin=subprocess.PIPE)
        self.process.communicate(input=bytes(self.IP + '\n' + str(self.time_between_behaviors), encoding="utf-8"))

    def cleanup(self):
        print("Running cleanup subprocess...")
        subprocess.run(self.cleanup_command, shell=True, input=bytes(self.IP, encoding="utf-8"))
        if self.process:
            self.process.terminate()

    def __enter__(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def signal_handler(self, sig, frame):
        self.cleanup()
        sys.exit(0)