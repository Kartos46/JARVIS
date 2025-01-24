import datetime
import os
import sys
import time
import webbrowser
import pyttsx3  # Ensure this is installed using pip install pyttsx3
import speech_recognition as sr
import json
import pickle
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import psutil
import subprocess  # Added for closing Google Chrome
import pyautogui  # Ensure this is installed using pip install pyautogui

# Load necessary files and model
with open("intents.json") as file:
    data = json.load(file)

model = load_model("chat_model.h5")

with open("tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)

with open("label_encoder.pkl", "rb") as encoder_file:
    label_encoder = pickle.load(encoder_file)

# Initialize text-to-speech engine
def initialize_engine():
    engine = pyttsx3.init("sapi5")  # Initialize the speech engine
    voices = engine.getProperty('voices')  # Get available voices
    for voice in voices:
        if 'male' in voice.name.lower():  # Set male voice
            engine.setProperty('voice', voice.id)
            break
    engine.setProperty('rate', engine.getProperty('rate') - 50)  # Adjust speech speed
    engine.setProperty('volume', engine.getProperty('volume') + 0.25)  # Adjust volume
    return engine

def speak(text):
    engine = initialize_engine()
    engine.say(text)
    engine.runAndWait()

# Recognize voice commands
def command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening...", end="", flush=True)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("Recognizing...")
            query = recognizer.recognize_google(audio, language='en-in')
            print(f"User said: {query}\n")
        except Exception:
            speak("Sorry, I didn't catch that. Could you say that again?")
            return "None"
    return query.lower()

# Get current day
def cal_day():
    day = datetime.datetime.today().weekday() + 1
    day_dict = {
        1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"
    }
    return day_dict.get(day, "Unknown")

# Wish user based on time of day
def wishMe():
    hour = datetime.datetime.now().hour
    current_time = time.strftime("%I:%M %p")
    day = cal_day()

    if 0 <= hour < 12:
        speak(f"Good morning Kartik, it's {day} and the time is {current_time}.")
    elif 12 <= hour < 16:
        speak(f"Good afternoon Kartik, it's {day} and the time is {current_time}.")
    else:
        speak(f"Good evening Kartik, it's {day} and the time is {current_time}.")

# Handle social media commands
def social_media(command):
    platforms = {
        'facebook': "https://www.facebook.com/",
        'whatsapp': "https://web.whatsapp.com/",
        'discord': "https://discord.com/",
        'instagram': "https://www.instagram.com/"
    }
    for platform, url in platforms.items():
        if platform in command:
            speak(f"Opening {platform}.")
            webbrowser.open(url)
            return
    speak("No matching platform found.")

# Close social media tabs
def close_social_media(command):
    platforms = ['facebook', 'whatsapp', 'discord', 'instagram']
    for platform in platforms:
        if platform in command:
            speak(f"Closing {platform}.")
            try:
                # Check all browser processes and close tabs with the platform
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['name'] and ('chrome' in proc.info['name'].lower() or 'firefox' in proc.info['name'].lower()):
                        proc.terminate()
                speak(f"{platform.capitalize()} has been closed.")
                return
            except Exception as e:
                speak(f"Could not close {platform}. Error: {e}")
                return
    speak("No matching platform found to close.")

# Provide the schedule for the day
def schedule():
    day = cal_day().lower()
    speak("Here's your schedule for today.")
    week = {
        "monday": "From 9:00 to 9:50 you have Algorithms class, followed by System Design, and Programming Lab in the afternoon.",
        "tuesday": "From 9:00 you have Web Development, followed by Database Systems, and Open Source Projects Lab in the afternoon.",
        "wednesday": "A full day of classes, including Machine Learning, Operating Systems, Ethics in Technology, and Software Engineering Workshop.",
        "thursday": "Classes include Computer Networks, Cloud Computing, and a Cybersecurity lab in the afternoon.",
        "friday": "You have Artificial Intelligence, Advanced Programming, UI/UX Design, and Capstone Project work in the afternoon.",
        "saturday": "Team meetings for Capstone Project and Innovation and Entrepreneurship class in the morning, with time for coding practice in the afternoon.",
        "sunday": "A holiday, but it's a good time to catch up on pending work."
    }
    speak(week.get(day, "No schedule available."))

# Open system applications
def openApp(command):
    apps = {
        "calculator": 'C:\\Windows\\System32\\calc.exe',
        "notepad": 'C:\\Windows\\System32\\notepad.exe',
        "paint": 'C:\\Windows\\System32\\mspaint.exe'
    }
    for app, path in apps.items():
        if app in command:
            try:
                speak(f"Opening {app}.")
                os.startfile(path)
            except FileNotFoundError:
                speak(f"Sorry, I couldn't find {app} on this system.")
            return
    speak("Application not found.")

# Close system applications
def closeApp(command):
    processes = {
        "calculator": "calc.exe",
        "notepad": "notepad.exe",
        "paint": "mspaint.exe",
        "google": "chrome.exe"  # Add Google Chrome process name
    }
    for app, process in processes.items():
        if app in command:
            if any(proc.name().lower() == process.lower() for proc in psutil.process_iter()):
                speak(f"Closing {app}.")
                os.system(f"taskkill /f /im {process}")
            else:
                speak(f"{app} is not running.")
            return
    speak("Application not found.")


# Handle YouTube commands
# Handle YouTube commands
def youtube(query):
    if "open youtube" in query:
        speak("What should I search on YouTube?")
        search_query = command()  # Listening for the search query
        if search_query and search_query.lower() != "none":
            speak(f"Searching YouTube for {search_query}.")
            webbrowser.open(f"https://www.youtube.com/results?search_query={search_query}")
        else:
            speak("Opening YouTube.")
            webbrowser.open("https://www.youtube.com/")
    else:
        speak("Command not recognized for YouTube.")


    # Add scrolling and specific video functionality after opening YouTube
    while True:
        query = command()
        if 'scroll down' in query:
            speak("Scrolling down.")
            pyautogui.scroll(-800)
        elif 'scroll up' in query:
            speak("Scrolling up.")
            pyautogui.scroll(800)
        elif 'open' in query and ('video' in query or 'result' in query):
            try:
                number = int(query.split()[1])  # Extract the number
                speak(f"Opening video number {number}.")
                pyautogui.click(300, 300 + (number - 1) * 100)  # Adjust click position based on video list
            except (ValueError, IndexError):
                speak("Please specify a valid video number.")
        elif 'close youtube' in query:
            speak("Closing YouTube.")
            for proc in psutil.process_iter(['name']):
                if 'chrome' in proc.info['name'].lower():
                    proc.terminate()
            break

 # Improved Google Close Command with better process handling
def google(query):
    if "open google" in query or "search google" in query:
        speak("What should I search on Google?")
        search_query = command()
        if search_query and search_query.lower() != "none":
            speak(f"Searching Google for {search_query}.")
            webbrowser.open(f"https://www.google.com/search?q={search_query}")
        else:
            speak("Opening Google homepage.")
            webbrowser.open("https://www.google.com/")
    elif "google" in query and "close" in query:  # Handle closing Google Chrome specifically
        speak("Closing Google.")
        closed = False
        for proc in psutil.process_iter(['pid', 'name']):
            if 'chrome' in proc.info['name'].lower():  # Check for Chrome processes
                try:
                    proc.terminate()  # Attempt to terminate the process
                    closed = True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        if closed:
            speak("Google has been closed.")
        else:
            speak("Google was not running.")
    elif "google" in query:
        speak("Opening Google.")
        webbrowser.open("https://www.google.com/")
    else:
        speak("I couldn't understand your request. Please try again.")


# Check system condition
def condition():
    usage = psutil.cpu_percent()
    battery = psutil.sensors_battery()
    speak(f"CPU usage is at {usage} percent.")
    if battery:
        speak(f"Battery is at {battery.percent} percent.")
        if battery.percent < 40:
            speak("Please connect the system to a charging point.")

# Main script
if __name__ == "__main__":
    speak("Hello! I am Jarvis. Say 'Start Jarvis' to activate me.")  # Greet the user

    while True:
        query = command()

        if "start jarvis" in query:
            speak("Starting Jarvis.")
            wishMe()  # Greet the user when starting Jarvis
            break  # Start assistant loop after greeting

   # Main loop for Jarvis commands
while True:
    query = command()

    if "shutdown jarvis" in query:
        speak("Shutting down Jarvis.")
        sys.exit()  # Gracefully shut down the script

    elif query == "none":
        continue

    # Explicitly handle Google commands first
    elif "google" in query:
        google(query)

    # Handle YouTube commands specifically
    elif "open youtube" in query or "youtube" in query:
        youtube(query)

    # Execute social media related commands
    elif any(platform in query for platform in ['facebook', 'whatsapp', 'discord', 'instagram']):
        if 'close' in query:
            close_social_media(query)
        else:
            social_media(query)

    # Schedule related commands
    elif "schedule" in query:
        schedule()

    # Open or close system applications
    elif "open" in query:
        openApp(query)
    elif "close" in query:
        closeApp(query)

    # System condition check
    elif "system condition" in query:
        condition()

    # Exit command
    elif query in ["exit", "quit"]:
        speak("Goodbye!")
        sys.exit()

    # Process user input with ML model for generic queries
    else:
        sequences = pad_sequences(tokenizer.texts_to_sequences([query]), maxlen=20, truncating='post')
        result = model.predict(sequences)
        tag = label_encoder.inverse_transform([np.argmax(result)])[0]
        for intent in data['intents']:
            if intent['tag'] == tag:
                speak(np.random.choice(intent['responses']))
