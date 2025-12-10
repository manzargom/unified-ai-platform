from transformers import AutoProcessor, SeamlessM4TModel
import torch

# Load processor and model (this will download ~5GB first time)
print("Loading model... This may take a few minutes...")
processor = AutoProcessor.from_pretrained("facebook/seamless-m4t-large")
model = SeamlessM4TModel.from_pretrained("facebook/seamless-m4t-large")

# Move to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
print(f"Model loaded on: {device}")

# Example text translation: English to Spanish
text_inputs = "Hello, my friend! How are you today?"
tgt_lang = "spa"  # Spanish

# Process and translate
inputs = processor(text=text_inputs, src_lang="eng", return_tensors="pt").to(device)
output_tokens = model.generate(**inputs, tgt_lang=tgt_lang, generate_speech=False)

# Decode the translation
translated_text = processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)
print(f"\nOriginal (English): {text_inputs}")
print(f"Translated (Spanish): {translated_text}")

# Optional: Try another language
print("\n--- Trying French ---")
tgt_lang = "fra"
inputs = processor(text=text_inputs, src_lang="eng", return_tensors="pt").to(device)
output_tokens = model.generate(**inputs, tgt_lang=tgt_lang, generate_speech=False)
translated_text = processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)
print(f"Translated (French): {translated_text}")