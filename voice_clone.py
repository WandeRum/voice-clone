"""
Core voice cloning logic — backend module.
Uses XTTS v2 (Coqui) for open-source multilingual voice cloning.
"""

import os
import tempfile

os.environ.setdefault("COQUI_TOS_AGREED", "1")

# PyTorch 2.6+ changed torch.load default to weights_only=True, breaking Coqui TTS.
_original_torch_load = None

def _patch_torch_load():
    global _original_torch_load
    import torch
    _original_torch_load = torch.load
    def _load(*args, **kwargs):
        kwargs.setdefault("weights_only", False)
        return _original_torch_load(*args, **kwargs)
    torch.load = _load

_patch_torch_load()
import numpy as np
import soundfile as sf
import torch

_model = None


def get_model():
    global _model
    if _model is None:
        from TTS.api import TTS
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading XTTS v2 on {device}…")
        _model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    return _model


def extract_voiceprint(audio_path: str, out_path: str) -> str:
    """
    Extract speaker embedding from an audio file and save as .vprint (npz).

    Args:
        audio_path: WAV file of the speaker (3–30 seconds, clear speech).
        out_path:   Where to save the .vprint file.

    Returns:
        out_path
    """
    model = get_model()
    gpt_cond_latent, speaker_embedding = model.synthesizer.tts_model.get_conditioning_latents(
        audio_path=[audio_path]
    )
    audio, sr = sf.read(audio_path)
    np.savez(
        out_path,
        gpt_cond_latent=gpt_cond_latent.cpu().numpy(),
        speaker_embedding=speaker_embedding.cpu().numpy(),
        ref_audio=audio,
        sample_rate=np.array(sr),
    )
    return out_path


def load_voiceprint(vprint_path: str):
    """Load a .vprint file and return XTTS conditioning tensors."""
    data = np.load(vprint_path, allow_pickle=False)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    gpt_cond_latent = torch.tensor(data["gpt_cond_latent"]).to(device)
    speaker_embedding = torch.tensor(data["speaker_embedding"]).to(device)
    return gpt_cond_latent, speaker_embedding


def synthesize(vprint_path: str, text: str, language: str = "zh-cn") -> str:
    """
    Synthesize text in the voice stored in a .vprint file.

    Args:
        vprint_path: Path to a .vprint file.
        text:        Text to synthesize.
        language:    Language code (default: zh-cn).

    Returns:
        Path to a temporary output WAV file.
    """
    import torchaudio
    gpt_cond_latent, speaker_embedding = load_voiceprint(vprint_path)
    model = get_model()
    out = model.synthesizer.tts_model.inference(
        text=text,
        language=language,
        gpt_cond_latent=gpt_cond_latent,
        speaker_embedding=speaker_embedding,
    )
    tmp = tempfile.mktemp(suffix=".wav")
    wav = torch.tensor(out["wav"]).unsqueeze(0)
    torchaudio.save(tmp, wav, 24000)
    return tmp
