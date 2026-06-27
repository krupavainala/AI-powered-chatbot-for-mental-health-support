from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_name = "microsoft/DialoGPT-medium"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
model.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))

chat_history_ids = {}

def generate_bot_response(user_input, session_id="default"):
    global chat_history_ids
    new_user_input_ids = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors='pt').to(model.device)

    if session_id in chat_history_ids:
        bot_input_ids = torch.cat([chat_history_ids[session_id], new_user_input_ids], dim=-1)
    else:
        bot_input_ids = new_user_input_ids

    chat_history_ids[session_id] = model.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)
    response = tokenizer.decode(chat_history_ids[session_id][:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
    return response


from app.quotes import detect_mood_from_emoji, mood_responses


def generate_response(user_message):
    # Emergency flag check (can be used in route)
    if is_emergency(user_message):
        return "⚠️ It sounds like you're in distress. Please stay calm. We're here for you. If you're in danger, reach out to emergency services."

    # Mood detection based on emoji
    mood = detect_mood_from_emoji(user_message)
    if mood and mood in mood_responses:
        return mood_responses[mood]

    # Otherwise use AI
    return get_chatbot_response(user_message)
