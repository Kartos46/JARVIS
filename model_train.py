import json
import pickle
import numpy as np
import tensorflow as tf
import datetime
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Embedding, GlobalAveragePooling1D
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.callbacks import EarlyStopping

# Load intents
def load_intents(file_path="intents.json"):
    try:
        with open(file_path) as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: '{file_path}' not found.")
        exit()

data = load_intents()
training_sentences, training_labels, labels = [], [], []

for intent in data['intents']:
    for pattern in intent['patterns']:
        training_sentences.append(pattern)
        training_labels.append(intent['tag'])
    if intent['tag'] not in labels:
        labels.append(intent['tag'])

# Encoding and tokenizing
label_encoder = LabelEncoder()
training_labels = label_encoder.fit_transform(training_labels)

vocab_size = 1000
embedding_dim = 16
max_len = 20
oov_token = "<OOV>"

tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_token)
tokenizer.fit_on_texts(training_sentences)
sequences = tokenizer.texts_to_sequences(training_sentences)
padded_sequences = pad_sequences(sequences, maxlen=max_len, truncating='post')

# Build model
model = Sequential([
    Embedding(vocab_size, embedding_dim, input_length=max_len),
    GlobalAveragePooling1D(),
    Dense(16, activation='relu'),
    Dense(16, activation='relu'),
    Dense(len(labels), activation='softmax')
])

model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model.summary()

# Train model
early_stop = EarlyStopping(monitor='loss', patience=10, restore_best_weights=True)
model.fit(padded_sequences, np.array(training_labels), epochs=1000, callbacks=[early_stop])

# Save model & assets
model.save("chat_model.h5")
with open("tokenizer.pkl", "wb") as f:
    pickle.dump(tokenizer, f)
with open("label_encoder.pkl", "wb") as f:
    pickle.dump(label_encoder, f)

# Chatbot prediction function
def predict_response(input_text, model, tokenizer, label_encoder, confidence_threshold=0.7):
    padded = pad_sequences(tokenizer.texts_to_sequences([input_text]), maxlen=max_len, truncating='post')
    predictions = model.predict(padded, verbose=0)
    confidence = np.max(predictions)

    if confidence < confidence_threshold:
        return "I'm not confident about that. Can you rephrase?"

    tag = label_encoder.inverse_transform([np.argmax(predictions)])[0]

    if tag == "datetime":
        now = datetime.datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')} and the time is {now.strftime('%I:%M %p')}"

    for intent in data['intents']:
        if intent['tag'] == tag:
            return np.random.choice(intent['responses'])

    return "I'm not sure what you mean."

# Chat loop
def chatbot():
    print("Welcome to Jarvis Chatbot! Type 'exit' to quit.")
    model, tokenizer, label_encoder = load_model("chat_model.h5"), pickle.load(open("tokenizer.pkl", "rb")), pickle.load(open("label_encoder.pkl", "rb"))

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("Jarvis: Goodbye!")
            break
        elif not user_input:
            print("Jarvis: Please type something.")
            continue

        response = predict_response(user_input, model, tokenizer, label_encoder)
        print("Jarvis:", response)

if __name__ == "__main__":
    chatbot()
