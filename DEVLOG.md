# Voice Cloning App — Dev Log

## Prototype Status: Working ✅

---

## What Was Built

A local voice cloning web app using:
- **Coqui XTTS v2** — open-source multilingual TTS model (~2 GB, downloads on first run)
- **Gradio** — web UI
- **Python 3.11** virtualenv (`voiceclone/`)

**Files:**
- `voice_clone.py` — backend: extract voiceprint, synthesize speech
- `app.py` — Gradio UI (2 tabs: record voiceprint, generate speech)
- `requirements.txt` — dependencies

**To run:**
```bash
cd /Users/rumwei/claude_test/test_1
voiceclone/bin/python app.py
# Open http://127.0.0.1:7860
```

---

## Issues Fixed During Setup

### 1. Missing virtualenv
- **Problem:** No venv, packages not installed
- **Fix:** Created `voiceclone/` venv with Python 3.11 (`python3.11 -m venv voiceclone`)

### 2. Python version incompatibility
- **Problem:** System Python was 3.13; Coqui TTS only supports up to 3.12
- **Fix:** `brew install python@3.11`, recreated venv

### 3. Coqui TOS interactive prompt (EOF error)
- **Problem:** TTS model download prompts for license agreement via `input()`, which fails in Gradio callback threads
- **Fix 1:** Set `COQUI_TOS_AGREED=1` env var in `voice_clone.py`
- **Fix 2:** Manually created `tos_agreed.txt` in the model cache dir:
  `~/Library/Application Support/tts/tts_models--multilingual--multi-dataset--xtts_v2/tos_agreed.txt`

### 4. `transformers` too new (BeamSearchScorer removed)
- **Problem:** `transformers==5.3.0` removed `BeamSearchScorer`, used by Coqui's `stream_generator.py`
- **Fix:** Pinned to `transformers==4.45.0`

### 5. PyTorch 2.6 `weights_only=True` default
- **Problem:** PyTorch 2.6 changed `torch.load` default to `weights_only=True`, breaking Coqui model loading (`XttsConfig`, `XttsAudioConfig` not allowlisted)
- **Fix:** Monkey-patched `torch.load` in `voice_clone.py` to default `weights_only=False`

### 6. `torchaudio` requiring `torchcodec`
- **Problem:** `torchaudio==2.10.0` requires `torchcodec` for audio loading
- **Fix:** Downgraded to `torchaudio==2.5.0` (also pulled `torch==2.5.0`)

### 7. Voiceprint download
- **Problem:** Voiceprint saved to temp dir with no way to download it
- **Fix:** Added `gr.File` download component to Step 1 tab in `app.py`

### 8. Stuck "processing" spinner
- **Problem:** Added a `.then()` Gradio callback to show/hide download component — got stuck
- **Fix:** Removed `.then()`, made the download component always visible

---

## Known Limitations / Future Improvements

- [ ] Voiceprint file is overwritten each session (no per-user management)
- [ ] No progress bar during model loading (first run takes a while)
- [ ] Gradio 6.0 deprecation warning: `css`/`theme` should move to `launch()`
- [ ] Model loads lazily on first button click — could preload on startup
- [ ] No audio preview of the uploaded voice sample before saving
