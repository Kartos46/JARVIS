import json
import pickle
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import random

# Load necessary files and model once
try:
    with open("intents.json") as file:
        data = json.load(file)

    model = load_model("chat_model.h5")

    with open("tokenizer.pkl", "rb") as f:
        tokenizer = pickle.load(f)

    with open("label_encoder.pkl", "rb") as encoder_file:
        label_encoder = pickle.load(encoder_file)

    print("Model and data loaded successfully.")

except FileNotFoundError as e:
    print(f"Error: {e}")
    print("Ensure that all necessary files are available in the correct directory.")
    exit()

except Exception as e:
    print(f"Unexpected error: {e}")
    exit()

# Main loop to interact with the assistant
while True:
    input_text = input("Enter your command-> ").lower()  # Take input and convert to lowercase

    # Check for exit command
    if input_text in ['exit', 'quit', 'bye']:
        print("Goodbye!")
        break

    try:
        # Prepare the input for prediction
        padded_sequences = pad_sequences(tokenizer.texts_to_sequences([input_text]), maxlen=20, truncating='post')

        # Predict the tag based on the input
        result = model.predict(padded_sequences)
        tag = label_encoder.inverse_transform([np.argmax(result)])[0]  # Get the predicted tag

        # Find matching responses
        for intent in data['intents']:
            if intent['tag'] == tag:
                response = random.choice(intent['responses'])  # Randomly select a response
                print(f"Response: {response}")
                break

        # If no matching tag is found
        else:
            print("Sorry, I didn't understand that.")

    except Exception as e:
        print(f"Error during prediction: {e}")
