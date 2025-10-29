import torch
from transformers import MarianMTModel, MarianTokenizer

# Force CPU
device = torch.device("cpu")

# English -> Hindi
tokenizer_en_hi = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-hi")
model_en_hi = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-en-hi").to(device)

# Hindi -> English
tokenizer_hi_en = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-hi-en")
model_hi_en = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-hi-en").to(device)

def translate(text, src_lang, tgt_lang):
    """Translate text between English and Hindi using MarianMT."""
    if src_lang == "en" and tgt_lang == "hi":
        tokenizer = tokenizer_en_hi
        model = model_en_hi
    elif src_lang == "hi" and tgt_lang == "en":
        tokenizer = tokenizer_hi_en
        model = model_hi_en
    else:
        return text

    inputs = tokenizer(text, return_tensors="pt")
    translated_tokens = model.generate(**inputs, max_length=256)
    translated_text = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
    return translated_text

print(translate("srm team robocon srm ka ek club hai", 'en', 'hi'))
