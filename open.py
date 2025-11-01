import re
import time
import io
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import speech_recognition as sr
from groq import Groq
import sounddevice
from openai import OpenAI
from llm3 import rag_query, call_llm_norm, llm_classify,summarize
from ttseleven import speak
import os
import tempfile
from pydub import AudioSegment


load_dotenv()

elevenlabs = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
)
#USE FUZZY LOGIC
#SET TIME LIMIT ONCE WAKE WORD IS SAID INSTEAD OF REPEATING KEYWORD
#CHANGE WAKE WORD


conversation_history = []  # list of dicts like [{'role': 'user', 'content': '...'}, {'role': 'assistant', 'content': '...'}]

def add_to_history(role, content):
    """Add a new message to conversation history."""
    conversation_history.append({"role": role, "content": content})
    # Limit history length to prevent context overload
    if len(conversation_history) > 5:
        conversation_history.pop(0)

def get_context_text():
    """Convert history to a text-based context for passing into LLM."""
    context = ""
    for msg in conversation_history:
        prefix = "User:" if msg["role"] == "user" else "Assistant:"
        context += f"{prefix} {msg['content']}\n"
    return context.strip()

# ---------------- Audio Processing ----------------
# def audio_to_text(audio_data):
#     """
#     Convert recorded audio to text using ElevenLabs Speech-to-Text (Scribe).
#     Stores/overwrites a fixed .wav file each time.
#     """
#     try:
#         # Define a persistent WAV file path
#         wav_path = "/home/eva/Desktop/dominic/current_audio.wav"  # change this path if needed

#         # Write the audio data to the .wav file (overwrite if it exists)
#         wav_data = audio_data.get_wav_data()
#         with open(wav_path, "wb") as wav_file:
#             wav_file.write(wav_data)

#         # Open and transcribe the saved file
#         with open(wav_path, "rb") as audio_file:
#             transcription = elevenlabs.speech_to_text.convert(
#                 file=audio_file,
#                 model_id="scribe_v1",      # Only model supported currently
#                 tag_audio_events=True,     # Tag laughter/applause
#                 diarize=True,              # Annotate speakers
#                 # language_code="hin"      # Optional: specify language manually
#             )

#         # Return just the text
#         return transcription.text

#     except Exception as e:
#         print("Error transcribing audio:", e)
#         return None
# def audio_to_text(audio_data):
#     """Convert recorded audio to text using OpenAI's Whisper model."""
#     try:
#         # Get the WAV audio data from the recognizer
#         wav_data = audio_data.get_wav_data()

#         # Save WAV data to a temporary file
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav_file:
#             temp_wav_file.write(wav_data)
#             temp_wav_filename = temp_wav_file.name  # Save the filename for later use

#         # Now, use the temporary file for transcription
#         with open(temp_wav_filename, "rb") as audio_file:
#             transcription = elevenlabs.speech_to_text.convert(
#                 file=audio_file,
#                 model_id="scribe_v1",  # Only "scribe_v1" supported for now
#                 tag_audio_events=True,  # Tag events like laughter, applause
#                 language_code="hin",     # Or None to auto-detect
#                 diarize=True             # Annotate who is speaking
#             )
#             return transcription.text
#     except Exception as e:
#         print("Error transcribing audio:", e)
#         return None
#     finally:
#         # Clean up: remove the temporary WAV file
#         if os.path.exists(temp_wav_filename):
#             os.remove(temp_wav_filename)

def checkwake(audio_data):
    try:
        # Convert recorded audio to BytesIO
        audio_file = io.BytesIO(audio_data.get_wav_data())

        # Call ElevenLabs speech-to-text
        transcription = elevenlabs.speech_to_text.convert(
            file=audio_file,
            model_id="scribe_v1",      # ElevenLabs transcription model
            tag_audio_events=False,    # optional: True if you want events
            language_code="eng",
            diarize=False              # optional: True if multiple speakers
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

def extract_prompt(transcribed_text, wake_word):
    """Extracts the prompt after the wake word (e.g., 'hello, tell me a joke')."""
    pattern = rf'\b{re.escape(wake_word)}[\s,.?!]*(.*)'
    match = re.search(pattern, transcribed_text, re.IGNORECASE)
    return match.group(1).strip() if match else None

r = sr.Recognizer()
r.pause_threshold=1.0
wake_word = "eva"
mic_index = 25
source = sr.Microphone(device_index=mic_index)

def callback(recognizer, audio):
    data = audio.get_wav_data()
    if len(data) < 1000:
        print("Warning: captured audio seems too short.")
        return

    try:
        check=checkwake(audio)
        if check:
            clean_promptc = extract_prompt(check, wake_word)
            if clean_promptc:
                clean_prompt = audio_to_text(audio)
                #DDDD USER SAID THIS
                classify = llm_classify(clean_prompt).lower()
                print(f"Classification: {classify}")

                # Add user message to history
                add_to_history("user", clean_prompt)

                context = get_context_text()
                combined_prompt = f"{context}\nUser: {clean_prompt}\nAssistant:"

                if "yes" in classify:
                    print(f"\nRAG USER: {clean_prompt}")
                    res = rag_query(combined_prompt)
                else:
                    print(f"\nNORM USER: {clean_prompt}")
                    res = call_llm_norm(combined_prompt)

                # Add assistant response to history
                add_to_history("assistant", res)
                # res_sum=summarize(res)
                #dddd chatbot output
                print(f"\nAssistant: {res}\n")
                speak(res)
                print("done")

    except Exception as e:
        print("Error in callback:", e)

def start_listening():
    print("Adjusting for ambient noise, please wait...")
    with source as s:
        r.adjust_for_ambient_noise(s, duration=1)
        print(f"\nSay '{wake_word}' followed by your prompt.\n")

        # Test mic once
        print("Testing mic with one recording...")
        audio = r.listen(s, timeout=10, phrase_time_limit=15)
        print(f"Captured {len(audio.get_wav_data())} bytes of audio!")

    stop_listening = r.listen_in_background(source, callback)

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping ASR...")
        stop_listening(wait_for_stop=False)
        print("\nConversation History:")
        for i, msg in enumerate(conversation_history):
            print(f"{i+1}. {msg['role'].capitalize()}: {msg['content']}")

if __name__ == "__main__":
    start_listening()
