"""
Voice Cloning — Gradio Web UI
--------------------------------------
Run:  python app.py
"""

import os
import tempfile
import gradio as gr
import voice_clone as vc

VPRINT_PATH = os.path.join(tempfile.gettempdir(), "session.vprint.npz")

LANGUAGES = {
    "Chinese (Mandarin)": "zh-cn",
    "English":            "en",
    "Japanese":           "ja",
    "Korean":             "ko",
    "French":             "fr",
    "German":             "de",
    "Spanish":            "es",
}

# ── Callbacks ─────────────────────────────────────────────────────────────────

def cb_save_voiceprint(audio):
    """Called when the user submits a recording or uploads a file."""
    if audio is None:
        return gr.update(), "Please record or upload an audio sample first.", None
    try:
        vc.extract_voiceprint(audio, VPRINT_PATH)
        return (
            gr.update(value="✅  Voiceprint saved — go to Step 2!", visible=True),
            "Voiceprint extracted and saved successfully.",
            VPRINT_PATH,
        )
    except Exception as e:
        return gr.update(visible=True), f"Error: {e}", None


def cb_synthesize(text, lang_label, vprint_file):
    """Called when the user clicks Generate."""
    vprint_path = vprint_file if vprint_file else VPRINT_PATH
    if not vprint_path or not os.path.exists(vprint_path):
        return None, "No voiceprint found. Complete Step 1 first."
    if not text.strip():
        return None, "Please enter some text."
    lang_code = LANGUAGES.get(lang_label, "zh-cn")
    try:
        out_wav = vc.synthesize(vprint_path, text, lang_code)
        return out_wav, "Done! Press play to hear your cloned voice."
    except Exception as e:
        return None, f"Error: {e}"


# ── UI Layout ─────────────────────────────────────────────────────────────────

custom_css = """
#title { text-align: center; }
#subtitle { text-align: center; color: #666; margin-bottom: 1rem; }
.step-header { font-size: 1.1rem; font-weight: 600; margin-bottom: 0.25rem; }
.tip { font-size: 0.85rem; color: #888; }
"""

with gr.Blocks(title="Voice Cloning", css=custom_css, theme=gr.themes.Soft()) as demo:

    # ── Header ────────────────────────────────────────────────────────────────
    gr.Markdown("# Voice Cloning", elem_id="title")
    gr.Markdown(
        "Clone any voice in two steps — record once, synthesize forever.",
        elem_id="subtitle",
    )

    with gr.Tabs():

        # ── Tab 1: Record voiceprint ──────────────────────────────────────────
        with gr.Tab("🎙️  Step 1 — Record Voiceprint"):
            gr.Markdown(
                "Record **10–20 seconds** of clear speech, or upload an existing audio file. "
                "The model will extract your unique voice identity.",
                elem_classes="tip",
            )
            with gr.Row():
                with gr.Column(scale=2):
                    audio_input = gr.Audio(
                        sources=["microphone", "upload"],
                        type="filepath",
                        label="Your Voice Sample",
                    )
                    save_btn = gr.Button("💾  Save Voiceprint", variant="primary", size="lg")

                with gr.Column(scale=1):
                    save_status = gr.Textbox(label="Status", interactive=False, lines=3)
                    saved_badge = gr.Markdown(visible=False)
                    vprint_download = gr.File(label="Download Voiceprint")

            save_btn.click(
                fn=cb_save_voiceprint,
                inputs=[audio_input],
                outputs=[saved_badge, save_status, vprint_download],
            )

        # ── Tab 2: Synthesize ─────────────────────────────────────────────────
        with gr.Tab("🔊  Step 2 — Speak Any Text"):
            gr.Markdown(
                "Type any text and it will be read aloud **in your voice**.",
                elem_classes="tip",
            )
            with gr.Row():
                with gr.Column(scale=2):
                    text_input = gr.Textbox(
                        label="Text to Synthesize",
                        placeholder="Hello, this is my cloned voice.",
                        lines=5,
                    )
                    with gr.Row():
                        lang_selector = gr.Dropdown(
                            label="Language",
                            choices=list(LANGUAGES.keys()),
                            value="English",
                        )
                        vprint_upload = gr.File(
                            label="Load .vprint file (optional)",
                            file_types=[".npz"],
                            type="filepath",
                        )
                    speak_btn = gr.Button("▶  Generate Audio", variant="primary", size="lg")

                with gr.Column(scale=2):
                    out_audio = gr.Audio(label="Cloned Voice Output", type="filepath")
                    speak_status = gr.Textbox(label="Status", interactive=False, lines=2)

            speak_btn.click(
                fn=cb_synthesize,
                inputs=[text_input, lang_selector, vprint_upload],
                outputs=[out_audio, speak_status],
            )

        # ── Tab 3: Help ───────────────────────────────────────────────────────
        with gr.Tab("ℹ️  Help"):
            gr.Markdown("""
## How it works

| Step | Action | Result |
|------|--------|--------|
| 1 | Record or upload your voice (10–20 sec) | A `.vprint` file is saved with your voice identity |
| 2 | Type any text + pick a language | Audio is generated in your voice |

## Tips for best quality
- Record in a **quiet room** with no background noise
- Speak **naturally** — no need to speak slowly
- **10–20 seconds** of speech gives the best voiceprint
- The more **varied** your sample (different sentences), the better

## Voiceprint file
Your voiceprint is saved as a `.npz` file in your temp folder each session.
You can also **upload a saved .vprint file** in Step 2 to reuse a previous voiceprint.

## Supported languages
Chinese (Mandarin) · English · Japanese · Korean · French · German · Spanish

## Model
[XTTS v2 by Coqui](https://huggingface.co/coqui/XTTS-v2) — open-source, runs locally.
First run downloads ~2 GB model weights automatically.
            """)

if __name__ == "__main__":
    demo.launch(inbrowser=True)
