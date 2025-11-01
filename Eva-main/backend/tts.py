from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
import os
from .app import summarize
load_dotenv()

elevenlabs = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
)

def speak(content):
    audio = elevenlabs.text_to_speech.convert(
        text=summarize(content),
        voice_id="1qEiC6qsybMkmnNdVMbK",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )

    play(audio)

