import json
import pickle
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Embedding, GlobalAveragePooling1D
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.callbacks import EarlyStopping

# Load and prepare data
def load_intents(file_path="intents.json"):
    """
    Load intents data from a JSON file.
    """
    try:
        with open(file_path) as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: '{file_path}' not found.")
        exit()

data = load_intents()
training_sentences, training_labels, labels, responses = [], [], [], []

for intent in data['intents']:
    for pattern in intent['patterns']:
        training_sentences.append(pattern)
        training_labels.append(intent['tag'])
    responses.append(intent['responses'])
    if intent['tag'] not in labels:
        labels.append(intent['tag'])

number_of_classes = len(labels)

# Encode labels
label_encoder = LabelEncoder()
training_labels = label_encoder.fit_transform(training_labels)

# Tokenize and pad sequences
vocab_size = 1000
max_len = 20
oov_token = "<OOV>"
embedding_dim = 16

tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_token)
tokenizer.fit_on_texts(training_sentences)
sequences = tokenizer.texts_to_sequences(training_sentences)
padded_sequences = pad_sequences(sequences, truncating='post', maxlen=max_len)

# Build the model
model = Sequential([
    Embedding(vocab_size, embedding_dim, input_length=max_len),
    GlobalAveragePooling1D(),
    Dense(16, activation="relu"),
    Dense(16, activation="relu"),
    Dense(number_of_classes, activation="softmax")
])

model.compile(loss='sparse_categorical_crossentropy', optimizer="adam", metrics=["accuracy"])
model.summary()

# Train the model with early stopping
early_stopping = EarlyStopping(monitor='loss', patience=10, restore_best_weights=True)
history = model.fit(padded_sequences, np.array(training_labels), epochs=1000, callbacks=[early_stopping])

# Save resources
model.save("chat_model.h5")

with open("tokenizer.pkl", "wb") as f:
    pickle.dump(tokenizer, f, protocol=pickle.HIGHEST_PROTOCOL)

with open("label_encoder.pkl", "wb") as encoder_file:
    pickle.dump(label_encoder, encoder_file, protocol=pickle.HIGHEST_PROTOCOL)

# Chatbot functionality
def load_resources():
    """
    Load the model, tokenizer, and label encoder for the chatbot.
    """
    try:
        model = load_model("chat_model.h5")
        with open("tokenizer.pkl", "rb") as f:
            tokenizer = pickle.load(f)
        with open("label_encoder.pkl", "rb") as encoder_file:
            label_encoder = pickle.load(encoder_file)
        return model, tokenizer, label_encoder
    except Exception as e:
        print(f"Error loading resources: {e}")
        exit()

def predict_response(input_text, model, tokenizer, label_encoder, confidence_threshold=0.7):
    """
    Predict the chatbot's response based on user input.

    Args:
        input_text (str): User's input text.
        model (tf.keras.Model): Trained model.
        tokenizer (Tokenizer): Tokenizer for preprocessing.
        label_encoder (LabelEncoder): Label encoder for decoding predictions.
        confidence_threshold (float): Minimum confidence to accept a response.

    Returns:
        str: The chatbot's response or a fallback message.
    """
    padded_sequences = pad_sequences(tokenizer.texts_to_sequences([input_text]), maxlen=max_len, truncating='post')
    predictions = model.predict(padded_sequences, verbose=0)
    confidence = np.max(predictions)
    
    if confidence < confidence_threshold:
        return "I'm not confident about my answer. Can you rephrase?"
    
    tag = label_encoder.inverse_transform([np.argmax(predictions)])[0]
    for intent in data['intents']:
        if intent['tag'] == tag:
            return np.random.choice(intent['responses'])
    return "I'm sorry, I don't understand that."

def chatbot():
    """
    Main loop for chatbot interaction.
    """
    print("\nWelcome to the Chatbot! Type 'quit' or 'exit' to end the conversation.")
    model, tokenizer, label_encoder = load_resources()

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ["quit", "exit"]:
            print("Chatbot: Goodbye! Have a great day!")
            break
        elif not user_input:
            print("Chatbot: Please enter a valid message.")
            continue

        response = predict_response(user_input, model, tokenizer, label_encoder)
        print(f"Chatbot: {response}")

if __name__ == "__main__":
    chatbot()
