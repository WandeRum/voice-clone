# Voice Cloning App

Local voice cloning web app using Coqui XTTS v2 and Gradio.

## Setup

Requires Python 3.11 (Coqui TTS does not support 3.12+).

```bash
python3.11 -m venv voiceclone
voiceclone/bin/pip install -r requirements.txt
```

## Running

```bash
voiceclone/bin/python app.py
# Open http://127.0.0.1:7860
```

## Key Dependency Constraints

| Package | Pinned Version | Reason |
|---|---|---|
| `transformers` | `==4.45.0` | 5.x removed `BeamSearchScorer` used by Coqui |
| `torchaudio` | `==2.5.0` | 2.6+ requires `torchcodec` which isn't available |
| Python | `3.11` | Coqui TTS incompatible with 3.12+ |

## Known Quirks

- **`torch.load` patch** — `voice_clone.py` monkey-patches `torch.load` to use `weights_only=False` because PyTorch 2.6 changed the default and Coqui's model classes aren't allowlisted.
- **Coqui TOS** — `COQUI_TOS_AGREED=1` is set in `voice_clone.py` and a `tos_agreed.txt` file exists in `~/Library/Application Support/tts/tts_models--multilingual--multi-dataset--xtts_v2/` to bypass the interactive license prompt.
- **Model download** — First run downloads ~2 GB of XTTS v2 weights to `~/Library/Application Support/tts/`.
- **Model loading** — Happens lazily on first button click, not at startup. Expect a delay.
