import os
import struct
import json
import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import pvporcupine
import pyaudio
from dotenv import load_dotenv
import pyautogui
import keyboard
import time
import requests
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import threading
from history import HistoryManager
from youtube_play_module_for_jarvis import play_youtube
import whatsapp_client
import email_client

# Try to import Ollama
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("⚠️  Ollama not installed. Offline LLM will be unavailable.")

# Try to import Vosk (offline STT)
try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    print("⚠️  Vosk not installed. Offline STT will be unavailable.")
    print("   Install with: pip install vosk")

# Load .env for API Keys
# Load .env for API Keys
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
PORCUPINE_ACCESS_KEY = os.getenv("PORCUPINE_ACCESS_KEY")

# Fallback for Porcupine if not in env (but warn user)
if not PORCUPINE_ACCESS_KEY:
    PORCUPINE_ACCESS_KEY = "Yw10NNPz7WeUo4E2eOnihbALHfRfsY2ry7R9xuhnzw4PVcRl1WZUpg=="  # Default invalid key

# Validate API keys
if not GOOGLE_API_KEY:
    print("⚠️  WARNING: GOOGLE_API_KEY not found in .env file!")
    print("   Please create a .env file with your API keys.")
    print("   See .env.example for reference.")

# Configure Gemini
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")
except Exception as e:
    print(f"❌ Error configuring Gemini: {e}")
    model = None

# Text-to-speech setup
try:
    engine = pyttsx3.init()
    speech_rate = int(os.getenv("SPEECH_RATE", "180"))
    engine.setProperty('rate', speech_rate)
    
    # Try to set voice type (0=male, 1=female)
    voices = engine.getProperty('voices')
    voice_id = int(os.getenv("TTS_VOICE", "0"))
    if voices and voice_id < len(voices):
        engine.setProperty('voice', voices[voice_id].id)
except Exception as e:
    print(f"❌ Error initializing TTS: {e}")
    engine = None

def speak(text):
    """Text-to-speech function with error handling"""
    print(f"🗣️ Jarvis: {text}")
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"❌ TTS Error: {e}")
    else:
        print("⚠️  TTS engine not available")

# Control Volume
def change_volume(action):
    """Control system volume with error handling"""
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))

        if action == "up":
            volume.VolumeStepUp(None)
        elif action == "down":
            volume.VolumeStepDown(None)
        elif action == "mute":
            volume.SetMute(1, None)
        elif action == "unmute":
            volume.SetMute(0, None)
    except Exception as e:
        print(f"❌ Volume control error: {e}")
        speak("Sorry, I couldn't change the volume.")

# Take Screenshot
def take_screenshot():
    """Take and save a screenshot"""
    try:
        # Create screenshots directory in Pictures if it doesn't exist
        screenshot_dir = os.path.join(os.path.expanduser("~"), "Screenshots")
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
        
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        screenshot_path = os.path.join(screenshot_dir, f"screenshot_{timestamp}.png")
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        speak(f"Screenshot taken and saved to {screenshot_path}!")
        return screenshot_path
    except Exception as e:
        print(f"❌ Screenshot error: {e}")
        speak("Sorry, I couldn't take a screenshot.")
        return None

# Lock Screen
def lock_screen():
    os.system("rundll32.exe user32.dll,LockWorkStation")
    speak("Locking your computer.")

# Media Play/Pause
def media_control(action):
    """Control media playback"""
    try:
        if action == "play_pause":
            keyboard.send('play/pause media')
        elif action == "next":
            keyboard.send('next track media')
        elif action == "previous":
            keyboard.send('previous track media')
    except Exception as e:
        print(f"❌ Media control error: {e}")
        speak("Sorry, I couldn't control the media.")

# Search and Open App
def search_and_open_app(app_name):
    try:
        keyboard.press('windows')
        keyboard.release('windows')
        time.sleep(1)
        pyautogui.typewrite(app_name, interval=0.1)
        time.sleep(1)
        keyboard.press('enter')
        keyboard.release('enter')
        speak(f"Opening {app_name}.")
    except Exception as e:
        print("❌ Error opening app:", e)
        speak(f"Sorry, I couldn't open {app_name}.")

# Speech recognition setup
recognizer = sr.Recognizer()

# Vosk offline STT setup
vosk_model = None
vosk_recognizer = None

