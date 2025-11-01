from dotenv import load_dotenv
import os
from elevenlabs.client import ElevenLabs
import io
load_dotenv()

elevenlabs = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
)

def audio_to_text1(audio_path):
    try:
        with open(audio_path, "rb") as f:
            transcription = elevenlabs.speech_to_text.convert(
                file=f,
                model_id="scribe_v1",
                tag_audio_events=False,
                diarize=False
            )
        return transcription.text
    except Exception as e:
        print("Error transcribing audio:", e)
        return None


def audio_to_text(audio_data):
    try:
        # Convert recorded audio to BytesIO
        audio_file = io.BytesIO(audio_data.get_wav_data())

        # Call ElevenLabs speech-to-text
        transcription = elevenlabs.speech_to_text.convert(
            file=audio_file,
            model_id="scribe_v1",      # ElevenLabs transcription model
            tag_audio_events=False,    # optional: True if you want events
            # language_code="eng",
            diarize=False              # optional: True if multiple speakers
        )

        return transcription.text
    except Exception as e:
        print("Error transcribing audio:", e)
        return None