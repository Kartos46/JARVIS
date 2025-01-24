import json
import pickle
import random
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Load intents, model, tokenizer, and label encoder
try:
    with open("intents.json") as file:
        data = json.load(file)
except FileNotFoundError:
    print("Error: 'intents.json' not found. Please ensure the file exists.")
    exit()

try:
    model = load_model("chat_model.h5")
except Exception as e:
    print(f"Error loading the model: {e}")
    exit()

try:
    with open("tokenizer.pkl", "rb") as f:
        tokenizer = pickle.load(f)
except FileNotFoundError:
    print("Error: 'tokenizer.pkl' not found. Please ensure the file exists.")
    exit()

try:
    with open("label_encoder.pkl", "rb") as encoder_file:
        label_encoder = pickle.load(encoder_file)
except FileNotFoundError:
    print("Error: 'label_encoder.pkl' not found. Please ensure the file exists.")
    exit()

def get_response(input_text, confidence_threshold=0.7):
    """
    Get the response from the model based on the user's input.

    Args:
        input_text (str): The input text from the user.
        confidence_threshold (float): Minimum confidence level to generate a response.

    Returns:
        str: The chatbot's response.
    """
    padded_sequences = pad_sequences(
        tokenizer.texts_to_sequences([input_text]),
        maxlen=20,
        truncating='post'
    )
    result = model.predict(padded_sequences, verbose=0)
    confidence = np.max(result)  # Get the highest confidence level
    if confidence < confidence_threshold:
        return "I'm not sure how to respond to that. Could you rephrase?"

    tag = label_encoder.inverse_transform([np.argmax(result)])[0]
    for intent in data['intents']:
        if intent['tag'] == tag:
            return random.choice(intent['responses'])

    return "I'm sorry, I don't understand that."

def main():
    """
    Main loop for interacting with the chatbot.
    """
    print("Hello! I am your chatbot. How can I assist you today?")
    print("Type 'quit' or 'exit' to end the chat.\n")

    while True:
        input_text = input("Enter your command-> ").strip().lower()
        if input_text in ["quit", "exit"]:
            print("Goodbye! Have a great day!")
            break
        elif not input_text:
            print("Please enter a valid command.")
            continue

        response = get_response(input_text)
        print(response)

if __name__ == "__main__":
    main()
