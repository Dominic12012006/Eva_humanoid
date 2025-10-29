import speech_recognition as sr
import sounddevice
# from llm3 import rag_query
# Initialize recognizer
r = sr.Recognizer()

# Use your USB mic
mic = sr.Microphone()  # Your mic index

print("Adjusting for ambient noise, please wait...")
with mic as source:
    r.adjust_for_ambient_noise(source, duration=1)
print("Ready! Say something...")

try:
    while True:
        with mic as source:
            print("\nListening...")
            audio = r.listen(source)

        try:
            text = r.recognize_google(audio)
            print("You said:", text)
            # print(rag_query(text))
        except sr.UnknownValueError:
            print("Sorry, could not understand the audio.")
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))

except KeyboardInterrupt:
    print("\nStopped listening.")
