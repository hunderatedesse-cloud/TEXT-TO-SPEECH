
"""from types import SimpleNamespace
from pathlib import Path
from TTS.tts.datasets import amharic_formatter as formatter


ds = Path("./datasets/amharic_tts")

print("Dataset folder:", ds)
print("Expecting files at:", ds / "text", "and", ds / "wav")

# Quick sanity checks
if not (ds / "text").exists():
    raise FileNotFoundError(f"'text' file not found at: {ds / 'text'}")
if not (ds / "wav").exists():
    raise FileNotFoundError(f"'wav' folder not found at: {ds / 'wav'}")

# Build the config object your formatter expects
cfg = SimpleNamespace(path=str(ds))

#  Run the formatter
samples = formatter.amharic_formatter(cfg)
print(f"\nLoaded {len(samples)} samples.")
for s in samples[:3]:
    print(" - audio_file:", s["audio_file"]) 
    print("   speaker   :", s["speaker_name"])
    print("   text      :", s["text"][:120], "...\n")"""
import json
from TTS.tts.datasets import load_tts_samples

cfg_path = "/tts/configs/tacotron2_config.py"  # or your local path
with open(cfg_path, "r", encoding="utf-8") as f:
    cfg = json.load(f)

train, val = load_tts_samples(
    cfg["datasets"],
    eval_split=True,
    eval_split_max_size=cfg.get("eval_split_max_size"),
    eval_split_size=cfg.get("eval_split_size", 0.01),
)
print("train:", len(train), "val:", len(val))
print(train[0])
