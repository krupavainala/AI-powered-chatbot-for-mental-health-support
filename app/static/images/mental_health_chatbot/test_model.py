from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

input_text = "Hello, I feel alone"
input_ids = tokenizer.encode(input_text + tokenizer.eos_token, return_tensors='pt')

chat_history_ids = model.generate(
    input_ids,
    max_length=1000,
    pad_token_id=tokenizer.eos_token_id,
    do_sample=True,
    top_p=0.95,
    top_k=50,
    temperature=0.7
)

response = tokenizer.decode(chat_history_ids[:, input_ids.shape[-1]:][0], skip_special_tokens=True)
print("Bot response:", response)
