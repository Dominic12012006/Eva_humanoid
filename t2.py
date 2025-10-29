import requests
import os

# -----------------------------
# 0. OpenRouter API key
# -----------------------------
OPENROUTER_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/completions"

# -----------------------------
# 1. Example prompt
# -----------------------------
prompt = "Write a short poem about a sunny day."

# -----------------------------
# 2. Create the request payload
# -----------------------------
payload = {
    "model": "gpt-3.5-turbo",  # OpenRouter hosted model
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "max_tokens": 200,
    "temperature": 0.7
}

# -----------------------------
# 3. Send request
# -----------------------------
headers = {
    "Authorization": f"Bearer {OPENROUTER_KEY}",
    "Content-Type": "application/json"
}

response = requests.post(API_URL, json=payload, headers=headers)

# -----------------------------
# 4. Parse and print response
# -----------------------------
if response.status_code == 200:
    data = response.json()
    # OpenRouter returns the text in choices[0].message.content
    print("Generated text:\n", data["choices"][0]["message"]["content"])
else:
    print("Error:", response.status_code, response.text)
