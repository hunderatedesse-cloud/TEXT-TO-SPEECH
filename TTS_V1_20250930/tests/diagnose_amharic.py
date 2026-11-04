import sys
import io
import os

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

sys.path.insert(0, r"D:\TTS_V1_20250930")

from TTS.tts.configs.tacotron2_config import Tacotron2Config
from TTS.tts.datasets import load_tts_samples
from TTS.tts.models import setup_model

def test_model_init():
    config = Tacotron2Config()
    print("Loading TTS samples...")
    train_samples, eval_samples = load_tts_samples(
        config.datasets,
        eval_split=True,
        eval_split_max_size=config.eval_split_max_size,
        eval_split_size=config.eval_split_size,
    )
    print(f"Train samples count: {len(train_samples)}")
    print(f"Eval samples count: {len(eval_samples)}")
    print(f"Sample 0: {train_samples[0]}")

    print("\nSetting up model from config and samples...")
    model = setup_model(config, train_samples + eval_samples)
    print("Model initialized successfully!")
    print(f"Model class: {type(model).__name__}")
    print(f"Number of characters in model embedding: {model.num_chars}")
    print(f"Embedding layer shape: {model.embedding.weight.shape}")
    print(f"Number of speakers registered: {model.num_speakers}")
    print(f"Speaker manager speaker count: {model.speaker_manager.num_speakers}")
    print(f"First 5 speakers: {model.speaker_manager.speaker_names[:5]}")

if __name__ == "__main__":
    test_model_init()
