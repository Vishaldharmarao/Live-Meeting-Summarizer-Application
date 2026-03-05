"""
PROJECT STRUCTURE & FILE GUIDE
Speaker Diarization + Speech-to-Text Pipeline
Week 3: AMI Meeting Corpus Analysis
"""

PROJECT STRUCTURE:
==================

📦 week 3/
│
├── 📄 main.py                          [MAIN APPLICATION]
│   ├── 400+ lines of production code
│   ├── Complete speaker diarization pipeline
│   ├── Whisper transcription + pyannote diarization
│   └── Result merging with overlap logic
│
├── 📄 requirements.txt                 [DEPENDENCIES]
│   └── All pip packages needed
│
├── 📄 setup_check.py                   [VALIDATION]
│   ├── Pre-flight validation script
│   ├── Checks Python version, packages, GPU
│   └── Run before main.py for diagnostics
│
├── 📄 examples.py                      [USAGE EXAMPLES]
│   ├── 7 complete example functions
│   ├── Load and analyze output
│   ├── Export to CSV/SRT formats
│   └── Search and statistics
│
├── 📄 README.md                        [DOCUMENTATION]
│   ├── Quick start guide
│   ├── Feature overview
│   ├── Output format documentation
│   ├── Troubleshooting section
│   └── Performance tips
│
├── 📄 CONFIG_GUIDE.md                  [CONFIGURATION]
│   ├── 10 scenario customizations
│   ├── Performance vs accuracy tradeoffs
│   ├── Custom audio processing
│   └── Environment-specific settings
│
├── 📄 .env.example                     [ENVIRONMENT TEMPLATE]
│   └── Template for HF_TOKEN setup
│
├── 📄 .gitignore                       [GIT IGNORE]
│   └── Proper Python/ML project ignores
│
├── 📁 audio/                           [INPUT DATA]
│   └── meeting.wav                    (download required)
│
├── 📁 output/                          [RESULTS]
│   ├── final_transcript.txt            (auto-generated)
│   ├── transcript_metadata.json        (auto-generated)
│   ├── transcript.csv                  (from examples.py)
│   ├── transcript.srt                  (from examples.py)
│   └── meeting_minutes.txt             (from examples.py)
│
└── 📁 annotations/                     [OPTIONAL REFERENCE]
    ├── reference.rttm                  (optional, for DER)
    └── reference.rttm.example          (RTTM format template)


KEY FILES EXPLAINED:
====================

1. main.py (PRIMARY APPLICATION)
   ──────────────────────────────────────
   
   ENTRY POINT FOR THE ENTIRE PIPELINE
   
   Core Functions:
   • validate_audio_file()      - Check audio file exists
   • load_models()              - Load Whisper + pyannote
   • transcribe_audio()         - Generate text with timestamps
   • run_diarization()          - Identify speakers
   • merge_results()            - Combine with overlap logic
   • map_speaker_labels()       - SPEAKER_00 → Speaker 1
   • format_transcript()        - Create human-readable output
   • save_transcript()          - Write files
   • calculate_der()            - Optional: Compute metrics
   • print_summary()            - Display statistics
   
   Classes:
   • Config                     - Paths, models, device settings
   
   Execute:
   >>> python main.py
   
   Output:
   • final_transcript.txt       - Readable transcript
   • transcript_metadata.json   - Full segment data + stats
   • speaker_diarization.log   - Detailed logs


2. requirements.txt
   ──────────────────────────────────────
   
   Install Dependencies:
   >>> pip install -r requirements.txt
   
   Key Packages:
   • torch (2.0+)               - PyTorch deep learning
   • torchaudio                 - Audio processing
   • transformers               - Hugging Face models
   • openai-whisper             - Speech recognition
   • pyannote.audio             - Speaker diarization
   • huggingface_hub            - Model downloads


3. setup_check.py
   ──────────────────────────────────────
   
   Pre-flight validation before running main.py
   
   Checks:
   ✓ Python version (3.8+)
   ✓ Project directory structure
   ✓ main.py exists
   ✓ Dependencies installed
   ✓ Audio file present
   ✓ HF_TOKEN configured
   ✓ CUDA/GPU availability
   
   Execute:
   >>> python setup_check.py
   
   Output: Detailed checklist with fixes for any issues


