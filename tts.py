# from gtts import gTTS
# import os



# def speak(text:str,language='en'):
#     tts = gTTS(text=text, lang=language, slow=False)  # slow=False makes it speak normally
#     tts.save("output.mp3")
#     os.system("mpg321 output.mp3")   # Linux


# gemini_tts_example.py

from google.cloud import texttospeech_v1beta1 as texttospeech
from google.api_core.client_options import ClientOptions
from playsound import playsound

# ---- CONFIG ----
PROJECT_ID = "quiet-spirit-469107-t6"
TTS_LOCATION = "global"   # or use regional endpoint if needed
MODEL = "gemini-2.5-flash-tts"  # or gemini-2.5-pro-tts
VOICE = "Aoede"
LANGUAGE_CODE = "en-US"

# ---- INITIALIZE CLIENT ----
API_ENDPOINT = (
    f"{TTS_LOCATION}-texttospeech.googleapis.com"
    if TTS_LOCATION != "global"
    else "texttospeech.googleapis.com"
)

client = texttospeech.TextToSpeechClient(
    client_options=ClientOptions(api_endpoint=API_ENDPOINT)
)

# ---- DEFINE INPUT TEXT AND PROMPT ----
PROMPT = "You are a guide to SRM University. Talk in calm and measured tones with a fast pace"

# ---- DEFINE VOICE SELECTION ----
voice = texttospeech.VoiceSelectionParams(
    name=VOICE,
    language_code=LANGUAGE_CODE,
    model_name=MODEL
)

# ---- SYNTHESIZE SPEECH ----
def speak(TEXT):
    response = client.synthesize_speech(
        input=texttospeech.SynthesisInput(text=TEXT, prompt=PROMPT),
        voice=voice,
        audio_config=texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
    )

    # ---- SAVE OUTPUT AUDIO ----
    output_file = "gemini_output.mp3"
    with open(output_file, "wb") as out:
        out.write(response.audio_content)
        print(f"✅ Audio content written to {output_file}")

    # ---- PLAY SOUND (optional) ----
    playsound(output_file)
