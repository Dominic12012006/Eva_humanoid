# from openai import OpenAI

# client = OpenAI()

# response = client.responses.create(
#     model="gpt-5",
#     input="How much gold would it take to coat the Statue of Liberty in a 1mm layer?",
#     reasoning={
#         "effort": "minimal"
#     }
# )

# print(response.output_text)


from openai import OpenAI

client = OpenAI()
audio_file= open("/home/eva/Desktop/dominic/gemini_output.wav", "rb")

transcription = client.audio.transcriptions.create(
    model="gpt-4o-transcribe", 
    file=audio_file
)

print(transcription.text)