4. examples.py
   ──────────────────────────────────────
   
   Demonstrates how to USE the pipeline output
   
   Functions:
   • load_transcript_metadata()  - Load output JSON
   • print_meeting_summary()     - Overview statistics
   • get_speaker_segments()      - Filter by speaker
   • print_speaker_transcript()  - One speaker's words
   • get_segments_by_time()      - Filter by time range
   • print_time_range_transcript() - Time-limited output
   • analyze_speaker_statistics()- Speaking time/words
   • print_speaker_statistics()  - Per-speaker metrics
   • export_to_csv()            - CSV export
   • export_to_srt()            - Subtitle format (video)
   • search_transcript()        - Find keywords
   • print_search_results()     - Highlighted search
   • generate_meeting_minutes() - Minutes-style format
   
   Execute:
   >>> python examples.py
   
   Note: Run main.py first to generate output


5. README.md
   ──────────────────────────────────────
   
   Complete documentation:
   • Feature overview
   • Quick start (5 steps)
   • Project structure explained
   • Configuration options
   • Output examples (formatted samples)
   • How the pipeline works (detailed)
   • Technical implementation details
   • Troubleshooting section
   • Performance optimization tips
   • References and citations
   • Common use cases


6. CONFIG_GUIDE.md
   ──────────────────────────────────────
   
   Advanced customization scenarios:
   
   Scenario 1: Fastest (tiny model, CPU)        ~5-10 min
   Scenario 2: Best accuracy (large model)      ~20-30 min
   Scenario 3: Balanced (base model, default)   ~30-40 min
   Scenario 4: Noisy audio (adjusted overlap)
   Scenario 5: Batch processing (multiple files)
   Scenario 6: Different overlap thresholds
   Scenario 7: Custom audio files
   Scenario 8: Real-time streaming
   Scenario 9: Non-English languages
   Scenario 10: Performance monitoring
   
   Quick reference table:
   • Environment vs model selection
   • Memory requirements
   • Processing duration estimates
   • Accuracy expectations


7. .env.example
   ──────────────────────────────────────
   
   Template for environment variables:
   • HF_TOKEN (optional, for faster downloads)
   • CUDA_VISIBLE_DEVICES (GPU selection)
   
   Copy to .env and fill in values:
   >>> cp .env.example .env
   >>> # Edit .env with your values


WORKFLOW:
=========

Step 1: SETUP ENVIRONMENT
  PowerShell> .\venv310\Scripts\Activate.ps1
  > pip install -r requirements.txt
  > python setup_check.py

Step 2: DOWNLOAD AUDIO (if needed)
  From: https://groups.inf.ed.ac.uk/ami/corpus/
  Meeting: ES2002a
  Place in: audio/meeting.wav

Step 3: CONFIGURE (optional)
  Edit main.py Config class for:
  • Different Whisper model size
  • Overlap threshold adjustment
  • Device selection (GPU/CPU)

Step 4: RUN PIPELINE
  > python main.py
  Generates:
  • output/final_transcript.txt
  • output/transcript_metadata.json

Step 5: ANALYZE OUTPUT (optional)
  > python examples.py
  Demonstrates:
  • Searching transcripts
  • Exporting to CSV/SRT
  • Speaker statistics
  • Meeting minutes format

Step 6: CUSTOMIZE (optional)
  Refer to CONFIG_GUIDE.md for:
  • Batch processing multiple files
  • Real-time streaming audio
  • Different languages
  • Performance monitoring


INPUT/OUTPUT DETAILS:
=====================

INPUT: audio/meeting.wav (required)
  • Format: WAV (44.1 kHz or 16 kHz, mono/stereo)
  • Duration: Any length (tested up to 2 hours)
  • Source: AMI Corpus ES2002a recommended
  • Download: https://groups.inf.ed.ac.uk/ami/corpus/

OUTPUT 1: output/final_transcript.txt (formatted)
  [00:01:23] Speaker 1: Hello everyone
  [00:01:28] Speaker 2: Good morning
  [00:01:32] Speaker 1: Let's begin the meeting
  
