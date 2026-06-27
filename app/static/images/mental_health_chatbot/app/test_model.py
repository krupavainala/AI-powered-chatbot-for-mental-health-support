from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")

print("Loading model...")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")
model.to(torch.device("cpu"))  # Force CPU usage, safer

print("Encoding input...")
input_text = "Hello, how are you?"
input_ids = tokenizer.encode(input_text + tokenizer.eos_token, return_tensors='pt')

print("Generating response...")
output_ids = model.generate(input_ids, max_length=50)

response = tokenizer.decode(output_ids[0], skip_special_tokens=True)
print("Bot response:", response)
