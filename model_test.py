import json
import pickle
import random
import numpy as np
import datetime
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Load resources
try:
    with open("intents.json") as file:
        data = json.load(file)
except FileNotFoundError:
    print("Error: 'intents.json' not found.")
    exit()

try:
    model = load_model("chat_model.h5")
except Exception as e:
    print(f"Error loading model: {e}")
    exit()

try:
    with open("tokenizer.pkl", "rb") as f:
        tokenizer = pickle.load(f)
except FileNotFoundError:
    print("Error: 'tokenizer.pkl' not found.")
    exit()

try:
    with open("label_encoder.pkl", "rb") as f:
        label_encoder = pickle.load(f)
except FileNotFoundError:
    print("Error: 'label_encoder.pkl' not found.")
    exit()

def get_response(input_text, confidence_threshold=0.7):
    """
    Get chatbot response from user input.
    """
    padded_seq = pad_sequences(
        tokenizer.texts_to_sequences([input_text]),
        maxlen=20, truncating='post'
    )

    result = model.predict(padded_seq, verbose=0)
    confidence = np.max(result)

    if confidence < confidence_threshold:
        return "I'm not sure how to respond to that. Could you rephrase?"

    tag = label_encoder.inverse_transform([np.argmax(result)])[0]

    if tag == "datetime":
        now = datetime.datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')} and the time is {now.strftime('%I:%M %p')}"

    for intent in data['intents']:
        if intent['tag'] == tag:
            return random.choice(intent['responses'])

    return "I'm sorry, I don't understand that."

def main():
    print("🤖 Hello! I am Jarvis Chatbot.")
    print("Type 'exit' or 'quit' to end the chat.\n")

    while True:
        user_input = input("You: ").strip().lower()
        if user_input in ["quit", "exit"]:
            print("Jarvis: Goodbye! Have a great day.")
            break
        elif not user_input:
            print("Jarvis: Please enter something.")
            continue

        response = get_response(user_input)
        print("Jarvis:", response)

if __name__ == "__main__":
    main()
