import logging
import os
from datetime import datetime
from textblob import TextBlob
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import pyttsx3
from database import save_message, get_chat_history

# Setup logging
log_path = os.path.join(os.path.dirname(__file__), 'chatbot.log')
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize TTS engine safely
try:
    engine = pyttsx3.init()
    engine.setProperty('rate', 160)
    engine.setProperty('volume', 0.9)
except Exception as e:
    logging.warning(f"TTS engine init failed: {e}")
    engine = None

# Load model and tokenizer
MODEL_PATH = "./local_model/godel"  # or use full path if needed

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH)
device = torch.device("cpu")
model.to(device)

def get_mood_emoji(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0.3:
        return "😊"
    elif polarity < -0.3:
        return "😔"
    else:
        return "😐"

def speak_response(text):
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            logging.warning(f"TTS engine error: {e}")





def build_prompt(user_input, chat_history=None, intro_text=None):

    base_intro = (
        "You are a compassionate and professional mental health assistant. "
        "Respond empathetically, providing support, motivation, and practical advice.\n\n"
    )

    calming_instructions = (
        "If the user asks about stress, anxiety, or calming exercises, "
        "provide simple, step-by-step relaxation techniques such as breathing exercises, "
        "progressive muscle relaxation, or visualization. Be gentle, encouraging, and clear.\n\n"
    )

    motivation_instructions = (
        "If the user asks for motivation or encouragement, offer positive affirmations "
        "and inspiring advice to help boost their confidence.\n\n"
    )

    meditation_instructions = (
        "If the user asks about meditation, suggest beginner-friendly meditation or breathing techniques.\n\n"
    )

    prompt = intro_text if intro_text else (
    base_intro + calming_instructions + motivation_instructions + meditation_instructions
)


    if chat_history:
        MAX_HISTORY = 6
        recent_history = chat_history[-MAX_HISTORY:]
        for speaker, text in recent_history:
            prompt += f"{speaker}: {text}\n"

    prompt += f"User: {user_input}\nAssistant:"

    return prompt


def generate_from_model(prompt):
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    input_ids = inputs.input_ids.to(device)
    attention_mask = inputs.attention_mask.to(device)
    output_ids = model.generate(
        input_ids,
        attention_mask=attention_mask,
        max_length=256,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        temperature=0.7,
        pad_token_id=tokenizer.eos_token_id
    )
    response = tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()
    if response.lower().startswith("assistant:"):
        response = response[len("assistant:"):].strip()
    return response

def generate_response(user_input, session_id="default"):
    try:
        if not session_id or not isinstance(session_id, str):
            logging.warning(f"Invalid session_id '{session_id}' received; defaulting to 'default'")
            session_id = "default"

        logging.info(f"generate_response called for session_id={session_id} with input: {user_input}")
        chat_history_raw = get_chat_history(session_id) or []
        logging.debug(f"Raw chat history: {chat_history_raw}")

        chat_history = []
        for entry in chat_history_raw:
            try:
                if isinstance(entry, dict):
                    sender = entry.get('sender')
                    message = entry.get('message')
                elif hasattr(entry, 'keys') and 'sender' in entry.keys() and 'message' in entry.keys():
                    sender = entry['sender']
                    message = entry['message']
                else:
                    logging.warning(f"Unknown entry format: {entry}")
                    continue

                if sender and message:
                    chat_history.append((str(sender).capitalize(), str(message)))
                else:
                    logging.warning(f"Incomplete chat entry: {entry}")
            except Exception as e:
                logging.error(f"Error parsing chat history entry: {entry} — {e}")
                continue

        save_message(session_id, "user", user_input)
        logging.info("User message saved to DB")

        user_input_lower = user_input.lower()

        distress_keywords = ["stress", "sad", "depress", "anxious", "anxiety", "overwhelmed", "tired", "hopeless", "lonely"]
        motivation_keywords = ["motivation", "inspire", "affirmation", "encourage", "confidence"]
        meditation_keywords = ["meditation", "meditate", "calm", "relax", "breathing", "peace"]
        music_keywords = ["music", "song", "soothing music", "calm music"]
        emergency_keywords = ["emergency", "suicide", "hurt myself", "end my life", "kill myself"]

        if any(word in user_input_lower for word in emergency_keywords):
            emergency_response = (
                "It sounds like you're in a lot of pain. You're not alone, and there are people who want to help. "
                "Please reach out to a mental health professional or contact a crisis line in your area. "
                "If you're in immediate danger, please call emergency services. You are important. 💙"
            )
            logging.warning("Emergency detected - urgent message returned")
            save_message(session_id, "bot", emergency_response)
            speak_response(emergency_response)
            return emergency_response, "🚨"

        if any(word in user_input_lower for word in distress_keywords):
            intro_text = (
                "You are a compassionate mental health assistant. The user is distressed. "
                "Respond with empathy, motivational advice, and simple calming exercises.\n\n"
            )
            logging.info("Distress detected - using distress prompt")
        elif any(word in user_input_lower for word in motivation_keywords):
            intro_text = (
                "You are a supportive assistant. Provide motivational advice and encouragement.\n\n"
            )
            logging.info("Motivation detected - using motivation prompt")
        elif any(word in user_input_lower for word in meditation_keywords):
            intro_text = (
                "You are a calm assistant. Offer a short calming exercise or breathing technique.\n\n"
            )
            logging.info("Meditation detected - using meditation prompt")
        elif any(word in user_input_lower for word in music_keywords):
            music_response = (
                "Here's some calming music to help you relax: https://open.spotify.com/playlist/5LWAFfebSzZT7XzaOmN2lX?si=ru0ol-lmSzqdBhMfVSH1Pw&pi=pWEAtLVnT-WE9 🎵"
            )
            save_message(session_id, "bot", music_response)
            speak_response(music_response)
            return music_response, "🎶"
        else:
            intro_text = (
                "You are a compassionate, calm, and professional mental health assistant. "
                "Respond empathetically and supportively.\n\n"
            )
            logging.info("Default chat mode - using general prompt")

        prompt = build_prompt(user_input, chat_history, intro_text)
        response = generate_from_model(prompt)
        logging.info(f"Model generated response: {response}")

        save_message(session_id, "bot", response)
        logging.info("Bot response saved to DB")

        mood = get_mood_emoji(response)
        logging.info(f"Mood emoji detected: {mood}")

        speak_response(response)

        return response, mood

    except Exception as e:
        logging.error("Exception in generate_response", exc_info=True)
        print(f"Error in generate_response: {e}")
        return "I'm really sorry, something went wrong. Please try again later.", "⚠"
