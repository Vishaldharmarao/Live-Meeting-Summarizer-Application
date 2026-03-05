# Speaker Diarization + Speech-to-Text Pipeline
## Week 3 Project: AMI Meeting Corpus Analysis

A production-ready Python application for simultaneous speaker identification and speech transcription using state-of-the-art models.

---

## 📋 Features

✅ **Automatic Audio Validation** - Checks for audio file and provides download instructions  
✅ **Speech Transcription** - OpenAI Whisper (base model) with timestamp-level accuracy  
✅ **Speaker Diarization** - pyannote.audio for speaker identification  
✅ **Intelligent Merging** - Overlap-based matching of speakers to speech segments  
✅ **GPU Support** - Automatic CUDA detection for faster processing  
✅ **Production-Ready** - Full error handling, logging, and modular architecture  
✅ **Formatted Output** - Human-readable transcripts with timestamps  
✅ **Metadata Export** - JSON export with full segment details and speaker mapping  

---

## 🚀 Quick Start

### 1. **Environment Setup**

Activate the virtual environment:
```powershell
# Windows PowerShell
.\venv310\Scripts\Activate.ps1

# Or for Command Prompt
.\venv310\Scripts\activate.bat
```

### 2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

### 3. **Download Audio File**

The script requires: `audio/meeting.wav`

