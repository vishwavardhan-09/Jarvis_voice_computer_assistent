# 🤖 Maxi Voice Assistant

A personal voice assistant for Windows, similar to Siri or Alexa, designed to increase productivity and efficiency. Maxi responds to voice commands, controls system functions, and uses AI to answer questions naturally.

## ✨ Features

### Core Capabilities
- 🎤 **Wake Word Detection**: Responds to "Hey Jarvis" (configurable)
- 🗣️ **Hybrid Voice Recognition**: 
  - 🌐 **Online**: Google Speech Recognition (when internet available)
  - 📴 **Offline**: Vosk offline STT (when internet unavailable)
  - **Automatic switching** based on internet connectivity
- 🤖 **AI Integration**: Powered by Google Gemini for intelligent responses
- 🔊 **Text-to-Speech**: Natural voice responses using pyttsx3

### System Controls
- 🔊 **Volume Control**: Increase, decrease, mute/unmute system volume
- 📸 **Screenshots**: Take and save screenshots with timestamps
- 🔒 **Screen Lock**: Lock your computer with voice command
- ⏸️ **Media Control**: Play/pause, next/previous track
- 🚀 **App Launching**: Open applications by name
- 🌐 **Web Navigation**: Open YouTube, Google, and other websites

### Future Enhancements
See [IMPROVEMENTS_SUGGESTIONS.md](IMPROVEMENTS_SUGGESTIONS.md) for detailed roadmap.

## 📋 Prerequisites

- **Python 3.8+**
- **Windows 10/11** (some features are Windows-specific)
- **Microphone** for voice input
- **Google Gemini API Key** ([Get one here](https://makersuite.google.com/app/apikey))
- **Porcupine Access Key** ([Get one here](https://console.picovoice.ai/))
- **Vosk Model** (optional, for offline STT - see [VOSK_SETUP.md](VOSK_SETUP.md))

## 🚀 Installation

1. **Clone or download this repository**
   ```bash
   cd maxi-voice-assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Note**: If you encounter issues with `pyaudio`, try:
   ```bash
   pip install pipwin
   pipwin install pyaudio
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root (see `env_template.txt` for reference):
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   PORCUPINE_ACCESS_KEY=your_porcupine_access_key_here
   WAKE_WORD=jarvis
   SPEECH_RATE=180
   TTS_VOICE=0
   VOSK_MODEL_PATH=vosk-model-en-us-0.22
   ```
   
   - `GOOGLE_API_KEY`: Your Google Gemini API key (required)
   - `PORCUPINE_ACCESS_KEY`: Your Porcupine access key for wake word detection (required)
   - `WAKE_WORD`: Custom wake word (default: "jarvis")
   - `SPEECH_RATE`: Speech speed in words per minute (default: 180)
   - `TTS_VOICE`: 0 for male, 1 for female voice (default: 0)
   - `VOSK_MODEL_PATH`: Path to Vosk offline STT model (optional, see [VOSK_SETUP.md](VOSK_SETUP.md))

4. **Set up Vosk for offline STT (Optional but Recommended)**
   
   See [VOSK_SETUP.md](VOSK_SETUP.md) for detailed instructions on:
   - Downloading language models
   - Configuring offline speech recognition
   - Troubleshooting offline STT

## 🎮 Usage

1. **Start the assistant**
   ```bash
   python jarvis.py
   ```

2. **Activate with wake word**
   - Say "Hey Jarvis" (or your configured wake word)
   - Wait for "Yes, I'm listening..."
   - Speak your command

3. **Example Commands**
   - "Open YouTube"
   - "Increase volume"
   - "Take screenshot"
   - "Lock screen"
   - "What's the weather?"
   - "Open Chrome"
   - "Play music" / "Pause music"
   - "Next song"
   - Any general question (answered by AI)

4. **Stop the assistant**
   - Press `Ctrl+C` in the terminal

## 🎯 Supported Commands

### System Commands
- `"open [app name]"` / `"launch [app name]"` - Open an application
- `"open youtube"` / `"open google"` - Open websites
- `"increase volume"` - Turn up volume
- `"decrease volume"` - Turn down volume
- `"mute volume"` / `"mute"` - Mute system
- `"unmute volume"` / `"unmute"` - Unmute system
- `"take screenshot"` / `"screenshot"` - Capture screen
- `"lock screen"` / `"lock computer"` - Lock Windows
- `"shutdown"` - Shut down computer (⚠️ use with caution)

### Media Commands
- `"play music"` / `"pause music"` - Toggle playback
- `"next song"` / `"next track"` - Skip to next track
- `"previous song"` / `"previous track"` - Go to previous track

### AI Queries
- Any natural language question (e.g., "What is AI?", "Tell me a joke")

## 🛠️ Project Structure

```
maxi-voice-assistant/
├── jarvis.py                  # Main assistant code
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── VOSK_SETUP.md             # Vosk offline STT setup guide
├── IMPROVEMENTS_SUGGESTIONS.md # Roadmap and suggestions
├── env_template.txt           # Environment variables template
└── screenshots/               # Directory for saved screenshots (auto-created)
```

## ⚙️ Configuration

All settings are configured via environment variables in the `.env` file. See the Installation section for details.

## 🔒 Security & Privacy

- **API Keys**: Never commit your `.env` file to version control
- **Audio Processing**: Audio is processed locally; only text queries are sent to Google Gemini
- **Privacy**: Consider reviewing what data is sent to external services

## 🐛 Troubleshooting

### Microphone not working
- Check microphone permissions in Windows Settings
- Ensure microphone is not muted or disabled
- Try running as administrator

### Wake word not detected
- Check Porcupine access key is correct
- Ensure microphone is working
- Adjust ambient noise by speaking louder/clearer

### Offline STT not working
- See [VOSK_SETUP.md](VOSK_SETUP.md) for detailed setup instructions
- Verify Vosk model is downloaded and path is correct in `.env`
- Ensure `pip install vosk` completed successfully

### TTS not working
- Check audio output device is connected
- Try changing TTS_VOICE in .env (0 or 1)
- Verify pyttsx3 installation: `pip install pyttsx3`

### API errors
- Verify API keys are correct in `.env`
- Check internet connection (required for Gemini)
- Ensure API keys have sufficient credits/quota

## 📝 License

This project is for educational and personal use.

## 🤝 Contributing

Suggestions and improvements are welcome! See [IMPROVEMENTS_SUGGESTIONS.md](IMPROVEMENTS_SUGGESTIONS.md) for ideas.

## 🙏 Acknowledgments

- **Google Gemini** - AI capabilities
- **Porcupine** - Wake word detection
- **SpeechRecognition** - Voice recognition
- **pyttsx3** - Text-to-speech

---

**Made with ❤️ for productivity and efficiency**

