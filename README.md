# 🧠 Jarvis - AI Voice Assistant using Python

Jarvis is an advanced **AI-powered virtual assistant** built with Python. Inspired by Marvel's Iron Man, this assistant uses **speech recognition**, **natural language processing**, and **system automation** to interact with users and perform various tasks—like your personal digital butler.

![GitHub stars](https://img.shields.io/github/stars/Kartos46/JARVIS?style=social)
![Python Version](https://img.shields.io/badge/Python-3.x-blue)
![License](https://img.shields.io/badge/License-MIT-green)

> "Just A Rather Very Intelligent System" — now on your machine.

---

## 📌 Features

✅ Understands **voice** and **text** commands  
✅ Speaks responses using **TTS (Text-to-Speech)**  
✅ Tells **date and time**  
✅ Opens and closes apps like **Notepad, Chrome, VS Code**  
✅ Automates **YouTube** and **Google** searches  
✅ Tells **jokes** and responds to appreciation  
✅ Uses a **trained neural network** for intent detection (`chat_model.h5`)  
✅ Responds contextually using `intents.json`  
✅ Friendly, conversational AI replies  
✅ Fully **expandable** with new commands and intents

---

## 🛠️ Technologies Used

- **Python 3.x**
- **TensorFlow / Keras** – Deep Learning for intent classification
- **SpeechRecognition** – Microphone input
- **pyttsx3** – Offline text-to-speech engine
- **PyAutoGUI** – GUI automation (e.g., mouse and keyboard control)
- **NumPy** – Numerical operations
- **scikit-learn** – Label encoding
- **Standard Python Libraries**: `webbrowser`, `psutil`, `datetime`, `subprocess`, `os`, `pickle`, `json`

---

## 📁 Project Structure
Jarvis-AI/  
│  
├── intents.json                            # Intent patterns and responses  
├── model_train.py                          # Script to train the model  
├── main.py                                 # Main assistant logic  
├── chat_model.h5                           # Trained neural network model  
├── tokenizer.pkl                           # Tokenizer for input processing  
├── label_encoder.pkl                       # Label encoder for output classes  
├── requirements.txt                        # Python dependencies  
└── README.md                               # Project documentation  


🚀 How to Run
1. Clone the Repository
    git clone https://github.com/Kartos46/JARVIS.git
    cd JARVIS

2. Install Dependencies
    pip install -r requirements.txt
   
3. Train the Model (Skip if already trained)
    python model_train.py

4. Start Jarvis
    python main.py
   

 💬 Example Commands
 
      "What is the time?"        → Returns current time  
      "Tell me a joke"           → Tells a random joke  
      "Open Chrome"              → Opens Chrome browser  
      "Close Chrome"             → Closes Chrome  
      "Who made you?"            → Tells the creator  
      "Shut up"                  → Jarvis gives a funny reply  
      "Haha"                     → Laughs back  
      "You are awesome"          → Thanks you  


🧪 Future Ideas

    🌦️ Add weather report integration  
    📧 Email & WhatsApp automation  
    🎵 Music playback  
    🖥️ GUI using Tkinter or PyQt  
    ⏰ Task reminders and calendar  



👨‍💻 Developer
  Kartik Redij
   📧 kartikredij6@gmail.com
   📍 India
   🔗 GitHub: https://github.com/Kartos46
   

📜 License
   This project is licensed under the MIT License.
   Free to use for learning, research, and educational purposes.
