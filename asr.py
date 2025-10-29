import re
import io
from groq import Groq
from dotenv import load_dotenv
import os
load_dotenv()

# Initialize Groq API client
groq_client = Groq(os.getenv("groq_api"))

def audio_to_text(audio_data):
    """Convert recorded audio to text using Groq's Whisper model."""
    try:
        audio_file = io.BytesIO(audio_data.get_wav_data())
        translation = groq_client.audio.translations.create(
            file=("audio.wav", audio_file.getvalue()),
            model="whisper-large-v3",
        )
        return translation.text
    except Exception as e:
        print("Error transcribing audio:", e)
        return None

def extract_prompt(transcribed_text, wake_word):
    """Extracts the prompt after the wake word (e.g., 'Teacher, tell me a joke')."""
    pattern = rf'\b{re.escape(wake_word)}[\s,.?!]*(.*)'
    match = re.search(pattern, transcribed_text, re.IGNORECASE)
    return match.group(1).strip() if match else None
