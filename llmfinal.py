import re
import time
import io
import speech_recognition as sr
from groq import Groq
import sounddevice
from llm3 import rag_query, call_llm_norm, llm_classify,summarize
from ttseleven import speak
import tempfile
from pydub import AudioSegment
import os
# ---------------- Groq API Setup ----------------
from dotenv import load_dotenv
load_dotenv()
# ---------------- Groq API Setup ----------------
groq_client = Groq(api_key=os.getenv('groq_api'))
# ---------------- Conversation History ----------------
conversation_history = []  # list of dicts like [{'role': 'user', 'content': '...'}, {'role': 'assistant', 'content': '...'}]

def add_to_history(role, content):
    """Add a new message to conversation history."""
    conversation_history.append({"role": role, "content": content})
    # Limit history length to prevent context overload
    if len(conversation_history) > 10:
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
#     """Convert recorded audio to text using Groq's Whisper model."""
#     try:
#         audio_file = io.BytesIO(audio_data.get_wav_data())
#         translation = groq_client.audio.transcriptions.create(
#             file=("audio.wav"
#             "v", audio_file.getvalue()),
#             model="whisper-large-v3",
#         )
#         return translation.text
#     except Exception as e:
#         print("Error transcribing audio:", e)
#         return None
def audio_to_text(audio_data):
    """Convert recorded audio to text using OpenAI's Whisper model."""
    try:
        # Get the WAV audio data from the recognizer
        wav_data = audio_data.get_wav_data()

        # Save WAV data to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav_file:
            temp_wav_file.write(wav_data)
            temp_wav_filename = temp_wav_file.name  # Save the filename for later use

        # Now, use the temporary file for transcription
        with open(temp_wav_filename, "rb") as audio_file:
            translation = groq_client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3",
        )
            return translation.text
    except Exception as e:
        print("Error transcribing audio:", e)
        return None
    finally:
        # Clean up: remove the temporary WAV file
        if os.path.exists(temp_wav_filename):
            os.remove(temp_wav_filename)

def extract_prompt(transcribed_text, wake_word):
    """Extracts the prompt after the wake word (e.g., 'hello, tell me a joke')."""
    pattern = rf'\b{re.escape(wake_word)}[\s,.?!]*(.*)'
    match = re.search(pattern, transcribed_text, re.IGNORECASE)
    return match.group(1).strip() if match else None

# ---------------- ASR Setup ----------------
r = sr.Recognizer()
wake_word = "hello"
mic_index = 25
source = sr.Microphone(device_index=mic_index)

# ---------------- Callback ----------------
def callback(recognizer, audio):
    data = audio.get_wav_data()
    if len(data) < 1000:
        print("Warning: captured audio seems too short.")
        return

    try:
        prompt_text = audio_to_text(audio)
        if prompt_text:
            clean_prompt = extract_prompt(prompt_text, wake_word)
            if clean_prompt:
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
                res_sum=summarize(res)
                print(f"\nAssistant: {res}\n")
                speak(res_sum)
                print("done")

    except Exception as e:
        print("Error in callback:", e)

# ---------------- Main Loop ----------------
def start_listening():
    print("Adjusting for ambient noise, please wait...")
    with source as s:
        r.adjust_for_ambient_noise(s, duration=1)
        print(f"\nSay '{wake_word}' followed by your prompt.\n")

        # Test mic once
        print("Testing mic with one recording...")
        audio = r.listen(s, timeout=5, phrase_time_limit=5)
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

# ---------------- Run ----------------
if __name__ == "__main__":
    start_listening()
