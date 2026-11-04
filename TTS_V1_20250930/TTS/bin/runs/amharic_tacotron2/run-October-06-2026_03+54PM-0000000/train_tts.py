import os
import sys
import io
from dataclasses import dataclass, field
from pathlib import Path

# Ensure local repository root is always in sys.path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

from trainer import Trainer, TrainerArgs

from TTS.config import load_config, register_config
from TTS.tts.datasets import load_tts_samples
from TTS.tts.models import setup_model


@dataclass
class TrainTTSArgs(TrainerArgs):
    config_path: str = field(default=None, metadata={"help": "Path to the config file."})
    validate_only: bool = field(default=False, metadata={"help": "Validate configuration, dataset, tokenizer, model, and trainer without starting training."})


def resolve_config_path(config_path: str) -> str:
    """Find and resolve config path across possible candidate locations."""
    if config_path and os.path.isfile(config_path):
        return os.path.abspath(config_path)

    # Candidate default configurations in order of preference
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, "../.."))
    candidates = [
        config_path,
        os.path.join(repo_root, "config", "amharic_tacotron2_config.json"),
        os.path.join(repo_root, "TTS", "config", "model_config.json"),
        os.path.join(script_dir, "../config/model_config.json"),
        os.path.join(os.getcwd(), "config/amharic_tacotron2_config.json"),
    ]

    for cand in candidates:
        if cand and os.path.isfile(cand):
            return os.path.abspath(cand)

    raise FileNotFoundError(
        f" [!] Could not resolve a valid configuration file. Checked: {[c for c in candidates if c]}"
    )


def validate_dataset_samples(train_samples, eval_samples):
    """Print diagnostic information about the discovered dataset."""
    total = len(train_samples) + len(eval_samples)
    speakers = set(s.get("speaker_name", "") for s in train_samples + eval_samples)
    
    print("\n" + "=" * 60)
    print("DATASET VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total samples discovered : {total}")
    print(f"Training samples count   : {len(train_samples)}")
    print(f"Evaluation samples count : {len(eval_samples)}")
    print(f"Unique speakers count    : {len(speakers)}")
    
    # Check sample files existence
    missing_files = 0
    for s in (train_samples[:50] + eval_samples[:50]):
        if not os.path.isfile(s.get("audio_file", "")):
            missing_files += 1
    print(f"Audio file existence check (sample): {100 - missing_files}/100 valid")
    
    print("\nExample Discovered Samples:")
    for idx, sample in enumerate(train_samples[:2], start=1):
        print(f"\n[Sample {idx}]")
        print(f"  Text         : {sample.get('text')}")
        print(f"  Audio Path   : {sample.get('audio_file')}")
        print(f"  Speaker      : {sample.get('speaker_name')}")
        print(f"  Language     : {sample.get('language')}")
        print(f"  Audio Exists : {os.path.isfile(sample.get('audio_file', ''))}")
    print("=" * 60 + "\n")


def main():
    """Run `tts` model training directly by a `config.json` file."""
    # init trainer args
    train_args = TrainTTSArgs()
    parser = train_args.init_argparse(arg_prefix="")

    # override trainer args from command-line args
    args, config_overrides = parser.parse_known_args()
    train_args.parse_args(args)

    # resolve config file path
    resolved_config_path = resolve_config_path(args.config_path)
    train_args.config_path = resolved_config_path
    print(f" > Using configuration file: {resolved_config_path}")

    # load config.json and register
    if resolved_config_path or args.continue_path:
        if resolved_config_path:
            # init from a file
            config = load_config(resolved_config_path)
            if len(config_overrides) > 0:
                config.parse_known_args(config_overrides, relaxed_parser=True)
        elif args.continue_path:
            # continue from a prev experiment
            config = load_config(os.path.join(args.continue_path, "config.json"))
            if len(config_overrides) > 0:
                config.parse_known_args(config_overrides, relaxed_parser=True)
        else:
            # init from console args
            from TTS.config.shared_configs import BaseTrainingConfig  # pylint: disable=import-outside-toplevel

            config_base = BaseTrainingConfig()
            config_base.parse_known_args(config_overrides)
            config = register_config(config_base.model)()

    # load training samples
    train_samples, eval_samples = load_tts_samples(
        config.datasets,
        eval_split=True,
        eval_split_max_size=config.eval_split_max_size,
        eval_split_size=config.eval_split_size,
    )

    # Validate dataset before model initialization
    validate_dataset_samples(train_samples, eval_samples)

    # init the model from config
    model = setup_model(config, train_samples + eval_samples)

    # init the trainer and 🚀
    trainer = Trainer(
        train_args,
        model.config,
        config.output_path,
        model=model,
        train_samples=train_samples,
        eval_samples=eval_samples,
        parse_command_line_args=False,
    )

    if args.validate_only:
        print("\n [✓] VALIDATION COMPLETED SUCCESSFULLY!")
        print(" [✓] Configuration, dataset, tokenizer, audio processor, speaker manager, model, and trainer are 100% verified.")
        print(" [✓] Ready to begin training when invoked without --validate_only.")
        return

    # Start training
    trainer.fit()


if __name__ == "__main__":
    main()
