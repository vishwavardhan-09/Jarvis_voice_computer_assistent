# 📥 Vosk Offline STT Setup Guide

## Overview
Vosk provides offline speech-to-text capabilities, allowing your voice assistant to work without an internet connection.

## Installation Steps

### 1. Install Vosk
```bash
pip install vosk
```

Or update all dependencies:
```bash
pip install -r requirements.txt
```

### 2. Download a Language Model

Choose and download a model from the [Vosk Models page](https://alphacephei.com/vosk/models):

#### Recommended Models:

**English (Small & Fast - ~40MB):**
- Model: `vosk-model-en-us-0.22`
- Download: https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
- Best for: Quick responses, lower accuracy

**English (Large & Accurate - ~1.8GB):**
- Model: `vosk-model-en-us-0.22-lgraph`
- Download: https://alphacephei.com/vosk/models/vosk-model-en-us-0.22-lgraph.zip
- Best for: Better accuracy, slower initial load

**Other Languages:**
- Spanish: `vosk-model-es-0.42`
- French: `vosk-model-fr-0.22`
- German: `vosk-model-de-0.22`
- And many more at [vosk/models](https://alphacephei.com/vosk/models)

### 3. Extract the Model

1. Download the ZIP file to your project directory
2. Extract it (right-click → Extract All on Windows)
3. You should have a folder like `vosk-model-en-us-0.22/`

### 4. Configure in .env

Add the model path to your `.env` file:

```env
VOSK_MODEL_PATH=vosk-model-en-us-0.22
```

**Important**: Use the folder name, not the ZIP file name!

### 5. Verify Installation

Run the assistant:
```bash
python jarvis.py
```

You should see:
```
📥 Initializing offline speech recognition...
✅ Vosk offline STT initialized successfully
✅ Offline STT ready (Vosk)
```

## How It Works

### Automatic Switching

The assistant automatically detects internet connectivity and switches between:

- **🌐 Online Mode**: Uses Google Speech Recognition (when internet available)
  - More accurate
  - Requires internet
  - Free (limited requests)

- **📴 Offline Mode**: Uses Vosk (when internet unavailable)
  - Works offline
  - No API calls
  - Slightly less accurate
  - Requires downloaded model

### Fallback Mechanism

1. **Internet Available**:
   - Primary: Google Speech Recognition
   - Fallback: Vosk (if Google fails)

2. **No Internet**:
   - Primary: Vosk (offline)
   - Fallback: Error message if Vosk not available

## Troubleshooting

### Model Not Found Error
```
⚠️  Vosk model not found at: vosk-model-en-us-0.22
```

**Solution**:
1. Check the folder exists in your project directory
2. Verify the folder name matches `VOSK_MODEL_PATH` in `.env`
3. Make sure you extracted the ZIP file (don't use the ZIP directly)

### Vosk Not Installed
```
⚠️  Vosk not installed. Offline STT will be unavailable.
```

**Solution**:
```bash
pip install vosk
```

### Poor Recognition Accuracy

**Try**:
1. Download a larger model (e.g., `vosk-model-en-us-0.22-lgraph`)
2. Speak more clearly
3. Reduce background noise
4. Check microphone quality

### Slow Performance

**The first recognition after startup may be slower** - this is normal as Vosk loads the model into memory.

**Tips**:
- Use a smaller model for faster response
- Ensure sufficient RAM available
- Close other memory-intensive applications

## Model Sizes Comparison

| Model | Size | Accuracy | Speed | RAM Usage |
|-------|------|----------|-------|-----------|
| vosk-model-en-us-0.22 | ~40MB | Good | Fast | ~50MB |
| vosk-model-en-us-0.22-lgraph | ~1.8GB | Excellent | Moderate | ~2GB |

## Multiple Languages

To support multiple languages:

1. Download models for each language
2. Create separate folders for each
3. Switch `VOSK_MODEL_PATH` in `.env` as needed

Or implement language detection to auto-switch models based on detected language.

## Advanced: Using Multiple Models

You can modify the code to support multiple models simultaneously or switch based on language preference. See the `initialize_vosk()` function in `jarvis.py` for customization.

## Resources

- **Vosk GitHub**: https://github.com/alphacep/vosk-api
- **Model Downloads**: https://alphacephei.com/vosk/models
- **Documentation**: https://alphacephei.com/vosk/
- **Python Examples**: https://github.com/alphacep/vosk-api/tree/master/python/example

---

**Enjoy offline speech recognition! 🎉**