def initialize_vosk():
    """Initialize Vosk offline speech recognition model"""
    global vosk_model, vosk_recognizer
    
    if not VOSK_AVAILABLE:
        return False
    
    try:
        # Get model path from environment variable or use default
        model_path = os.getenv("VOSK_MODEL_PATH", "vosk-model-en-us-0.22")
        
        # Check if model exists
        if not os.path.exists(model_path):
            print(f"⚠️  Vosk model not found at: {model_path}")
            print(f"   Please download a model from: https://alphacephei.com/vosk/models")
            print(f"   Set VOSK_MODEL_PATH in .env to point to the model directory")
            return False
        
        vosk_model = Model(model_path)
        vosk_recognizer = KaldiRecognizer(vosk_model, 16000)
        print("✅ Vosk offline STT initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Error initializing Vosk: {e}")
        return False

class InternetMonitor:
    """Monitors internet connection in the background"""
    def __init__(self, interval=30):
        self.interval = interval
        self.is_online = False
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        # Initial check (blocking but fast)
        self.check_connection()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)

    def _monitor_loop(self):
        while self.running:
            self.check_connection()
            time.sleep(self.interval)

    def check_connection(self):
        try:
            requests.get("https://www.google.com", timeout=3)
            if not self.is_online:
                print("\n🌐 Internet connection restored.")
                self.is_online = True
        except:
            if self.is_online:
                print("\n📴 Internet connection lost.")
                self.is_online = False

# Global internet monitor
internet_monitor = InternetMonitor()

# Initialize History Manager
history_manager = HistoryManager()

def listen_online(audio_data, timeout=5, phrase_time_limit=10):
    """Online speech recognition using Google Speech Recognition"""
    try:
        # Improved recognition for Indian English context
        query = recognizer.recognize_google(audio_data, language="en-IN")
        print(f"👤 You (Online): {query}")
        return query
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that. Could you repeat?")
        return None
    except sr.RequestError as e:
        print(f"❌ Online recognition error: {e}")
        return None

def listen_offline_vosk_stream(timeout=5, phrase_time_limit=10):
    """Offline speech recognition using Vosk with direct microphone stream"""
    if not VOSK_AVAILABLE or not vosk_recognizer:
        return None
    
    try:
        # Vosk requires 16kHz mono PCM audio
        CHUNK = 4096
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        
        pa = pyaudio.PyAudio()
        stream = pa.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        vosk_recognizer.SetWords(True)
        print("🎤 Listening with Vosk (Offline)...")
        
        result_text = ""
        start_time = time.time()
        
        while True:
            # Check timeout
            if time.time() - start_time > timeout:
                break
            
            # Read audio chunk
            data = stream.read(CHUNK, exception_on_overflow=False)
            
            # Process with Vosk
            if vosk_recognizer.AcceptWaveform(data):
                result = json.loads(vosk_recognizer.Result())
                if 'text' in result and result['text']:
                    result_text = result['text']
                    # If we got a result and enough time has passed, stop
                    if time.time() - start_time > 1.0:  # At least 1 second of audio
                        break
        
        # Get final result
        final_result = json.loads(vosk_recognizer.FinalResult())
        if 'text' in final_result and final_result['text']:
            if result_text:
                result_text += " " + final_result['text']
            else:
                result_text = final_result['text']
        
        stream.stop_stream()
        stream.close()
        pa.terminate()
        
        if result_text.strip():
            print(f"👤 You (Offline): {result_text}")
            return result_text.strip()
        return None
        
    except Exception as e:
        print(f"❌ Vosk recognition error: {e}")
        return None

def listen_offline_vosk(audio_data):
    """Offline speech recognition using Vosk from speech_recognition AudioData"""
    if not VOSK_AVAILABLE or not vosk_recognizer:
        return None
    
    try:
        # Convert AudioData to raw bytes
        # speech_recognition provides audio in different formats
        # We need 16kHz mono PCM for Vosk
        wav_data = audio_data.get_wav_data()
        
        # Skip WAV header (44 bytes) to get raw PCM data
        if len(wav_data) > 44:
            raw_audio = wav_data[44:]
            
            vosk_recognizer.SetWords(True)
            
            # Process audio in chunks
            chunk_size = 4000
            result_text = ""
            
            for i in range(0, len(raw_audio), chunk_size):
                chunk = raw_audio[i:i + chunk_size]
                if vosk_recognizer.AcceptWaveform(chunk):
                    result = json.loads(vosk_recognizer.Result())
                    if 'text' in result and result['text']:
                        result_text = result['text']
            
            # Get final result
            final_result = json.loads(vosk_recognizer.FinalResult())
            if 'text' in final_result and final_result['text']:
                if result_text:
                    result_text += " " + final_result['text']
                else:
                    result_text = final_result['text']
            
            if result_text.strip():
                print(f"👤 You (Offline): {result_text}")
                return result_text.strip()
        
        return None
        
    except Exception as e:
        print(f"❌ Vosk recognition error: {e}")
        return None

