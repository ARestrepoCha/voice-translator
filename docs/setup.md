# Setup Guide — Voice Translator

## Prerequisites

| Tool | Version | Check |
|------|---------|-------|
| Python | 3.11+ | `python --version` |
| .NET SDK | 8.0 LTS | `dotnet --version` |
| VB-Cable | latest | Installed as audio device |

## 1. Install VB-Cable (manual, one-time)

Download and install from https://vb-audio.com/Cable/

After install, you should see **"CABLE Input (VB-Audio Virtual Cable)"** in your audio devices.

## 2. Python microservice

```bash
cd src/VoiceTranslator.Service

# Create virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env and add your DEEPL_API_KEY
```

Get a free DeepL API key at: https://www.deepl.com/pro-api

## 3. .NET application

```bash
cd src/VoiceTranslator.App
dotnet restore
```

## 4. Run the project

**Terminal 1 — Python microservice:**
```bash
cd src/VoiceTranslator.Service
.venv\Scripts\activate
uvicorn main:app --host localhost --port 8000 --reload
```

**Terminal 2 — .NET application:**
```bash
cd src/VoiceTranslator.App
dotnet run
```

## 5. Configure Zoom / Meet / Teams

In your meeting app, set the microphone to:
> **CABLE Output (VB-Audio Virtual Cable)**

The translated audio will be routed through VB-Cable to the meeting.

## Hardware notes

- Whisper runs on **CPU** — model `base` gives ~2-4 sec latency on Intel Iris Xe
- Do NOT use `medium` or `large` Whisper models — too slow on integrated GPU
- DeepL free tier: 500,000 characters/month (~8-10 hours of conversation)

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `DEEPL_API_KEY` not set | Copy `.env.example` to `.env` and add your key |
| VB-Cable not detected | Reinstall VB-Cable and restart the app |
| High latency (>5 sec) | Confirm Whisper model is `base` in `.env` |
| No audio output | Check Windows default audio device settings |
