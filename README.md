### README.md for cloudspeech.py

#### Introduction
`cloudspeech.py` is a Python script utilizing Google Cloud Speech-to-Text, OpenAI's GPT models, and ElevenLabs' voice synthesis for interactive voice-enabled applications with a Softbanks Robotics Pepper Robot. This script incorporates functionality to interface with Pepper, execute voice streaming with real-time response using AI models, and perform object detection leveraging MediaPipe (provided MediaPipe is configured in the environment).

#### Prerequisites
1. **Python 3.x** and **Python 2.7.18** with the PythonSDK from Naoqi in your PYTHONPATH. **Python 3.x** handles AI models and **Python 2.7.18x** uses the Pepper Python SDK to send commands to the robot. 
2. **PyAudio** library, which can be installed using pip:
    ```bash
    pip install pyaudio
    ```
3. **Google Cloud Speech-to-Text API** credentials:
   - Right now, the API keys are in the code. But will be changed such that you should: Obtain your credentials JSON file from Google Cloud and place it in the project directory.
   - Set an environment variable pointing to this file:
     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS='path_to_your_credentials.json'
     ```
4. **OpenAI API key**:
   - Right now, the API keys are in the code. But will be changed such that you should: Set an environment variable for the OpenAI API key:
     ```bash
     export OPENAI_API_KEY='your_openai_api_key'
     ```
5. **ElevenLabs API key**:
   - Right now, the API keys are in the code. But will be changed such that you should: Set an environment variable for the ElevenLabs API key:
     ```bash
     export ELEVENLABS_API_KEY='your_elevenlabs_api_key'
     ```
6. **NAO Robot SDK**:
   - Ensure the NAO robot's IP is correctly set in the `robot/nao_*.py` files. If you don't remember your robot's IP, press the button behind the tablet on Pepper's body. 
7. **MediaPipe** (optional for object detection - harder to setup):
   - Set up MediaPipe according to your environment requirements and ensure it is functional prior to embedding this functionality within the script.

#### Usage
To run `cloudspeech.py`, navigate to the directory containing the script and use the following command:
```bash
python3 cloudspeech.py [arguments]
```

#### Arguments
You can customize the behavior of the script by passing the following arguments:
- `--name`: Name of the person to converse with (default "Human").
- `--ip`: The IP address to the Pepper robot that you wish to connect to. (**NOTE** Default is `None`).
- `--prompt`: Path to the initial prompt for starting the conversation (default path is `prompt.txt`).
- `--temperature`: Temperature for GPT model inference (a float between 0 and 2, default 0.7).
- `--max_tokens`: Maximum number of tokens for GPT model inference (default 300).
- `--top_p`: Top probability for GPT model token selection (default 1).
- `--language`: Language code for speech recognition (e.g., "en-US", "en-GB"), default "da-DK".
- `--final_read`: Boolean to decide if the final message should be read aloud by the robot (default False).
- `--init_voice`: the initial voice used (either Pepper or elevenlab voices)
- `--device`: The device (`cpu`, `cuda` or `mps`) yolo detection is run with.
- `-od` or `-object_detection`: If specified it will run with object detection and start a video-stream.
- `--camera`: The index of the camera used for object-detection.
- `-v` or `-verbose`: If specified prints verbose statements for each step in the process.
- `-ml` or `-multi_lingual`: Whether to use multi-lingual elevenlabs model
- `--vision`: Specify if vision-model (o-model) should be used to describe the environment.
- `-vf` or `-visionfreq`: The frequency (time between) of which the GPT O-model is queried by.
- `-pa` or `--process_audio`: Whether to apply post-processing on the audio generated from ElevenLabs.
- `--idle`: Whether to run the idle configuration of the robot.
- `--time_between_behaviors`: The time between randomly executed gestures in seconds.


**NOTE** There is an idle function included into the cloudspeech script. To run it execut the following command in your CLI, `python cloudspeech.py --idle` and then you can add the optional setting `--time_between_behaviors` which represents the time between each gesture performed in seconds (takes an integer number).

**NOTE** when the language is set different from "en-US" or "en-UK", multi_lingual is automatically set to True no matter if it has been specified otherwise in the CLI. 

**NOTE** it is not possible to change voice while `running` with `-ml`. It is however possible to change the used voice with `-ml` by specifying a different `--init_voice` index.

#### Example Command
```bash
python3 cloudspeech.py -v -od -ml --device mps --vision --visionfreq 5 --camera 0 --init_voice 7 --name Thomas --ip 192.168.1.152
```
The command runs cloudspeech with object-detection updating the vision description for every 5 seconds. It uses the multilingual TTS model from elevenlabs with voice 7. If skips the getName part of the conversation as the name is specified. It also runs with the robot since a specific IP is given in the CLI.

#### Object Detection Note
Object detection functionality requires a correctly set up environment that supports the use of Ultralyics. Make sure that if on MacOS you are able to run with --device mps if a GPU is available.

Hopefully, this README helps provide clarity on how to utilize and configure `cloudspeech.py` effectively for various interactive voice applications.


#### More info
- When installing portaudio and pyaduio, you might get a name_space warning. You can install sounddevice using pip install sounddevice and then importing sounddevice immediately before importin pyaudio for a quick fix (found here: https://github.com/OpenInterpreter/01/issues/68)

- Also, for MPS to work in yolo make sure to run export PYTORCH_ENABLE_MPS_FALLBACK=1 for a temporary fallback to cpu for any functions not implemented for the silicon processor. To make the fallback permanent and global add the line to your '.zshrc' found in 'users/user' (the file is hidden by default, but you can reveal hidden files in the finder by pressing 'cmd+shift+.').

- The quickets way to share an conda env between group members is by using .yml files that can be sent and created locally by 'conda env create -f environment.yml -n name_for_env'. Remember to check that dependencies are working before sending an .yml file to a friend since these can cause headaches. Anecdote: Mediapipe and Google-cloud-speech will both try to create non-compatible versions of the protobuf library (if both are not completely up to date).
- 
