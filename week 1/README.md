# Speech-to-Text Evaluation System

A production-quality Speech-to-Text evaluation framework comparing **Vosk** and **OpenAI Whisper** models using the LibriSpeech dev-clean dataset.

## 📌 Project Overview

This system:
- **Processes audio** from LibriSpeech dev-clean dataset (FLAC → WAV conversion)
- **Transcribes** audio using two STT models (Vosk & Whisper)
- **Calculates metrics** - Word Error Rate (WER) for accuracy comparison
- **Generates reports** with detailed analysis and recommendations
- **Provides insights** on model performance and use case suitability

## 🏗️ Project Structure

```
meeting-stt-project/
├── data/
│   ├── raw_librispeech/        # Extract dev-clean here
│   ├── audio/                  # Converted WAV files (auto-generated)
│   └── transcripts/            # Extracted transcripts (auto-generated)
├── models/
│   └── vosk-model-small-en-us-0.15/    # Download required
├── outputs/
│   └── evaluation_report.txt   # Generated report
├── main.py                     # Main execution script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 📋 Requirements

- **Python 3.10+**
- **Operating System**: Windows, macOS, or Linux
- **Storage**: 
  - ~5GB for LibriSpeech dev-clean
  - ~500MB for Whisper-large model
  - ~50MB for Vosk model
- **RAM**: 8GB minimum (16GB recommended for Whisper)
- **GPU** (optional): CUDA-capable GPU for faster Whisper inference

## 🚀 Installation Guide

### Step 1: Clone/Create Project

```bash
cd d:/infosys-project
mkdir meeting-stt-project
cd meeting-stt-project
```

### Step 2: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/Scripts/activate  # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# For GPU acceleration with CUDA (optional)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Step 3: Download LibriSpeech Dataset

```bash
# Option 1: Manual Download
# 1. Go to: https://www.openslr.org/12
# 2. Download "dev-clean" (~1.6GB)
# 3. Extract to: data/raw_librispeech/dev-clean/

# Verify structure:
# data/raw_librispeech/dev-clean/
#   ├── 1272/
#   │   ├── 128104/
#   │   │   ├── 1272-128104-0000.flac
#   │   │   ├── 1272-128104-0001.flac
#   │   │   └── 1272-128104.trans.txt
#   │   └── ...
#   └── ...
```

### Step 4: Download Vosk Model

```bash
# Download from: https://alphacephei.com/vosk/models
# Extract to: models/vosk-model-small-en-us-0.15/

# Verify structure:
# models/vosk-model-small-en-us-0.15/
#   ├── am/
#   ├── conf/
#   ├── graph/
#   └── ivector/
```

### Step 5: Verify Installation

```bash
python -c "import vosk, whisper, librosa, jiwer; print('All dependencies installed!')"
```

## 📖 Usage

### Basic Usage

```bash
python main.py
```

### Expected Output

The system will:
1. Scan for FLAC files in `data/raw_librispeech/dev-clean/`
2. Convert first 5 files (configurable) to WAV format
3. Extract corresponding transcripts
4. Run Vosk and Whisper transcription on each file
5. Calculate WER metrics
6. Generate comprehensive report in `outputs/evaluation_report.txt`

### Customization

Edit `main.py` to modify parameters:

```python
# Change number of files to evaluate
pairs = LibriSpeechDataset.prepare_librispeech_dataset(
    raw_dataset_path,
    max_files=10  # Increase to 10 files
)

# Change Whisper model size (tiny, base, small, medium, large)
def transcribe_whisper(audio_path, model_size="small"):
    # ...
```

## 📊 Understanding the Report

### Key Metrics

- **WER (Word Error Rate)**: Percentage of words that differ from reference
  - 0.00 = Perfect transcription
  - 1.00+ = Poor transcription
  - Formula: WER = (S + D + I) / N where S=substitutions, D=deletions, I=insertions, N=reference words

- **Better Model**: Determined by lower average WER

### Sample Output

```
======================================================================
SPEECH-TO-TEXT MODEL EVALUATION REPORT
======================================================================

Average Word Error Rate (WER):
  Vosk:    0.1234 (12.34%)
  Whisper: 0.0567 (5.67%)

Performance Difference:
  Whisper is better by: 0.0667 (6.67%)