def listen(timeout=5, phrase_time_limit=10):
    """Hybrid speech recognition: Online (Google) when available, Offline (Vosk) only when disconnected"""
    # Use the background monitor status
    is_online = internet_monitor.is_online
    
    # CASE 1: OFFLINE - Use Vosk directly
    if not is_online:
        if not vosk_recognizer:
            if not initialize_vosk():
                speak("I am offline and offline speech recognition is not available.")
                return None
        print("📴 Offline mode: Using Vosk (local) STT...")
        return listen_offline_vosk_stream(timeout, phrase_time_limit)
    
    # CASE 2: ONLINE - Use Google Speech Recognition
    try:
        with sr.Microphone() as source:
            # Better ambient noise adjustment
            recognizer.adjust_for_ambient_noise(source, duration=2)
            recognizer.dynamic_energy_threshold = True
            
            print("🌐 Online mode: Using Google Speech Recognition...")
            print("🎧 Listening for your command...")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            
            # Use online recognition
            query = listen_online(audio)
            return query
            
    except sr.WaitTimeoutError:
        print("⏱️  Listening timeout - no speech detected")
        return None
    except Exception as e:
        print(f"❌ Listening error: {e}")
        speak("Sorry, I encountered an error with the microphone.")
        return None

# ✅ Fixed Gemini call with improved error handling
def ask_ollama(prompt):
    """Query local Ollama instance"""
    if not OLLAMA_AVAILABLE:
        return None
        
    try:
        model_name = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
        response = ollama.chat(model=model_name, messages=[
            {
                'role': 'user',
                'content': f"You are Maxi, an assistant like Siri. Be extremely concise. Answer in one short direct sentence. User: {prompt}",
            },
        ])
        return response['message']['content']
    except Exception as e:
        print(f"❌ Ollama Error: {e}")
        return None

def ask_ai(prompt):
    """Query AI (Gemini Online -> Ollama only IF offline)"""
    
    # 1. Try Gemini if Online
    if internet_monitor.is_online and model:
        try:
            # Extremely concise prompt for Siri-like behavior
            enhanced_prompt = f"""You are Maxi, a helpful voice assistant like Siri. 
Be extremely concise and direct. Answer the user's question in one single, short sentence.
User question: {prompt}"""
            
            response = model.generate_content(
                [enhanced_prompt],
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=60, # Further reduced for conciseness
                    temperature=0.7
                )
            )
            return response.text.strip()
        except Exception as e:
            print(f"❌ Gemini Error: {e}")
            return "Sorry, I'm having trouble connecting to my brain right now."
    
    # 2. Try Ollama (ONLY if Offline)
    if not internet_monitor.is_online:
        print("🔄 Running in offline mode (Ollama)...")
        response = ask_ollama(prompt)
        if response:
            return response
        return "I am offline and my local brain is not available."
        
    # 3. Fallback
    return "Sorry, I couldn't get a response from the AI."

def generate_email_body(subject):
    """Generates a professional email body using Gemini based on a subject."""
    if not internet_monitor.is_online or not model:
        return "Offline: Could not generate email body."
    
    try:
        prompt = f"Write a professional and concise email body for the subject: '{subject}'. Do not include the subject line or headers, just the body text."
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"❌ Gemini Email Error: {e}")
        return f"Could not generate email body for '{subject}'."

