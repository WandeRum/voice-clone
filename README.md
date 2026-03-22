# Voice Clone

A local voice cloning web app powered by [Coqui XTTS v2](https://huggingface.co/coqui/XTTS-v2). Record a short voice sample, then synthesize any text in that voice — fully offline, no API keys needed.

## Features

- Clone any voice from a 10–20 second audio sample
- Supports 7 languages: English, Chinese (Mandarin), Japanese, Korean, French, German, Spanish
- Simple two-step Gradio web UI
- Runs entirely on your machine

## Requirements

- Python 3.11 (Coqui TTS does not support 3.12+)
- ~2 GB disk space for model weights (downloaded on first run)

## Setup

```bash
python3.11 -m venv voiceclone
voiceclone/bin/pip install -r requirements.txt
```

## Usage

```bash
voiceclone/bin/python app.py
```

Open http://127.0.0.1:7860 in your browser.

1. **Step 1** — Record or upload 10–20 seconds of clear speech to create a voiceprint
2. **Step 2** — Type any text, pick a language, and generate audio in your cloned voice

## Model

[XTTS v2 by Coqui](https://huggingface.co/coqui/XTTS-v2) — open-source multilingual TTS with voice cloning.
