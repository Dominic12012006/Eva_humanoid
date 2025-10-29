from transformers import AutoTokenizer, AutoModel
import torch

# -----------------------------
# Config
# -----------------------------
model_name = "nvidia/NV-Embed-v2"
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using device:", device)

# -----------------------------
# Load model + tokenizer
# -----------------------------
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModel.from_pretrained(model_name, trust_remote_code=True).to(device)
model.eval()

# -----------------------------
# Test text
# -----------------------------
texts = ["Hello world", "The weather is nice today"]

# Tokenize
inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt").to(device)

# Forward pass
with torch.no_grad():
    outputs = model(**inputs)
    embeddings = outputs.last_hidden_state[:, 0, :]  # CLS token

print("Embeddings shape:", embeddings.shape)
print("Sample embedding:", embeddings[0][:10])  # first 10 dims
