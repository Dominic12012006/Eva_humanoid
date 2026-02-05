from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
import os
from .app import summarize
load_dotenv()

elevenlabs = ElevenLabs(
    api_key="sk_2aa9be07efeac959f8db7e770c899a1c34019716fa0695ce"
)

def speak(content):
    audio = elevenlabs.text_to_speech.convert(
        text=summarize(content),
        voice_id="1qEiC6qsybMkmnNdVMbK",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    print("fdv")

    play(audio)

