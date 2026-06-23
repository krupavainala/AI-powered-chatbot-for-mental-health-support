import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot import generate_from_model

def test_response():
    prompt = "User: I am feeling happy today.\nAssistant:"
    response = generate_from_model(prompt)
    print("Model response:", response)

if __name__ == "__main__":
    test_response()
