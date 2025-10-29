import speech_recognition as sr
import sounddevice
r = sr.Recognizer()

# Find ReSpeaker mic automatically
mic_name = "ReSpeaker 4 Mic Array"
mic_index = None
for i, name in enumerate(sr.Microphone.list_microphone_names()):
    if mic_name.lower() in name.lower():
        mic_index = i
        break

if mic_index is None:
    raise RuntimeError(f"Microphone '{mic_name}' not found!")
else:
    print(f"Using mic index {mic_index}: {mic_name}")

source = sr.Microphone(device_index=mic_index)