def execute_command(command):
    """Executes a single command and returns (success, response_text)"""
    command_lower = command.lower()
    
    # NLP Pre-processing: Remove common conversational prefixes
    # This allows "I want to open youtube" or "Can you play music" to work
    prefixes = [
        "i want to ", "can you ", "please ", "could you ", "maxi ", "hey maxi ", 
        "just ", "asking to ", "would you "
    ]
    
    cleaned_command = command_lower
    for prefix in prefixes:
        if cleaned_command.startswith(prefix):
            cleaned_command = cleaned_command.replace(prefix, "", 1).strip()
    
    # Use cleaned_command for matching, but keep original if needed? 
    # Actually, replacing command_lower with cleaned_command is generally safe for these commands.
    command_lower = cleaned_command
    
    response_text = ""
    executed = False

    if "open youtube" in command_lower:
        response_text = "Opening YouTube."
        speak(response_text)
        os.system("start chrome https://www.youtube.com")
        executed = True

    elif "open google" in command_lower:
        response_text = "Opening Google."
        speak(response_text)
        os.system("start chrome https://www.google.com")
        executed = True

    elif "shutdown" in command_lower:
        response_text = "Shutting down your PC."
        speak(response_text)
        os.system("shutdown /s /t 1")
        executed = True

    elif "open" in command_lower or "launch" in command_lower:
        app_name = command_lower.replace("open", "").replace("launch", "").strip()
        response_text = f"Opening {app_name}."
        search_and_open_app(app_name)
        executed = True

    elif "increase volume" in command_lower:
        change_volume("up")
        response_text = "Increasing volume."
        speak(response_text)
        executed = True

    elif "decrease volume" in command_lower:
        change_volume("down")
        response_text = "Decreasing volume."
        speak(response_text)
        executed = True

    elif "mute volume" in command_lower or "mute" in command_lower:
        change_volume("mute")
        response_text = "Volume muted."
        speak(response_text)
        executed = True

    elif "unmute volume" in command_lower or "unmute" in command_lower:
        change_volume("unmute")
        response_text = "Volume unmuted."
        speak(response_text)
        executed = True

    elif "take screenshot" in command_lower or "screenshot" in command_lower:
        path = take_screenshot()
        response_text = f"Screenshot taken and saved to {path}." if path else "Sorry, I couldn't take a screenshot."
        executed = True

    elif "lock screen" in command_lower or "lock computer" in command_lower:
        lock_screen()
        response_text = "Locking your computer."
        executed = True

    elif "pause music" in command_lower or "play music" in command_lower or command_lower == "pause" or command_lower == "play":
        media_control("play_pause")
        response_text = "Media play/pause toggled."
        speak(response_text)
        executed = True
        
    elif "next song" in command_lower or "next track" in command_lower:
        media_control("next")
        response_text = "Skipping to next track."
        speak(response_text)
        executed = True
        
    elif "previous song" in command_lower or "previous track" in command_lower:
        media_control("previous")
        response_text = "Playing previous track."
        speak(response_text)
        executed = True
        
    # YouTube Play Integration
    elif command_lower.startswith("play "):
        query = command_lower.replace("play ", "", 1).strip()
        
        # Clean up "in/on youtube" from the query if user matched specific pattern
        for suffix in [" on youtube", " in youtube", " from youtube"]:
            if query.endswith(suffix):
                query = query.replace(suffix, "").strip()
                
        if query and query != "music":
            response_text = f"Searching YouTube for {query}..."
            speak(response_text)
            
            # Run search
            result = play_youtube(query)
            if result['status'] == 'success':
                response_text = f"Playing {result['title']} on YouTube."
                speak(f"Playing {result['title']}.") 
            else:
                response_text = "Sorry, I couldn't find that video."
                speak(response_text)
            executed = True

    # Handle "YouTube and play..." or "Play ... on YouTube"
    elif "youtube" in command_lower and "play" in command_lower:
        # Improved cleanup
        query = command_lower.replace("youtube", "").replace("play", "").replace(" and ", " ").replace(" on ", " ").replace(" in ", " ").strip()
        
        # Also strip prefixes if they were part of the original replacement logic but leaked through?
        # The top-level prefix stripper should handle "i want to", so we don't need to re-do it here usually.
        
        if query:
            response_text = f"Searching YouTube for {query}..."
            speak(response_text)
            
            # Run search
            result = play_youtube(query)
            if result['status'] == 'success':
                response_text = f"Playing {result['title']} on YouTube."
                speak(f"Playing {result['title']}.")
            else:
                response_text = "Sorry, I couldn't find that video."
                speak(response_text)
            executed = True

    # WhatsApp Integration
    elif "whatsapp" in command_lower and ("send" in command_lower or " to " in command_lower or "message" in command_lower):
        try:
            # Defined contacts (name -> number mapping)
            # Users can add their own contacts here
            CONTACTS = {
                "mom": "+910000000000",  # Placeholder
                "dad": "+910000000000",  # Placeholder
                "friend": "+910000000000" # Placeholder
            }
            
            recipient = ""
            message = ""
            
            # Pattern 1: "send whatsapp to [recipient] saying [message]" (Legacy)
            if "send whatsapp to" in command_lower:
                parts = command_lower.replace("send whatsapp to", "").strip()
                if "saying" in parts:
                    recipient_part, message_part = parts.split("saying", 1)
                elif "message" in parts:
                    recipient_part, message_part = parts.split("message", 1)
                else:
                    recipient_part, message_part = parts, "" # weird case
                
                recipient = recipient_part.strip()
                message = message_part.strip()
                
            # Pattern 2: "send [message] to [recipient] on/in whatsapp"
            # e.g. "send hi to mom in whatsapp"
            elif " to " in command_lower and (" in whatsapp" in command_lower or " on whatsapp" in command_lower):
                # Remove "send " and " in/on whatsapp"
                cleaned = command_lower.replace("send ", "", 1).replace(" in whatsapp", "").replace(" on whatsapp", "")
                
                # Split by " to "
                # "hi to mom" -> ["hi", "mom"]
                if " to " in cleaned:
                    message_part, recipient_part = cleaned.rsplit(" to ", 1) # use rsplit to split at the last "to"
                    recipient = recipient_part.strip()
                    message = message_part.strip()
            
            # Resolve recipient from contacts
            if recipient in CONTACTS:
                recipient_number = CONTACTS[recipient]
                print(f"👤 Contact found: {recipient} -> {recipient_number}")
                recipient = recipient_number
            else:
                # If not in contacts, check if it looks like a number
                # If it's a number (mostly digits), clean it.
                # If it's a name (mostly letters), keep it as is for UI search.
                
                clean_check = recipient.replace(" ", "").replace("+", "")
                if clean_check.isdigit() and len(clean_check) >= 10:
                     # It's a number
                     recipient = recipient.replace(" ", "")
                     if not recipient.startswith("+"):
                        recipient = "+91" + recipient
                else:
                    # It's likely a name (e.g., "Chetan")
                    # Pass it as is to whatsapp_client which now handles names via UI search
                    print(f"👤 Unknown contact '{recipient}', strictly passing to WhatsApp search...")
                    pass
            
            if recipient and message:
                # Check for placeholders
                if recipient == "+910000000000":
                    speak(f"I don't have a number for {recipient_part} yet. Please update the contacts list in the code.")
                else:
                    speak(f"Sending WhatsApp message to {recipient}")
                    success = whatsapp_client.send_whatsapp_message(recipient, message)
                    if success:
                        response_text = "Message sent successfully."
                        speak(response_text)
                    else:
                        response_text = "Failed to send WhatsApp message."
                        speak(response_text)
            else:
                speak("I couldn't understand who to send the message to or what the message is.")
                
        except Exception as e:
            print(f"❌ WhatsApp Command Error: {e}")
            speak("Sorry, I encountered an error with WhatsApp.")
        executed = True

    # Email Integration
    elif "email" in command_lower and ("send" in command_lower or " to " in command_lower):
        try:
            # Pattern: "send an email to [email] with subject [subject]"
            # Pattern: "email [email] about [subject]"
            
            recipient_email = ""
            subject = "No Subject"
            
            if " to " in command_lower:
                parts = command_lower.split(" to ", 1)[1].strip()
                if " with subject " in parts:
                    recipient_email, subject = parts.split(" with subject ", 1)
                elif " about " in parts:
                    recipient_email, subject = parts.split(" about ", 1)
                else:
                    recipient_email = parts
            
            # Basic email validation (very simple)
            recipient_email = recipient_email.strip().replace(" ", "")
            if "@" not in recipient_email or "." not in recipient_email:
                speak(f"I'm sorry, '{recipient_email}' doesn't look like a valid email address.")
            else:
                speak(f"Generating content for email to {recipient_email} regarding {subject}...")
                
                # Generate body using Gemini
                body = generate_email_body(subject)
                
                speak(f"Sending email now.")
                success, msg = email_client.send_email(recipient_email, subject, body)
                
                if success:
                    response_text = f"Email sent to {recipient_email}."
                    speak(response_text)
                else:
                    response_text = f"Failed to send email: {msg}"
                    speak(response_text)
                    
        except Exception as e:
            print(f"❌ Email Command Error: {e}")
            speak("Sorry, I encountered an error while trying to send the email.")
        executed = True

    return executed, response_text