✓ Better Model: Whisper
```

## 🔍 Model Comparison

| Feature | Vosk | Whisper |
|---------|------|---------|
| **Accuracy** | Medium ⭐⭐ | High ⭐⭐⭐⭐ |
| **Speed** | Fast ⚡⚡⚡ | Moderate ⚡⚡ |
| **Model Size** | ~50MB | 500MB+ |
| **Memory** | Low | High |
| **Offline** | ✓ Yes | Partial* |
| **Multilingual** | Limited | ✓ 45+ languages |
| **Noise Robust** | Fair | Good ✓ |
| **Cloud Ready** | ✗ | ✓ Yes |

*Whisper can run offline but requires significant resources

## 📈 Use Case Recommendations

### Use **Vosk** for:
- ✓ Mobile applications
- ✓ Edge devices with limited resources
- ✓ Real-time voice commands
- ✓ Offline-first applications
- ✓ Low-latency requirements

### Use **Whisper** for:
- ✓ High-accuracy transcription
- ✓ Multilingual support needed
- ✓ Background noise handling
- ✓ Cloud/server deployments
- ✓ Archival/compliance transcription

## 🛠️ System Architecture

```
    LibriSpeech Audio (FLAC)
              ↓
    Convert to WAV (16kHz, Mono)
              ↓
         ┌────┴────┐
         ↓         ↓
      Vosk      Whisper
         ↓         ↓
      Text      Text
         ↓         ↓
    Calculate WER
         ↓
   Generate Report
```

## 🐛 Troubleshooting

### Issue: "No FLAC files found"
**Solution**: Ensure LibriSpeech is extracted correctly:
```
data/raw_librispeech/dev-clean/
├── 1272/
├── 1462/
└── ...
```

### Issue: "Vosk model not found"
**Solution**: Download and extract to `models/vosk-model-small-en-us-0.15/`

### Issue: Out of Memory (Whisper)
**Solution**: Use smaller Whisper model or increase system RAM:
```python
model_size="small"  # Instead of "large"
```

### Issue: Slow Vosk transcription
**Solution**: Ensure audio is valid WAV format (mono, 16-bit, 16kHz)

### Issue: GPU not detected
**Solution**: Verify CUDA installation and PyTorch:
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

## 📝 Output Files

### evaluation_report.txt
Contains:
- Per-file transcription comparison
- WER scores for each model
- Average performance metrics
- Model recommendation
- Architecture diagram
- Detailed analysis and observations

## 🎓 How It Works

### 1. Dataset Preparation
- Finds FLAC files in LibriSpeech dev-clean
- Converts each FLAC to mono WAV at 16kHz
- Extracts ground-truth transcripts from .trans.txt files

### 2. Voice Recognition
- **Vosk**: Uses Kaldi speech recognition framework (lightweight)
- **Whisper**: Uses OpenAI's Transformer-based model (accurate)

### 3. Evaluation
- Normalizes both reference and hypothesis text
- Calculates WER using jiwer library
- Aggregates metrics across all files

### 4. Reporting
- Generates comprehensive markdown report
- Includes architecture diagram and comparisons
- Provides actionable recommendations

## 📚 API Reference

### Main Classes

#### `LibriSpeechDataset`
- `prepare_librispeech_dataset(raw_path, max_files=5)` → List[Tuple[str, str]]

#### `VoskTranscriber`
- `transcribe_vosk(audio_path, model_path)` → str

#### `WhisperTranscriber`
- `transcribe_whisper(audio_path, model_size="base")` → str

#### `WERCalculator`
- `calculate_wer(reference, hypothesis)` → float

#### `ModelEvaluator`
- `evaluate_models(pairs, vosk_model_path)` → Tuple[List[Dict], float, float]

#### `ReportGenerator`
- `generate_report(results, avg_vosk_wer, avg_whisper_wer, output_path)` → None

## ⚙️ Configuration

### Adjustable Parameters

```python
# Number of files to evaluate
max_files = 5  # Increase for more comprehensive evaluation

# Whisper model size
model_size = "base"  # Options: tiny, base, small, medium, large

# Audio target sample rate
target_sr = 16000  # Standard for STT models

# Maximum WER threshold for warnings
wer_threshold = 0.3  # 30% error rate
```

## 🔐 Production Considerations

- **Data Privacy**: Ensure compliance with audio handling regulations
- **Model Licensing**: Respect Vosk and Whisper licensing terms
- **Performance Monitoring**: Track WER trends over time
- **Error Logging**: Review logs for failed transcriptions
- **Version Control**: Pin specific model versions for reproducibility

## 📞 Support & Documentation

- **Vosk**: https://alphacephei.com/vosk/
- **Whisper**: https://github.com/openai/whisper
- **LibriSpeech**: https://www.openslr.org/12
- **jiwer**: https://github.com/jitsi/jiwer

## 📄 License

This project is provided as-is. Ensure compliance with:
- Vosk license
- OpenAI Whisper license  
- LibriSpeech dataset terms

## ✅ Checklist for First Run

- [ ] Python 3.10+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] LibriSpeech dev-clean downloaded and extracted
- [ ] Vosk model downloaded and extracted
- [ ] Directory structure verified
- [ ] `python main.py` executed successfully
- [ ] Report generated in `outputs/evaluation_report.txt`

## 🎯 Next Steps

1. **Expand Dataset**: Increase `max_files` to evaluate on more samples
2. **Compare Models**: Try different Whisper model sizes
3. **Analyze Results**: Review report for insights
4. **Optimize**: Choose model based on your use case
5. **Deploy**: Integrate chosen model into your application

---

**Last Updated**: February 14, 2026  
**Version**: 1.0.0  
**Status**: Production Ready ✓
