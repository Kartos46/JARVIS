import datetime
import os
import sys
import time
import webbrowser
import pyttsx3
import speech_recognition as sr
import json
import pickle
import numpy as np
import psutil
import pyautogui
import pygetwindow as gw
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
import subprocess

class JarvisAssistant:
    def __init__(self):
        self.active_tab = None
        self.mode = "voice"
        self.data, self.model, self.tokenizer, self.label_encoder = self.load_resources()
        self.engine = self.initialize_engine()
        self.chrome_path = self.get_chrome_path()
        self.current_search = None
        self.in_video = False
        
        # System applications with their executable paths
        self.system_apps = {
            "photos": "ms-photos:",
            "file manager": "explorer",
            "vs code": "code",
            "visual studio code": "code",
            "paint": "mspaint",
            "calculator": "calc",
            "task manager": "taskmgr",
            "clock": "timedate.cpl",
            "notepad": "notepad"
        }
        
        # Special process names for closing system apps
        self.system_processes = {
            "task manager": "Taskmgr.exe",
            "file manager": "explorer.exe",
            "clock": "ShellExperienceHost.exe"
        }
        
        # Social media platforms with their URLs
        self.social_media = {
            "instagram": "https://www.instagram.com/",
            "facebook": "https://www.facebook.com/",
            "linkedin": "https://www.linkedin.com/",
            "github": "https://www.github.com/",
            "whatsapp": "https://web.whatsapp.com/",
            "twitter": "https://twitter.com/",
            "discord": "https://discord.com/"
        }

    def get_chrome_path(self):
        """Get the path to Google Chrome executable"""
        chrome_paths = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe")
        ]
        
        for path in chrome_paths:
            if os.path.exists(path):
                return path
        
        self.speak("Warning: Google Chrome not found. Using default browser instead.")
        return None

    def open_in_chrome(self, url):
        """Open a URL specifically in Google Chrome"""
        try:
            if self.chrome_path:
                subprocess.Popen([self.chrome_path, url])
            else:
                webbrowser.open(url, new=2)
            return True
        except Exception as e:
            self.speak(f"Sorry, I couldn't open the browser. Error: {str(e)}")
            return False

    def load_resources(self):
        """Load all necessary ML resources with error handling"""
        try:
            with open("intents.json") as file:
                data = json.load(file)
            
            model = load_model("chat_model.h5")
            
            with open("tokenizer.pkl", "rb") as f:
                tokenizer = pickle.load(f)
                
            with open("label_encoder.pkl", "rb") as f:
                label_encoder = pickle.load(f)
                
            return data, model, tokenizer, label_encoder
            
        except Exception as e:
            self.speak(f"Error loading resources: {str(e)}")
            sys.exit(1)

    def initialize_engine(self):
        """Initialize text-to-speech engine"""
        engine = pyttsx3.init("sapi5")
        voices = engine.getProperty('voices')
        
        for voice in voices:
            if 'male' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
                
        engine.setProperty('rate', engine.getProperty('rate') - 50)
        engine.setProperty('volume', min(engine.getProperty('volume') + 0.25, 1.0))
        return engine

    def speak(self, text):
        """Convert text to speech"""
        self.engine.say(text)
        self.engine.runAndWait()

    def command(self):
        """Get user command via voice or text"""
        if self.mode == "text":
            query = input("Enter your command: ").strip().lower()
            return query if query else "none"

        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("Listening...", end="", flush=True)
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print("Recognizing...")
                query = recognizer.recognize_google(audio, language='en-in')
                print(f"User said: {query}\n")
            except sr.UnknownValueError:
                self.speak("Sorry, I didn't catch that. Could you repeat?")
                return "none"
            except Exception as e:
                print(f"Error: {e}")
                self.speak("There was an error processing your request.")
                return "none"
        return query.lower()

    def get_day(self):
        """Get current day of week"""
        return datetime.datetime.today().strftime("%A")

    def wish_me(self):
        """Greet user based on time of day"""
        hour = datetime.datetime.now().hour
        current_time = time.strftime("%I:%M %p")
        day = self.get_day()

        if 0 <= hour < 12:
            self.speak(f"Good morning Kartik, it's {day} and the time is {current_time}.")
        elif 12 <= hour < 16:
            self.speak(f"Good afternoon Kartik, it's {day} and the time is {current_time}.")
        else:
            self.speak(f"Good evening Kartik, it's {day} and the time is {current_time}.")

    def open_application(self, app_name):
        """Open system applications"""
        app_name = app_name.lower()
        if app_name in self.system_apps:
            try:
                self.speak(f"Opening {app_name}")
                os.system(f"start {self.system_apps[app_name]}")
                return True
            except Exception as e:
                self.speak(f"Sorry, I couldn't open {app_name}. Error: {str(e)}")
                return False
        else:
            self.speak(f"I don't know how to open {app_name}")
            return False

    def close_application(self, app_name):
        """Close system applications with improved handling"""
        app_name = app_name.lower()
        
        # Special handling for File Explorer to prevent white screen
        if app_name == "file manager":
            try:
                # This safely restarts Explorer instead of killing it
                os.system("taskkill /f /im explorer.exe")
                time.sleep(1)  # Wait a second
                os.system("start explorer.exe")
                self.speak("File Manager closed and restarted safely")
                return True
            except Exception as e:
                self.speak(f"Couldn't properly close File Manager. Error: {str(e)}")
                return False
        
        # Special handling for other system applications
        if app_name in self.system_processes:
            try:
                os.system(f"taskkill /f /im {self.system_processes[app_name]}")
                self.speak(f"Closed {app_name}")
                return True
            except Exception as e:
                self.speak(f"Couldn't close {app_name}. Error: {str(e)}")
                return False
        
        # Default handling for other applications
        for proc in psutil.process_iter(['name', 'pid']):
            if app_name in proc.info['name'].lower():
                try:
                    proc.terminate()
                    self.speak(f"Closed {app_name}")
                    return True
                except Exception as e:
                    self.speak(f"Couldn't close {app_name}. Error: {str(e)}")
                    return False
        
        try:
            for window in gw.getWindowsWithTitle(app_name.capitalize()):
                window.close()
                self.speak(f"Closed {app_name}")
                return True
        except:
            pass
        
        self.speak(f"Couldn't find {app_name} to close")
        return False

    # Social Media Handling
    def open_social_media(self, platform):
        """Open social media platforms in Chrome"""
        platform = platform.lower()
        if platform in self.social_media:
            self.speak(f"Opening {platform} in Chrome")
            return self.open_in_chrome(self.social_media[platform])
        else:
            self.speak(f"I don't know how to open {platform}")
            return False

    def close_social_media(self, platform):
        """Close social media browser tabs precisely"""
        platform = platform.lower()
        if platform in self.social_media:
            try:
                # Try to close by window title first
                closed = False
                for window in gw.getWindowsWithTitle(platform.capitalize()):
                    if platform in window.title.lower():
                        window.close()
                        closed = True
                
                if not closed and self.chrome_path:
                    # Use Chrome's command line to close specific tab
                    subprocess.run([
                        self.chrome_path,
                        "--remote-debugging-port=9222",
                        f"--close-tab-with-url={self.social_media[platform]}"
                    ], timeout=5)
                    closed = True
                
                if closed:
                    self.speak(f"Closed {platform}")
                else:
                    self.speak(f"Couldn't find {platform} tab to close")
                return closed
                
            except Exception as e:
                self.speak(f"Couldn't close {platform}. Error: {str(e)}")
                return False
        else:
            self.speak(f"I don't know how to close {platform}")
            return False

    def handle_scroll(self, direction):
        """Handle scrolling up or down"""
        if direction == "up":
            self.speak("Scrolling up")
            pyautogui.scroll(300)  # Positive number scrolls up
        elif direction == "down":
            self.speak("Scrolling down")
            pyautogui.scroll(-300)  # Negative number scrolls down
        else:
            self.speak("I didn't understand the scroll direction")

    def handle_youtube(self, query):
        """Enhanced YouTube handling with video navigation"""
        if "open youtube" in query:
            self.speak("What would you like to search on YouTube?")
            search_query = self.command()
            
            if search_query and search_query.lower() != "none":
                self.speak(f"Searching YouTube for {search_query}.")
                url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
                self.current_search = search_query  # Store current search
            else:
                self.speak("Opening YouTube homepage.")
                url = "https://www.youtube.com/"
                self.current_search = None
                
            self.open_in_chrome(url)
            self.active_tab = "youtube"
            self.in_video = False  # Track if we're in a video
            
        elif "close youtube" in query or "close video" in query:
            if self.in_video:
                # Go back to search results
                pyautogui.hotkey('alt', 'left')  # Browser back
                self.speak("Returned to search results")
                self.in_video = False
            else:
                if "tab" in query:
                    self.speak("Closing current YouTube tab.")
                    pyautogui.hotkey('ctrl', 'w')
                else:
                    self.speak("Closing YouTube completely.")
                    self.close_browser_tabs('youtube')
                self.active_tab = None
                self.current_search = None
            
        elif self.active_tab == "youtube":
            if 'scroll up' in query:
                self.handle_scroll("up")
            elif 'scroll down' in query:
                self.handle_scroll("down")
            elif 'play video' in query or 'open video' in query:
                try:
                    if 'video' in query:
                        # Extract video name/number from query
                        if any(word.isdigit() for word in query.split()):
                            # If number specified (e.g., "play video 3")
                            video_num = int([w for w in query.split() if w.isdigit()][0])
                            self.speak(f"Opening video number {video_num}")
                            pyautogui.click(x=500, y=200 + (video_num-1)*200)
                        else:
                            # If name specified (e.g., "play video tutorial")
                            video_name = query.split('video')[-1].strip()
                            self.speak(f"Searching for {video_name}")
                            pyautogui.hotkey('ctrl', 'f')
                            time.sleep(0.5)
                            pyautogui.write(video_name)
                            time.sleep(1)
                            pyautogui.press('enter')
                            time.sleep(1)
                            pyautogui.click(x=500, y=200)  # Click first result
                    else:
                        # Default to first video
                        self.speak("Opening first video")
                        pyautogui.click(x=500, y=200)
                    
                    self.in_video = True
                except Exception as e:
                    self.speak(f"Couldn't open video. Error: {str(e)}")
            elif 'back to search' in query and self.in_video:
                pyautogui.hotkey('alt', 'left')
                self.speak("Returned to search results")
                self.in_video = False
            elif 'search again' in query and self.current_search:
                self.speak(f"Searching again for {self.current_search}")
                url = f"https://www.youtube.com/results?search_query={self.current_search.replace(' ', '+')}"
                self.open_in_chrome(url)

    def handle_google(self, query):
        """Handle all Google related commands in Chrome"""
        if "open google" in query or "search google" in query:
            search_query = self.extract_search_query(query, "google")
            
            if search_query:
                self.speak(f"Searching Google for {search_query}.")
                url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
            else:
                self.speak("Opening Google homepage.")
                url = "https://www.google.com/"
                
            self.open_in_chrome(url)
            self.active_tab = "google"
            
        elif "close google" in query:
            if "tab" in query:
                self.speak("Closing current Google tab.")
                pyautogui.hotkey('ctrl', 'w')
            else:
                self.speak("Closing Google Chrome completely.")
                self.close_chrome()
            self.active_tab = None
            
        elif self.active_tab == "google":
            if 'scroll up' in query:
                self.handle_scroll("up")
            elif 'scroll down' in query:
                self.handle_scroll("down")

    def close_chrome(self):
        """Close Google Chrome completely"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                    try:
                        proc.terminate()
                    except:
                        continue
            return True
        except Exception as e:
            self.speak(f"Couldn't close Chrome. Error: {str(e)}")
            return False

    def close_browser_tabs(self, service):
        """Close browser tabs for specific service"""
        try:
            for window in gw.getWindowsWithTitle(service.capitalize()):
                window.close()
            return True
        except Exception as e:
            self.speak(f"Error closing {service}: {str(e)}")
            return False

    def extract_search_query(self, query, service):
        """Extract search query from command"""
        if "search" in query:
            search_query = query.replace(f"search {service} for", "").replace(f"search {service}", "").strip()
            if not search_query:
                self.speak(f"What should I search on {service.capitalize()}?")
                search_query = self.command()
            return search_query if search_query.lower() != "none" else None
        return None

    def handle_system_commands(self, query):
        """Handle system application commands"""
        if "open" in query:
            for app in self.system_apps:
                if app in query:
                    self.open_application(app)
                    return True
                    
        elif "close" in query:
            for app in self.system_apps:
                if app in query:
                    self.close_application(app)
                    return True
                    
        return False

    def handle_social_media_commands(self, query):
        """Handle social media commands"""
        if "open" in query:
            for platform in self.social_media:
                if platform in query:
                    self.open_social_media(platform)
                    return True
                    
        elif "close" in query:
            for platform in self.social_media:
                if platform in query:
                    self.close_social_media(platform)
                    return True
                    
        return False

    def get_ml_response(self, query):
        """Get response from ML model"""
        sequences = pad_sequences(
            self.tokenizer.texts_to_sequences([query]),
            maxlen=20,
            truncating='post'
        )
        result = self.model.predict(sequences)
        tag = self.label_encoder.inverse_transform([np.argmax(result)])[0]
        
        for intent in self.data['intents']:
            if intent['tag'] == tag:
                return np.random.choice(intent['responses'])
                
        return "I'm not sure how to respond to that."

    def run(self):
        """Main execution loop"""
        self.speak("Hello! I am Jarvis. Do you want to use voice or text commands?")
        self.mode = input("Enter 'voice' or 'text': ").strip().lower()
        
        if self.mode not in ["voice", "text"]:
            self.mode = "voice"

        self.speak("Say 'Start Jarvis' or type 'start jarvis' to begin.")

        while True:
            query = self.command()

            if "start jarvis" in query:
                self.speak("Initializing systems.")
                self.wish_me()
                break

        # Main command loop
        while True:
            query = self.command()

            if not query or query == "none":
                continue
                
            if "shutdown jarvis" in query or "exit" in query or "quit" in query:
                self.speak("Shutting down systems. Goodbye!")
                sys.exit()

            # Handle system applications
            if self.handle_system_commands(query):
                continue
                
            # Handle social media
            if self.handle_social_media_commands(query):
                continue
                
            # Handle YouTube
            if "youtube" in query:
                self.handle_youtube(query)
                continue
                
            # Handle Google
            if "google" in query:
                self.handle_google(query)
                continue
                
            # Handle scroll commands
            if 'scroll up' in query:
                self.handle_scroll("up")
                continue
            elif 'scroll down' in query:
                self.handle_scroll("down")
                continue
                
            # Default ML response
            response = self.get_ml_response(query)
            self.speak(response)

if __name__ == "__main__":
    assistant = JarvisAssistant()
    assistant.run()
