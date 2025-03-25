import os

# Set the environment variable for the Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'credentials/keep/google_key.json'

# Set the environment variable for the OpenAI API key
with open('credentials/keep/openai_key.txt', 'r') as f:
    os.environ['gpt4key'] = f.read()
    
# Set the environment variable for the Elevenlabs API key
with open('credentials/keep/elevenlabs_key.txt', 'r') as f:
    os.environ['elevenlabs_key'] = f.read()