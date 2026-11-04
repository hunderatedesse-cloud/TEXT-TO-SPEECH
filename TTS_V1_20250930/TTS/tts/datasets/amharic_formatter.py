import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import pandas as pd

from TTS.tts.amharic_g2p import g2p_amharic

AUDIO_EXTS = {".wav", ".flac", ".mp3", ".ogg", ".m4a"}


def _scan_speaker_tree(wav_root: str) -> Dict[Tuple[str, str], str]:
    """
    Index audio files by (speaker_id, utt_id).

    Structure:
        wav/
            speaker_id/
                audio_file.wav
    """
    index: Dict[Tuple[str, str], str] = {}
    if not os.path.isdir(wav_root):
        return index

    for spk_name in sorted(os.listdir(wav_root)):
        spk_dir = os.path.join(wav_root, spk_name)
        if not os.path.isdir(spk_dir):
            continue

        for root, _, files in os.walk(spk_dir):
            for fn in sorted(files):
                stem, ext = os.path.splitext(fn)
                if ext.lower() not in AUDIO_EXTS:
                    continue
                audio_path = os.path.join(root, fn)
                index[(spk_name, stem)] = audio_path
                # Also index with generic stem if speaker not given
                index[("", stem)] = audio_path

    return index


def amharic_formatter(config, *args, **kwargs) -> List[dict]:
    """
    Load Amharic audio and transcription data from CSV / dataset directory.

    Supported CSV columns:
        speaker or speaker_id
        wav_id or audio_file
        transcription or text
    """
    # Accept config object or string path
    ds_path = config.path if hasattr(config, "path") else str(config)
    ds_path = os.path.abspath(ds_path)

    # If ds_path points to data/ but the files are in data/amharic_dataset/
    if not os.path.isdir(os.path.join(ds_path, "wav")) and os.path.isdir(os.path.join(ds_path, "amharic_dataset", "wav")):
        ds_path = os.path.join(ds_path, "amharic_dataset")

    wav_root = os.path.join(ds_path, "wav")
    if not os.path.isdir(wav_root):
        raise FileNotFoundError(f"Missing audio directory: {wav_root}")

    # Determine metadata CSV file
    meta_file = kwargs.get("meta_file") or kwargs.get("meta_file_train")
    candidate_files = []
    if meta_file:
        candidate_files.append(meta_file if os.path.isabs(meta_file) else os.path.join(ds_path, meta_file))
    
    # Defaults in priority order (augmented first)
    candidate_files.extend([
        os.path.join(ds_path, "CAC_DA_TTS_am_augmented.csv"),
        os.path.join(ds_path, "CAC_DA_TTS_am.csv"),
        os.path.join(ds_path, "train.csv"),
        os.path.join(ds_path, "metadata.csv"),
    ])

    csv_path = None
    for cand in candidate_files:
        if os.path.isfile(cand):
            csv_path = cand
            break

    if not csv_path:
        raise FileNotFoundError(f"Could not find metadata CSV in {ds_path}. Checked: {candidate_files}")

    print(f"[amharic_formatter] Reading metadata from: {csv_path}")

    # Read CSV
    audio_data = pd.read_csv(csv_path, encoding="utf-8", dtype=str, keep_default_na=False)

    # Detect column names
    speaker_col = None
    for cand in ["speaker", "speaker_id", "speaker_name"]:
        if cand in audio_data.columns:
            speaker_col = cand
            break

    wav_id_col = None
    for cand in ["wav_id", "audio_file", "id"]:
        if cand in audio_data.columns:
            wav_id_col = cand
            break

    text_col = None
    for cand in ["transcription", "text", "transcript"]:
        if cand in audio_data.columns:
            text_col = cand
            break

    if not speaker_col or not wav_id_col or not text_col:
        raise ValueError(
            f"Missing required CSV columns. Found columns: {list(audio_data.columns)}. "
            f"Expected speaker column ({speaker_col}), wav_id column ({wav_id_col}), text column ({text_col})"
        )

    # Scan wav directory
    utt_index = _scan_speaker_tree(wav_root)
    print(f"[amharic_formatter] Indexed {len(utt_index)} audio entries across speakers in {wav_root}.")

    # Include augmented audio (fast, slow, normal) by default
    include_augmented = kwargs.get("include_augmented", True)
    use_g2p = kwargs.get("use_g2p", False)

    samples = []
    missing_audio = []
    empty_transcripts = []
    g2p_errors = []

    for row_number, (_, row) in enumerate(audio_data.iterrows(), start=2):
        speaker_name = row[speaker_col].strip()
        raw_wav_id = row[wav_id_col].strip().replace("\\", "/")
        base_utt_id = Path(raw_wav_id).stem
        transcript = row[text_col].strip()

        if not speaker_name or not base_utt_id:
            continue

        if not transcript:
            empty_transcripts.append(base_utt_id)
            continue

        # Target utterance IDs to search for (base and optionally augmented)
        if include_augmented:
            candidate_stems = [base_utt_id, f"{base_utt_id}_fast", f"{base_utt_id}_slow"]
        else:
            candidate_stems = [base_utt_id]

        matched_for_row = 0
        for stem in candidate_stems:
            audio_path = utt_index.get((speaker_name, stem)) or utt_index.get(("", stem))
            if not audio_path or not os.path.isfile(audio_path):
                continue

            matched_for_row += 1

            # Process text
            text = transcript
            if use_g2p:
                try:
                    text = g2p_amharic(transcript)
                except Exception as exc:
                    g2p_errors.append((stem, str(exc)))
                    text = transcript

            language = (row["language"].strip() if "language" in audio_data.columns else "am") or "am"

            samples.append({
                "text": text,
                "audio_file": audio_path,
                "speaker_name": speaker_name,
                "language": language,
                "audio_unique_name": f"{speaker_name}_{stem}",
                "root_path": ds_path,
                "base_id": base_utt_id,
            })

        if matched_for_row == 0:
            missing_audio.append(base_utt_id)

    print(f"[amharic_formatter] CSV rows: {len(audio_data)}")
    print(f"[amharic_formatter] Successfully loaded samples: {len(samples)}")
    print(f"[amharic_formatter] Missing audio count: {len(missing_audio)}")
    if empty_transcripts:
        print(f"[amharic_formatter] Empty transcripts count: {len(empty_transcripts)}")
    if g2p_errors:
        print(f"[amharic_formatter] G2P errors count: {len(g2p_errors)}")

    if not samples:
        raise ValueError(f"No valid samples were loaded from {csv_path}. Check paths and audio files.")

    return samples


def amharic_formatter_wrapper(root_path, meta_file=None, ignored_speakers=None, **kwargs):
    """
    Adapt Coqui dataset loader calls to amharic_formatter.
    """
    class Config:
        path = root_path

    return amharic_formatter(
        Config(),
        meta_file=meta_file,
        ignored_speakers=ignored_speakers,
        **kwargs
    )