OUTPUT 2: output/transcript_metadata.json (detailed)
  {
    "device": "CUDA",
    "num_speakers": 3,
    "num_segments": 42,
    "duration_seconds": 3847.5,
    "speaker_mapping": {
      "SPEAKER_00": "Speaker 1",
      "SPEAKER_01": "Speaker 2",
      "SPEAKER_02": "Speaker 3"
    },
    "segments": [
      {
        "start": 1.23,
        "end": 4.56,
        "text": "Hello everyone",
        "speaker": "SPEAKER_00",
        "speaker_label": "Speaker 1",
        "overlap_confidence": 0.87
      },
      ...
    ]
  }

OPTIONAL INPUT: annotations/reference.rttm (for DER)
  SPEAKER ES2002a 1 0.000 5.230 <NA> SPK0001 <NA> <NA>
  SPEAKER ES2002a 1 5.230 3.890 <NA> SPK0002 <NA> <NA>
  (Enables automatic Diarization Error Rate calculation)


PERFORMANCE BENCHMARKS:
=======================

Device           | Whisper | Duration | Memory  | Speed
-----------------------------------------------------------------
CPU (i7-9700K)   | tiny    | 30 min   | 4-6 GB  | ~60x slower
CPU (i7-9700K)   | base    | 45 min   | 5-8 GB  | ~80x slower
GPU (RTX 2070)   | base    | 35 min   | 6-8 GB  | Real-time
GPU (RTX 3080)   | base    | 25 min   | 8-10 GB | 2-3x real-time
GPU (RTX 4090)   | large   | 20 min   | 12-16GB | 4-5x real-time

(Benchmarks for 1-hour audio file, approximate)


TROUBLESHOOTING QUICK REFERENCE:
=================================

Problem                          | Solution
──────────────────────────────────────────────────────────────
Audio file not found            | Download from AMI Corpus
Models not downloading          | Check HF_TOKEN, internet
CUDA out of memory              | Use 'tiny' model or CPU
Transcription accuracy poor     | Use 'large' model
Wrong speaker assignments       | Adjust MIN_OVERLAP threshold
Models taking too long to load  | First run is slow, cached after

See README.md TROUBLESHOOTING section for details


FILE SIZES (APPROXIMATE):
==========================

main.py                    ~14 KB
requirements.txt          ~0.5 KB
setup_check.py           ~4 KB
examples.py              ~12 KB
README.md                ~15 KB
CONFIG_GUIDE.md          ~12 KB

Models (auto-downloaded):
  Whisper base            ~140 MB
  pyannote diarization    ~800 MB
  (Total ~1 GB)

Output files (for 1-hour meeting):
  final_transcript.txt    ~50-100 KB (readable)
  transcript_metadata.json ~100-200 KB (detailed)


KEY COMMANDS:
=============

# Setup
python setup_check.py

# Run pipeline
python main.py

# View logs
tail -f speaker_diarization.log

# Analyze output
python examples.py

# Customize config
nano main.py  # Edit Config class

# Install specific model
pip install openai-whisper[large]

# List available CUDA devices
python -c "import torch; print(torch.cuda.device_count())"


QUICK START (TLDR):
===================

# 1. Activate venv
.\venv310\Scripts\Activate.ps1

# 2. Install packages
pip install -r requirements.txt

# 3. Download audio (ES2002a.Mix-Headset.wav) and place as audio/meeting.wav

# 4. Check setup
python setup_check.py

# 5. Run pipeline
python main.py

# Done! Check:
# - output/final_transcript.txt (readable)
# - output/transcript_metadata.json (data)
# - speaker_diarization.log (details)


CONTACTS & RESOURCES:
=====================

Questions about Whisper?      → https://github.com/openai/whisper
Questions about pyannote?     → https://github.com/pyannote/pyannote-audio
Need AMI corpus data?         → https://groups.inf.ed.ac.uk/ami/
HuggingFace models?           → https://huggingface.co/models
PyTorch documentation?        → https://pytorch.org
"""
