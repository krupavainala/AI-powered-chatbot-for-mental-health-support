from chatbot import generate_response

chat_history = []

def chat_with_bot(user_input):
    global chat_history
    response, _ = generate_response(user_input, chat_history, session_id="testuser")
    chat_history.append(("user", user_input))
    chat_history.append(("bot", response))
    print(f"User: {user_input}")
    print(f"Bot: {response}\n")

# Test calm exercise generation
chat_with_bot("I need a calm exercise.")

# Test motivational response
chat_with_bot("Can you motivate me?")