def run_maxi():
    utterance = listen()
    if utterance:
        utterance_lower = utterance.lower()
        
        # Smart Split Logic
        # We split by " and " but we want to avoid splitting things like "rock and roll"
        # Heuristic: split if the word after "and" is a command starter
        
        potential_commands = utterance_lower.split(" and ")
        final_commands = []
        
        # Command starters (verbs/keywords) that likely start a new independent command
        command_starters = [
            "open", "launch", "shutdown", "increase", "decrease", "mute", "unmute",
            "take", "screenshot", "lock", "pause", "play", "next", "previous", "send"
        ]
        
        if potential_commands:
            current_command = potential_commands[0]
            
            for part in potential_commands[1:]:
                # Check if this part starts with a known command verb
                is_new_command = any(part.strip().startswith(starter) for starter in command_starters)
                
                if is_new_command:
                    final_commands.append(current_command)
                    current_command = part
                else:
                    # It's likely part of the previous command (e.g. "play rock and roll")
                    current_command += " and " + part
            
            final_commands.append(current_command)
        
        # Execute commands
        for cmd in final_commands:
            print(f"🤖 Processing command: {cmd}")
            executed, response = execute_command(cmd)
            
            # If not a recognized local command, and it's solely one command in the list, ask AI
            # If we have multiple commands, we probably shouldn't send partial sentence fragments to AI unless specifically asked?
            # Current logic: if it's not a command, send to AI.
            if not executed:
                # If we have multiple segments and one isn't a command, it might be chat.
                # If the user said "open youtube and tell me a joke", first part executes, second part goes to AI.
                response_text = ask_ai(cmd)
                speak(response_text)
                
            # Log history
            if executed or response: # if executed or we got an AI response
                history_manager.add_entry(cmd, response if not executed else response)