Download from **[AMI Corpus](https://groups.inf.ed.ac.uk/ami/corpus/)**:
- Meeting: **ES2002a**
- Audio Type: **Headset Mix**
- File: `ES2002a.Mix-Headset.wav`

**Steps:**
1. Visit https://groups.inf.ed.ac.uk/ami/corpus/
2. Download meeting ES2002a  
3. Extract the Mix-Headset audio
4. Place in `audio/` folder
5. Rename to `meeting.wav`

### 4. **Set HuggingFace Token (Optional)**

For faster model downloads and access to all models:
```powershell
$env:HF_TOKEN = "your_huggingface_token_here"
```

Or set it permanently in Windows:
```powershell
[Environment]::SetEnvironmentVariable("HF_TOKEN", "your_token", "User")
```

### 5. **Run the Pipeline**

```bash
python main.py
```

---

## 📁 Project Structure

```
project/
├── main.py                          # Main pipeline script
├── requirements.txt                 # Python dependencies
├── speaker_diarization.log          # Application log file (auto-created)
│
├── audio/
│   └── meeting.wav                  # Input audio file (download required)
│
├── output/
│   ├── final_transcript.txt          # Formatted transcript
│   └── transcript_metadata.json      # Full segment data + metadata
│
└── annotations/
    └── reference.rttm               # Optional: RTTM reference for DER (optional)
```

---

## 🔧 Configuration

Edit `main.py` to customize:

```python
class Config:
    WHISPER_MODEL = "base"                           # Options: tiny, base, small, medium, large
    DIARIZATION_MODEL = "pyannote/speaker-diarization-3.0"
    MIN_OVERLAP = 0.5                               # 50% overlap threshold for speaker assignment
    DEVICE = "cuda"                                 # Auto-detects, or set manually
```

---

## 📊 Output Examples

### Final Transcript (`output/final_transcript.txt`)
```
[00:00:01.230] Speaker 1: Welcome everyone to the meeting.

[00:00:05.120] Speaker 2: Thank you for joining us today.

[00:00:08.450] Speaker 1: Let's begin with the agenda items.

[00:00:12.760] Speaker 3: I have prepared a presentation.
```

### Metadata (`output/transcript_metadata.json`)
```json
{
  "device": "CUDA",
  "num_speakers": 3,
  "num_segments": 42,
  "speaker_mapping": {
    "SPEAKER_00": "Speaker 1",
    "SPEAKER_01": "Speaker 2",
    "SPEAKER_02": "Speaker 3"
  },
  "duration_seconds": 3847.5,
  "segments": [
    {
      "start": 1.23,
      "end": 4.56,
      "text": "Welcome everyone to the meeting.",
      "speaker": "SPEAKER_00",
      "speaker_label": "Speaker 1",
      "overlap_confidence": 0.87
    }
  ]
}
```

---

## 🔍 How It Works

### 1. **Audio Validation**
- Checks if `audio/meeting.wav` exists
- Provides detailed download instructions if missing

### 2. **Model Loading**
- Downloads Whisper (base) from Hugging Face
- Downloads pyannote diarization from Hugging Face
- Automatically uses GPU if available

### 3. **Transcription** (Whisper)
- Generates text with timestamps
- Chunks audio for accurate segment timing

### 4. **Diarization** (pyannote)
- Identifies speaker boundaries
- Outputs speaker segments with timestamps

### 5. **Merging** (Overlap Logic)
```
For each transcription segment:
  - Find all diarization segments
  - Calculate overlap ratio with each
  - Assign speaker with maximum overlap (if > 50%)
  - Otherwise label as "Unknown"
```

Example:
```
Transcription: [0.0-5.0] "Hello"
Diarization:   SPEAKER_0 [0.2-4.8]  → 96% overlap ✓
               SPEAKER_1 [5.5-6.0]   → 0% overlap ✗

Result: [0.0-5.0] "Hello" → SPEAKER_0
```

### 6. **Speaker Mapping**
- Converts `SPEAKER_00` → `Speaker 1`, `SPEAKER_01` → `Speaker 2`, etc.
- Maintains consistency throughout transcript

### 7. **Output Generation**
- Formatted transcript with speakers and timestamps
- JSON metadata with all details
- Summary report with statistics

---

## 🎯 Key Functions

| Function | Purpose |
|----------|---------|
| `validate_audio_file()` | Ensures audio file exists, provides instructions if missing |
| `load_models()` | Loads Whisper and pyannote pipelines |
| `transcribe_audio()` | Generates text with timestamps using Whisper |
| `run_diarization()` | Identifies speakers using pyannote |
| `merge_results()` | Combines transcription + diarization with overlap logic |
| `map_speaker_labels()` | Converts SPEAKER_XX IDs to "Speaker N" format |
| `format_transcript()` | Creates human-readable output |
| `save_transcript()` | Writes transcript and metadata to files |
| `calculate_der()` | Optional: Computes Diarization Error Rate |
| `print_summary()` | Displays statistics and results |

---

## ⚙️ Technical Details

### Overlap-Based Matching

The pipeline uses a **maximum overlap strategy** for speaker assignment:

```python
overlap_ratio = overlap_duration / transcription_segment_duration

if overlap_ratio ≥ 0.5:
    assign_speaker = diarization_speaker
else:
    assign_speaker = "Unknown"
```

**Why?** Ensures transcription text is matched to the predominant speaker during that time window. Mitigates edge cases where text begins/ends near speaker transitions.

### Device Selection

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
```

- **CUDA**: ~20-30x faster (GPU memory required)
- **CPU**: Works on any machine, slower processing

### Model Details

| Component | Model | Size | Accuracy |
|-----------|-------|------|----------|
| Transcription | Whisper base | 140M params | ~96% WER |
| Diarization | pyannote 3.0 | Pre-trained | SOTA performance |

---

## 🐛 Troubleshooting

### Issue: "Audio file not found"
**Solution:** Download `ES2002a.Mix-Headset.wav` from AMI Corpus and place in `audio/` as `meeting.wav`

### Issue: "CUDA out of memory"
**Solutions:**
- Use smaller Whisper model: `WHISPER_MODEL = "tiny"`
- Process on CPU: `DEVICE = "cpu"`
- Reduce batch size in model config

### Issue: "HF_TOKEN not set - using anonymous access"
**Solution:** Set environment variable:
```powershell
$env:HF_TOKEN = "hf_xxxxxxxxxxxx"
```

### Issue: Model download fails
**Troubleshooting:**
1. Check internet connection
2. Ensure HF_TOKEN is valid (for some models)
3. Try manual download: `huggingface-cli download pyannote/speaker-diarization-3.0`

---

## 📈 Performance Tips

### For Faster Processing:
1. **Use CUDA**: Requires NVIDIA GPU + CUDA Toolkit
2. **Smaller Whisper**: Change to `tiny` or `small` model
3. **Batch Processing**: Process multiple files sequentially

### For Better Accuracy:
1. **Larger Whisper**: Use `medium` or `large` model
2. **Clean Audio**: Minimize background noise
3. **Adjust MIN_OVERLAP**: Try 0.3-0.7 range for different audio quality

---

## 📝 Logging

Console and file logging enabled:

```
speaker_diarization.log
```

Contains:
- Model loading status
- Transcription progress
- Diarization results
- Merge statistics
- Output file locations
- Any errors/warnings

---

## 🔐 Privacy & Security

- Models downloaded from official Hugging Face Hub
- HF_TOKEN kept in environment variables (not in code)
- All processing done locally (no cloud upload)
- Audio file path configurable via Config class

---

## 📚 References

- **Whisper Paper**: [Robust Speech Recognition via Large-Scale Weak Supervision](https://arxiv.org/abs/2212.04356)
- **pyannote**: [End-to-End Speaker Segmentation and Clustering](https://github.com/pyannote/pyannote-audio)
- **AMI Corpus**: [Meeting Transcription Dataset](https://groups.inf.ed.ac.uk/ami/corpus/)

---

## 🎓 Author

**Vishal** - Week 3 Project: Speaker Diarization + Speech-to-Text

---

## 📄 License

This project uses open-source models and libraries. Ensure compliance with their respective licenses.

---

## ⭐ Common Use Cases

### Use Case 1: Meeting Transcription
```bash
python main.py  # Transcribe meeting with speaker labels
# Output: final_transcript.txt with "Speaker 1:", "Speaker 2:", etc.
```

### Use Case 2: Data Extraction
```python
# Load metadata to extract specific speaker
import json
with open("output/transcript_metadata.json") as f:
    data = json.load(f)
    speaker1_segments = [s for s in data["segments"] if s["speaker_label"] == "Speaker 1"]
```

### Use Case 3: Quality Assessment
```python
# Compare with reference RTTM and compute DER
# Place reference.rttm in annotations/
python main.py  # Automatically calculates DER if reference exists
```

---

**Questions?** Check the logs in `speaker_diarization.log` for detailed diagnostic information.
