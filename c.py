# example_local.py
import os
from dotenv import load_dotenv
from io import BytesIO
from elevenlabs.client import ElevenLabs

load_dotenv()

elevenlabs = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
)

# -------------------------
# Use a local WAV file
# -------------------------
wav_path = r"/home/eva/Desktop/dominic/gemini_output.mp3"  # replace with your file path
with open(wav_path, "rb") as f:
    audio_data = BytesIO(f.read())

transcription = elevenlabs.speech_to_text.convert(
    file=audio_data,
    model_id="scribe_v1",  # Only "scribe_v1" supported for now
    tag_audio_events=True,  # Tag events like laughter, applause
    diarize=True             # Annotate who is speaking
)

print(transcription.text)