# Wake Word Listener
def wake_word_listener():
    """Listen for wake word using Porcupine with error handling"""
    wake_word = os.getenv("WAKE_WORD", "jarvis").lower()
    
    try:
        porcupine = pvporcupine.create(
            access_key=PORCUPINE_ACCESS_KEY,
            keywords=[wake_word]  # ✅ Configurable wake word
        )
    except Exception as e:
        print(f"❌ Error initializing Porcupine: {e}")
        print("⚠️  Make sure PORCUPINE_ACCESS_KEY is set in .env file")
        return

    try:
        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )

        print(f"🎤 Listening for 'Hey {wake_word.capitalize()}'...")
        print("💡 Press Ctrl+C to stop")

        try:
            while True:
                pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
                pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

                keyword_index = porcupine.process(pcm)
                if keyword_index >= 0:
                    print("🎯 Wake word detected!")
                    speak("Yes, I'm listening...")
                    run_maxi()
        except KeyboardInterrupt:
            print("\n🛑 Stopped by user.")
            speak("Goodbye!")
        finally:
            audio_stream.close()
            pa.terminate()
            porcupine.delete()
    except Exception as e:
        print(f"❌ Error in wake word listener: {e}")
        speak("Sorry, there was an error with the wake word detection.")

# Start the Assistant
if __name__ == "__main__":
    print("=" * 50)
    print("🤖 Jarvis Voice Assistant - Starting...")
    print("=" * 50)
    
    # Validate essential components before starting
    if not GOOGLE_API_KEY:
        print("⚠️  WARNING: GOOGLE_API_KEY not configured!")
        print("   Some features may not work properly.")
        print()
    
    if not engine:
        print("⚠️  WARNING: TTS engine failed to initialize!")
        print("   Voice responses may not work.")
        print()
    
    # Initialize Vosk for offline STT (if available)
    print("📥 Initializing offline speech recognition...")
    if initialize_vosk():
        print("   ✅ Offline STT ready (Vosk)")
    else:
        print("   ⚠️  Offline STT unavailable (install Vosk and download model)")
    
    # Start internet monitor
    print("🌐 Starting background internet monitor...")
    internet_monitor.start()
    
    if internet_monitor.is_online:
        print("   ✅ Internet connection: Available (Online STT enabled)")
    else:
        print("   📴 Internet connection: Not available (Offline STT only)")
    
    print()
    print("✅ Initialization complete. Starting wake word listener...")
    print()
    
    wake_word_listener()
