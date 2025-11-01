from dotenv import load_dotenv
import os
from elevenlabs.client import ElevenLabs
import io
from pydub import AudioSegment
import speech_recognition as sr
import tempfile
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


def audio_to_text(audio_data,code):
    try:
        # Convert recorded audio to BytesIO
        audio_file = io.BytesIO(audio_data.get_wav_data())

        # Call ElevenLabs speech-to-text
        transcription = elevenlabs.speech_to_text.convert(
            file=audio_file,
            model_id="scribe_v1",      # ElevenLabs transcription model
            tag_audio_events=False,    # optional: True if you want events
            language_code=code,
            diarize=False              # optional: True if multiple speakers
        )

        return transcription.text
    except Exception as e:
        print("Error transcribing audio:", e)
        return None
def audio_to_text_button(audio_data,code):
    try:
        # Convert recorded audio to BytesIO
        audio_file = io.BytesIO(audio_data)

        # Call ElevenLabs speech-to-text
        transcription = elevenlabs.speech_to_text.convert(
            file=audio_file,
            model_id="scribe_v1",      # ElevenLabs transcription model
            tag_audio_events=False,    # optional: True if you want events
            language_code=code,
            diarize=False              # optional: True if multiple speakers
        )

        return transcription.text
    except Exception as e:
        print("Error transcribing audio:", e)
        return None



def extract_post_wake_audio(audio_data, wake_word="eva"):
    """
    Extracts the portion of audio that comes *after* the wake word.
    Uses ElevenLabs transcription for wake word detection.
    Input : speech_recognition.AudioData
    Output: speech_recognition.AudioData (trimmed)
    """
    recognizer = sr.Recognizer()  # only for final conversion back
    wav_bytes = audio_data.get_wav_data()
    audio_segment = AudioSegment.from_file(io.BytesIO(wav_bytes), format="wav")

    chunk_ms = 800
    chunks = [audio_segment[i:i + chunk_ms] for i in range(0, len(audio_segment), chunk_ms)]
    wake_index = None

    print(f"[extract_post_wake_audio] Detecting '{wake_word}' using ElevenLabs STT...")

    for i, chunk in enumerate(chunks):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            chunk.export(f.name, format="wav")
            try:
                with open(f.name, "rb") as audio_file:
                    transcription = elevenlabs.speech_to_text.convert(
                        file=audio_file,
                        model_id="scribe_v1",
                        tag_audio_events=False,
                        language_code='en',
                        diarize=False
                    )
                text = transcription.text.lower().strip()
                print(f"Chunk {i}: {text}")  # Debug log
                if wake_word in text:
                    print(f"✅ Wake word '{wake_word}' found in chunk {i}")
                    wake_index = i
                    break
            except Exception as e:
                print(f"[extract_post_wake_audio] ElevenLabs STT error in chunk {i}: {e}")
            finally:
                os.remove(f.name)

    # --- If found: return audio after wake word ---
    if wake_index is not None:
        start_ms = (wake_index + 1) * chunk_ms
        trimmed_audio = audio_segment[start_ms:]
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f_out:
            trimmed_audio.export(f_out.name, format="wav")
            with sr.AudioFile(f_out.name) as source:
                result_audio = recognizer.record(source)
        os.remove(f_out.name)
        print(f"[extract_post_wake_audio] Returning trimmed audio from {start_ms/1000:.2f}s onward.")
        return result_audio

    # --- Not found: return full audio (no None anymore) ---
    print("[extract_post_wake_audio] Wake word not found — returning full audio.")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f_out:
        audio_segment.export(f_out.name, format="wav")
        with sr.AudioFile(f_out.name) as source:
            result_audio = recognizer.record(source)
    os.remove(f_out.name)
    return result_audio