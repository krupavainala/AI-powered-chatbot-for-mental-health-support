from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_name = "microsoft/Godel-v1_1-large-seq2seq"

print("Downloading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.save_pretrained("./local_model/godel")

print("Downloading model...")
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
model.save_pretrained("./local_model/godel")

print("Download complete. Model saved to ./local_model/godel")
