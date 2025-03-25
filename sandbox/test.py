import whisper
import sounddevice as sd
import numpy as np
import keyboard
from scipy.io.wavfile import write

model = whisper.load_model("tiny")

def record_audio(filename="recording.wav", sample_rate=44100):
    print("Press space to start recording...")
    
    # Wait until the spacebar is pressed to start recording
    keyboard.wait("space")
    print("Recording started! Press space again to stop.")
    
    # Buffer to store the recorded audio
    audio_buffer = []

    def callback(indata, frames, time, status):
        # Add incoming audio data to the buffer
        audio_buffer.append(indata.copy())

    # Start the input stream
    with sd.InputStream(samplerate=sample_rate, channels=1, callback=callback):
        # Record until space is pressed again
        while not keyboard.is_pressed("space"):
            pass

    print("Recording stopped.")
    
    # Convert the buffer list to a numpy array
    audio_data = np.concatenate(audio_buffer, axis=0)
    write(filename, sample_rate, audio_data)
    print(f"Recording saved as {filename}")

# Run the recording function
record_audio()

print("Running speech-to-text...")
#record some audio
#whisper.record("audio.mp3", 5)

#transcribe the audio
result = model.transcribe("recording.wav")
print(result["text"])