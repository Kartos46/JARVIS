import json
import pickle
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, GlobalAveragePooling1D
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder

# Load intents data
try:
    with open("intents.json") as file:
        data = json.load(file)
    print("Intents data loaded successfully.")
except FileNotFoundError as e:
    print(f"Error: {e}")
    print("Ensure that the 'intents.json' file is in the correct directory.")
    exit()
except Exception as e:
    print(f"Unexpected error while loading the data: {e}")
    exit()

# Prepare training data
training_sentences = []
training_labels = []
labels = []
responses = []

for intent in data['intents']:
    for pattern in intent['patterns']:
        training_sentences.append(pattern)
        training_labels.append(intent['tag'])
    responses.append(intent['responses'])
    
    if intent['tag'] not in labels:
        labels.append(intent['tag'])

# Number of unique classes (labels)
number_of_classes = len(labels)
print(f"Number of classes: {number_of_classes}")

# Label encoding
label_encoder = LabelEncoder()
label_encoder.fit(training_labels)
training_labels = label_encoder.transform(training_labels)

# Tokenization and padding
vocab_size = 1000  # Max number of words to consider
max_len = 20       # Maximum length of sequences
oov_token = "<OOV>"  # Out-of-vocabulary token
embedding_dim = 16  # Embedding dimension for word vectors

tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_token)
tokenizer.fit_on_texts(training_sentences)
word_index = tokenizer.word_index
sequences = tokenizer.texts_to_sequences(training_sentences)
padded_sequences = pad_sequences(sequences, truncating='post', maxlen=max_len)

# Building the model
model = Sequential([
    Embedding(vocab_size, embedding_dim, input_length=max_len),
    GlobalAveragePooling1D(),
    Dense(16, activation="relu"),
    Dense(16, activation="relu"),
    Dense(number_of_classes, activation="softmax")
])

model.compile(loss='sparse_categorical_crossentropy', optimizer="adam", metrics=["accuracy"])
model.summary()

# Train the model
try:
    history = model.fit(padded_sequences, np.array(training_labels), epochs=1000, batch_size=8)
    print("Model trained successfully.")
except Exception as e:
    print(f"Error during model training: {e}")
    exit()

# Save the trained model and necessary files
try:
    # Save the model
    model.save("chat_model.h5")
    print("Model saved to 'chat_model.h5'.")

    # Save the tokenizer
    with open("tokenizer.pkl", "wb") as f:
        pickle.dump(tokenizer, f, protocol=pickle.HIGHEST_PROTOCOL)
    print("Tokenizer saved to 'tokenizer.pkl'.")

    # Save the label encoder
    with open("label_encoder.pkl", "wb") as encoder_file:
        pickle.dump(label_encoder, encoder_file, protocol=pickle.HIGHEST_PROTOCOL)
    print("Label encoder saved to 'label_encoder.pkl'.")

except Exception as e:
    print(f"Error during saving files: {e}")
    exit()
