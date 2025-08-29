import os
import struct
import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import pvporcupine
import pyaudio
from dotenv import load_dotenv
import pyautogui
import keyboard
import time
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Load .env for Gemini API Key
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-pro")

# Text-to-speech setup
engine = pyttsx3.init()
engine.setProperty('rate', 180)

def speak(text):
    print(f"🗣️ Maxi: {text}")
    engine.say(text)
    engine.runAndWait()

# Control Volume
def change_volume(action):
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

# Take Screenshot
def take_screenshot():
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    screenshot = pyautogui.screenshot()
    screenshot.save(f"screenshot_{timestamp}.png")
    speak("Screenshot taken and saved!")

# Lock Screen
def lock_screen():
    os.system("rundll32.exe user32.dll,LockWorkStation")
    speak("Locking your computer.")

# Media Play/Pause
def media_control(action):
    if action == "play_pause":
        keyboard.press_and_release('play/pause media')

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

def listen():
    with sr.Microphone() as source:
        print("🎧 Listening for your command...")
        audio = recognizer.listen(source)
        try:
            query = recognizer.recognize_google(audio)
            print(f"👤 You: {query}")
            return query
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that.")
            return None
        except sr.RequestError:
            speak("Sorry, I'm having trouble connecting to the recognition service.")
            return None

def ask_gemini(prompt):
    try:
        response = model.generate_content(
            f"Answer briefly in 2-3 sentences: {prompt}",
            generation_config={
                "max_output_tokens": 100
            }
        )
        return response.text.strip()
    except Exception as e:
        print("❌ Gemini Error:", e)
        return "Sorry, something went wrong while thinking."

def run_maxi():
    
    command = listen()
    if command:
        command = command.lower()

        if "open youtube" in command:
            speak("Opening YouTube.")
            os.system("start chrome https://www.youtube.com")

        elif "open google" in command:
            speak("Opening Google.")
            os.system("start chrome https://www.google.com")

        elif "shutdown" in command:
            speak("Shutting down your PC.")
            os.system("shutdown /s /t 1")

        elif "open" in command or "launch" in command:
            app_name = command.replace("open", "").replace("launch", "").strip()
            search_and_open_app(app_name)

        elif "increase volume" in command:
            change_volume("up")
            speak("Increasing volume.")

        elif "decrease volume" in command:
            change_volume("down")
            speak("Decreasing volume.")

        elif "mute volume" in command:
            change_volume("mute")
            speak("Volume muted.")

        elif "take screenshot" in command:
            take_screenshot()

        elif "lock screen" in command or "lock computer" in command:
            lock_screen()

        elif "pause music" in command or "play music" in command:
            media_control("play_pause")

        else:
            response = ask_gemini(command)
            speak(response)

# Wake Word Listener
def wake_word_listener():
    porcupine = pvporcupine.create(
        access_key="Yw10NNPz7WeUo4E2eOnihbALHdRfsY2ry7R9xuhnzw4PVcRl1WZUpg==",  # Your Access Key
        keywords=["jarvis"]  # ✅ Using Jarvis as wake word
    )

    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    print("🎤 Listening for 'Hey Jarvis'...")

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
        print("🛑 Stopped by user.")
    finally:
        audio_stream.close()
        pa.terminate()
        porcupine.delete()

# Start the Assistant
if __name__ == "__main__":
    wake_word_listener()
