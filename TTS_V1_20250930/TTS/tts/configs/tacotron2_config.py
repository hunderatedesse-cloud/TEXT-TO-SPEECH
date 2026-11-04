# TTS/tts/configs/tacotron2_config.py
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from TTS.config.shared_configs import BaseAudioConfig
from TTS.tts.configs.tacotron_config import TacotronConfig
from TTS.tts.configs.shared_configs import CharactersConfig

@dataclass
class Tacotron2Config(TacotronConfig):
    model: str = "tacotron2"
    output_path: str = "D:/TTS_V1_20250930/runs/amharic_tacotron2"

    #  use BaseAudioConfig with valid keys
    audio: BaseAudioConfig = field(default_factory=lambda: BaseAudioConfig(
        sample_rate=16000,#how many samples per second your audio has. At 16k, 1 second = 16,000 numbers.
        resample=True,#if our input audio isn’t 16k, it will be converted to 16k.
        fft_size=1024,#the window size for FFT (how many samples you look at per chunk). 1024/16000 ≈ 64 ms per chunk.
        win_length=1024, #how big the analysis window is (same as fft_size here).
        hop_length=256,#how far you slide the window each step. 256/16000 ≈ 16 ms. Smaller hop = more frames per second.
        num_mels=80,#how many mel frequency bins we compress into. Output shape is [batch, 80, time].
        mel_fmin=0.0,#lowest frequency used (0 Hz).
        mel_fmax=8000.0,#highest frequency (8 kHz). Because with 16k sample rate, Nyquist = 8k max.
        preemphasis=0.97,#a filter that boosts high frequencies a little before analysis. Makes consonants clearer.
        ref_level_db=20,#reference loudness for normalization. Audio around 20 dB will map near zero in mel scale.
        do_trim_silence=True,#cuts quiet parts at the start/end.
        trim_db=45,#threshold for trimming. If below -45 dB relative to peak, treat it as silence.
        signal_norm=True,#scale values to a standard range before feeding the model.
        symmetric_norm=True,#values go from -max_norm to +max_norm (instead of 0 → +max_norm).
        max_norm=4.0,#the scale limit. So spectrogram values are clipped into [-4, 4].
        min_level_db=-100,#lower floor for log-mel values. Anything quieter than -100 dB is set to that.
        clip_norm=True,#if a value goes beyond ±4, clip it instead of allowing it.
        power=1.5, griffin_lim_iters=60,#these two knobs only matter when you try to reconstruct audio from the spectrogram
    ))

    # model dims
    out_channels: int = 80
    encoder_in_features: int = 512
    decoder_in_features: int = 512
    prenet_type: str = "original"
    attention_type: str = "original"
    decoder_r: int = 5
    stopnet: bool = True
    use_forward_attn: bool = False

    # training
    batch_size: int = 32
    eval_batch_size: int = 16
    epochs: int = 100
    lr: float = 1e-3
    weight_decay: float = 1e-6
    grad_clip: float = 1.0
    test_delay_epochs: int = 10
    run_eval: bool = True
    test_sentences: List[str] = field(default_factory=lambda: [
        "ሰላም፡ እንደምን አለህ፡ ይህ የአማርኛ ድምፅ ሙከራ ነው።",
        "ኢትዮጵያ ታሪካዊ እና ውብ ሀገር ናት።",
        "የሰው ልጅ በነፃነት የመኖር መብት አለው።",
        "ትምህርት ለሕይወት መሠረት ነው።",
        "አመሰግናለሁ።"
    ])

    # tokenizer
    text_cleaner: Optional[str] = None
    use_phonemes: bool = False
    phoneme_separator: str = ""

    characters: CharactersConfig = field(
        default_factory=lambda: CharactersConfig(
            characters="0123456789abcdefghijklmnopqrstuvwxyzäħəɡɨɲʃʒʔʕʼሀሁሂሃሄህሆለሉሊላሌልሎሏሐሑሒሓሔሕመሙሚማሜምሞሟሠሡሣሥሦረሩሪራሬርሮሯሰሱሲሳሴስሶሷሸሹሺሻሼሽሾሿቀቁቂቃቄቅቆቋበቡቢባቤብቦቧቨቩቪቫቬቭቮቯተቱቲታቴትቶቷቸቹቺቻቼችቾቿኀኃኅኋነኑኒናኔንኖኗኘኙኚኛኜኝኞኟአኡኢኣኤእኦከኩኪካኬክኮኰኲኳኵኸኽወዉዊዋዌውዎዐዑዒዓዔዕዖዘዙዚዛዜዝዞዟዠዡዢዣዤዥዦዧየዩዪያዬይዮደዱዲዳዴድዶዷጀጁጂጃጄጅጆጇገጉጊጋጌግጎጐጓጔጛጠጡጢጣጤጥጦጧጨጩጪጫጬጭጮጯጰጱጲጳጴጵጶጸጹጺጻጼጽጾጿፀፁፂፃፅፆፈፉፊፋፌፍፎፏፐፑፒፓፔፕፖ",
            punctuations=" !\"'()-./:;?«»፡።፣፤፥፦፧፨–—‘’“”‹›\ufeff",
            pad="<PAD>",
            eos="<EOS>",
            bos="<BOS>",
            blank="<BLNK>",
            phonemes="",
            is_unique=True,
            is_sorted=True,
        )
    )

    # multi-speaker
    use_speaker_embedding: bool = True
    d_vector_dim: int = 512

    # datasets
    datasets: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "formatter": "amharic_formatter",
            "dataset_name": "amharic",
            "path": "D:/TTS_V1_20250930/data/amharic_dataset",
            "language": "am",
            "meta_file_train": "CAC_DA_TTS_am_augmented.csv",
            "meta_file_val": None,
            "ignored_speakers": None,
            "meta_file_attn_mask": None,
        }
    ])
