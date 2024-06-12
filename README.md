### README.md for cloudspeech.py
# TODO
- [X] Fix IP input to nao scripts
- [X] Create verbose option
- [ ] Test nao scripts on robot
- [ ] Configure better object-detection with a new model (look into YOLO for macos).

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
- `--prompt`: Initial prompt for starting the conversation (default is read from `prompt.txt`).
- `--temperature`: Temperature for GPT model inference (a float between 0 and 2, default 0.7).
- `--max_tokens`: Maximum number of tokens for GPT model inference (default 300).
- `--top_p`: Top probability for GPT model token selection (default 1).
- `--language`: Language code for speech recognition (e.g., "en-US", "en-GB"), default "en-US".
- `--final_read`: Boolean to decide if the final message should be read aloud by the robot (default False).

#### Example Command
```bash
python3 cloudspeech.py --temperature 0.9 --final_read True
```

#### Object Detection Note
Object detection functionality requires a correctly set up MediaPipe environment. Ensure that MediaPipe is configured before enabling object detection in this script.

Hopefully, this README helps provide clarity on how to utilize and configure `cloudspeech.py` effectively for various interactive voice applications.
