# Project Documentation

Complete technical documentation for the Speech-to-Text Evaluation System.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Module Overview](#module-overview)
3. [Class Reference](#class-reference)
4. [Function Reference](#function-reference)
5. [Data Flow](#data-flow)
6. [Error Handling](#error-handling)
7. [Performance Metrics](#performance-metrics)

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE LAYER                        │
├─────────────────────┬──────────────────────┬────────────────────┤
│  main.py (CLI)      │  quickstart.py (GUI) │  demo.py (Testing) │
└─────────────────────┴──────────────────────┴────────────────────┘
           │                     │                      │
           └─────────┬───────────┴──────────────────────┘
                     │
┌─────────────────────────────────────────────────────────────────┐
│               PROCESSING & EVALUATION LAYER                    │
├──────────────┬─────────────────┬────────────────┬──────────────┤
│   Dataset    │   Transcription │    Metrics     │   Reporting  │
│  Processing  │     Services    │   Calculation  │   Generation │
└──────────────┴─────────────────┴────────────────┴──────────────┘
           │              │              │              │
           v              v              v              v
┌──────────────┐  ┌──────────────────────────────┐  ┌──────────┐
│ LibriSpeech  │  │  STT Models                  │  │ WER      │
│ Audio Data   │  ├──────────────┬──────────────┤  │ Report   │
│              │  │ Vosk         │ Whisper      │  │ Generation│
│ (FLAC → WAV) │  │ (Kaldi,Fast) │ (Transformer,│  │          │
│              │  │              │  Accurate)   │  │ Outputs: │
│              │  └──────────────┴──────────────┘  │ • .txt   │
│              │                                    │ • Metrics│
└──────────────┘                                    └──────────┘
       │                      │                          │
       └──────────┬───────────┴──────────────────────────┘
                  │
         ┌────────────────┐
         │ Configuration  │
         │  (config.py)   │
         └────────────────┘
```

### Module Structure

```
meeting-stt-project/
│
├── Core Modules
│   ├── main.py              # Main execution & core classes
│   ├── config.py            # Configuration management
│   ├── quickstart.py        # Interactive setup guide
│   └── demo.py              # Demo & testing utilities
│
├── Data
│   ├── raw_librispeech/     # Raw LibriSpeech dataset (input)
│   ├── audio/               # Converted WAV files (processed)
│   └── transcripts/         # Extracted transcripts (processed)
│
├── Models
│   └── vosk-model-small.../ # Vosk STT model
│       # Whisper auto-downloads to ~/.cache/whisper/
│
├── Outputs
│   ├── evaluation_report.txt  # Main output report
│   └── evaluation.log         # Optional detailed logs
│
└── Documentation
    ├── README.md            # Main documentation
    ├── SETUP.md             # Installation guide
    ├── TROUBLESHOOTING.md   # Common issues & fixes
    ├── Project_Docs.md      # This file
    └── .gitignore           # Git ignore rules
```

## Module Overview

### main.py

**Purpose**: Core system implementation with all evaluation logic

**Key Classes**:

1. **AudioProcessor**
   - `convert_flac_to_wav()` - Convert FLAC to 16kHz mono WAV
   - Handles audio format standardization

2. **TextNormalizer**
   - `normalize_text()` - Normalize text for fair WER comparison
   - Lowercase, remove punctuation, clean whitespace

3. **LibriSpeechDataset**
   - `prepare_librispeech_dataset()` - Prepare dataset for evaluation
   - `_extract_transcript()` - Extract reference transcripts

4. **VoskTranscriber**
   - `transcribe_vosk()` - Transcribe using Vosk model
   - Handles Kaldi speech recognition

5. **WhisperTranscriber**
   - `transcribe_whisper()` - Transcribe using Whisper model
   - Supports multiple model sizes (tiny to large)

6. **WERCalculator**
   - `calculate_wer()` - Calculate Word Error Rate
   - Uses jiwer library for accurate WER calculation

7. **ModelEvaluator**
   - `evaluate_models()` - Compare models on multiple files
   - Aggregates results and calculates averages

8. **ReportGenerator**
   - `generate_report()` - Create comprehensive evaluation report
   - Includes architecture diagram and recommendations

**Entry Point**: `main()` function

### config.py

**Purpose**: Centralized configuration management

**Key Configurations**:
- Dataset paths and parameters
- Audio processing settings
- Model selection and parameters
- Output and logging settings
- Performance optimization options

**Helper Functions**:
- `get_config_summary()` - Display current configuration

### quickstart.py

**Purpose**: Interactive setup and verification guide

**Features**:
- Check Python version
- Verify directory structure
- Check dependencies
- Verify models
- Check dataset
- View configuration
- Download instructions

### demo.py

**Purpose**: Testing and demonstration without full dataset

**Features**:
- Generate sample audio files
- Test core components
- Demonstrate configuration system
- Verify directory structure
- Useful for development and debugging

## Class Reference

### AudioProcessor

```python
class AudioProcessor:
    """Handles audio file conversions and processing."""
    
    @staticmethod
    def convert_flac_to_wav(
        flac_path: str,
        wav_path: str,
        target_sr: int = 16000
    ) -> bool:
        """
        Convert FLAC to WAV (mono, 16kHz)
        
        Args:
            flac_path: Input FLAC file path
            wav_path: Output WAV file path
            target_sr: Target sample rate (default: 16000)
            
        Returns:
            True if successful, False if failed
        """
```

### TextNormalizer

```python
class TextNormalizer:
    """Handles text normalization for WER calculation."""
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text for fair comparison
        
        Operations:
        - Lowercase
        - Remove punctuation
        - Clean whitespace
        
        Args:
            text: Raw text
            
        Returns:
            Normalized text
        """
```

### LibriSpeechDataset

```python
class LibriSpeechDataset:
    """Manages LibriSpeech dataset preparation and access."""
    
    @staticmethod
    def prepare_librispeech_dataset(
        raw_path: str,
        max_files: int = 5
    ) -> List[Tuple[str, str]]:
        """
        Prepare LibriSpeech dataset for evaluation
        
        Args:
            raw_path: Path to raw dataset
            max_files: Maximum files to process
            
        Returns:
            List of (audio_path, transcript_path) tuples
            
        Raises:
            FileNotFoundError: If paths don't exist
            ValueError: If no files found
        """
```

### VoskTranscriber

```python
class VoskTranscriber:
    """Handles speech recognition using Vosk model."""
    
    @staticmethod
    def transcribe_vosk(
        audio_path: str,
        model_path: str
    ) -> str:
        """
        Transcribe using Vosk
        
        Args:
            audio_path: Path to WAV file
            model_path: Path to Vosk model
            
        Returns:
            Transcribed text
            
        Raises:
            FileNotFoundError: If files not found
            ValueError: If audio format invalid
        """
```

### WhisperTranscriber

```python
class WhisperTranscriber:
    """Handles speech recognition using Whisper model."""
    
    @staticmethod
    def transcribe_whisper(
        audio_path: str,
        model_size: str = "base"
    ) -> str:
        """
        Transcribe using Whisper
        
        Args:
            audio_path: Path to audio file
            model_size: Model size from {tiny, base, small, medium, large}
            
        Returns:
            Transcribed text
            
        Raises:
            FileNotFoundError: If audio not found
            ValueError: If model size invalid
        """
```

### WERCalculator

```python
class WERCalculator:
    """Calculates Word Error Rate (WER)."""
    
    @staticmethod
    def calculate_wer(
        reference: str,
        hypothesis: str
    ) -> float:
        """
        Calculate WER between reference and hypothesis
        
        Formula: WER = (S + D + I) / N
        - S = substitutions
        - D = deletions  
        - I = insertions
        - N = reference words
        
        Args:
            reference: Ground truth text
            hypothesis: Predicted text
            
        Returns:
            WER score (0.0 to 1.0+)
        """
```

### ModelEvaluator

```python
class ModelEvaluator:
    """Evaluates STT models on multiple audio files."""
    
    @staticmethod
    def evaluate_models(
        pairs: List[Tuple[str, str]],
        vosk_model_path: str
    ) -> Tuple[List[Dict], float, float]:
        """
        Evaluate both models on multiple files
        
        Args:
            pairs: List of (audio_path, transcript_path) tuples
            vosk_model_path: Path to Vosk model
            
        Returns:
            Tuple of:
            - List of result dictionaries
            - Average Vosk WER
            - Average Whisper WER
        """
```

### ReportGenerator

```python
class ReportGenerator:
    """Generates evaluation reports."""
    
    @staticmethod
    def generate_report(
        results: List[Dict],
        avg_vosk_wer: float,
        avg_whisper_wer: float,
        output_path: str = "outputs/evaluation_report.txt"
    ) -> None:
        """
        Generate comprehensive evaluation report
        
        Args:
            results: List of evaluation results
            avg_vosk_wer: Average Vosk WER
            avg_whisper_wer: Average Whisper WER
            output_path: Output file path
        """
```

## Function Reference

### Main Entry Point

```python
def main() -> None:
    """
    Main execution function orchestrating the complete pipeline
    
    Steps:
    1. Configuration
    2. Dataset Preparation
    3. Model Evaluation
    4. Report Generation
    5. Summary Output
    """
```

## Data Flow

### Evaluation Pipeline

```
1. DATA PREPARATION
   ├─ Load LibriSpeech dev-clean
   ├─ Find FLAC files (max_files)
   ├─ Convert FLAC → WAV (mono, 16kHz)
   ├─ Extract transcripts from .trans.txt
   └─ Return (audio_path, transcript_path) pairs

2. TRANSCRIPTION (for each file)
   ├─ Load reference transcript
   ├─ Transcribe with Vosk
   │  ├─ Load model
   │  ├─ Process WAV file
   │  └─ Extract text
   ├─ Transcribe with Whisper
   │  ├─ Load model (auto-download if needed)
   │  ├─ Process audio
   │  └─ Extract text
   └─ Store results

3. EVALUATION
   ├─ For each file:
   │  ├─ Normalize reference text
   │  ├─ Normalize Vosk text
   │  ├─ Calculate Vosk WER
   │  ├─ Normalize Whisper text
   │  ├─ Calculate Whisper WER
   │  └─ Store result
   ├─ Calculate average WER
   └─ Determine better model

4. REPORTING
   ├─ Format per-file results
   ├─ Calculate statistics
   ├─ Create recommendations
   ├─ Generate architecture diagram
   ├─ Save to evaluation_report.txt
   └─ Display to console
```

### Result Data Structure

```python
result = {
    'file_index': 1,
    'filename': 'speaker-chapter-seq.wav',
    'reference': 'ground truth text',
    'vosk_transcription': 'vosk predicted text',
    'vosk_wer': 0.1234,
    'whisper_transcription': 'whisper predicted text',
    'whisper_wer': 0.0567,
}
```

## Error Handling

### Exception Hierarchy

```
Exception
├─ FileNotFoundError
│  ├─ Dataset path not found
│  ├─ Audio file not found
│  ├─ Model path not found
│  └─ Transcript file not found
│
├─ ValueError
│  ├─ No FLAC files found
│  ├─ invalid model size
│  ├─ Invalid audio format
│  └─ Empty transcript
│
├─ RuntimeError
│  ├─ CUDA out of memory
│  ├─ Model loading failed
│  └─ Transcription timeout
│
└─ Other
   ├─ Audio format error
   ├─ Encoding error
   └─ Permission error
```

### Error Handling Strategy

```python
# Configuration
RAISE_ON_ERROR = False  # Continue on errors
SKIP_FAILED_FILES = True  # Skip problematic files
TRANSCRIPTION_TIMEOUT = 300  # 5 minute timeout

# Implementation
try:
    # Process file
except FileNotFoundError:
    logger.error(f"File not found: {path}")
except ValueError as e:
    logger.error(f"Invalid data: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
finally:
    # Cleanup if needed
```

## Performance Metrics

### WER Calculation

**Formula**: 
$$\text{WER} = \frac{S + D + I}{N} \times 100\%$$

Where:
- $S$ = number of substitutions
- $D$ = number of deletions
- $I$ = number of insertions
- $N$ = number of reference words

**Interpretation**:
- 0% = Perfect transcription
- <5% = Excellent
- 5-10% = Good
- 10-20% = Acceptable
- 20-30% = Poor
- >30% = Very poor

### Performance Ratings

```python
WER_EXCELLENT = 0.05    # ⭐⭐⭐⭐⭐
WER_GOOD = 0.10         # ⭐⭐⭐⭐
WER_ACCEPTABLE = 0.20   # ⭐⭐⭐
WER_POOR = 0.30         # ⭐⭐
```

### Processing Metrics

**Per File**:
- Audio duration: ~3-5 seconds for LibriSpeech files
- Vosk transcription time: ~100-500ms (real-time capable)
- Whisper transcription time: ~1-5s (depends on model size)
- WER calculation: ~10ms

**Overall**:
- 5 files: ~30-60 seconds total
- 10 files: ~60-120 seconds total
- 20 files: ~120-240 seconds total

### Resource Usage

**Memory**:
- Vosk model: ~50MB
- Whisper base: ~500MB
- Whisper large: ~3GB
- Process overhead: ~100-500MB

**Disk**:
- Raw FLAC (5 files): ~10MB
- Converted WAV (5 files): ~15MB
- Models: ~550MB total
- Report: ~50KB

## Configuration Examples

### Quick Evaluation

```python
# config.py
MAX_FILES_TO_PROCESS = 5
WHISPER_MODEL_SIZE = "tiny"  # Fastest
AUDIO_TARGET_SAMPLE_RATE = 16000
USE_GPU_IF_AVAILABLE = False  # CPU only
```

### Accurate Evaluation

```python
# config.py
MAX_FILES_TO_PROCESS = 20
WHISPER_MODEL_SIZE = "large"  # Most accurate
AUDIO_TARGET_SAMPLE_RATE = 16000
USE_GPU_IF_AVAILABLE = True  # GPU acceleration
```

### Resource-Constrained

```python
# config.py
MAX_FILES_TO_PROCESS = 3
WHISPER_MODEL_SIZE = "base"  # Balance
AUDIO_TARGET_SAMPLE_RATE = 16000
USE_GPU_IF_AVAILABLE = False
BATCH_SIZE = 1
```

##Extension Points

### Adding New STT Model

1. Create new Transcriber class
2. Implement transcribe() method
3. Add to ModelEvaluator.evaluate_models()
4. Update ReportGenerator with comparison

### Adding Custom Metrics

1. Create Metric calculator class
2. Implement calculation logic
3. Integrate into ResultDict
4. Update ReportGenerator output

### Adding Data Sources

1. Create Dataset class
2. Implement prepare() method
3. Return (audio_path, transcript_path) pairs
4. Follow same structure as LibriSpeechDataset

---

**For support and additional information, see README.md, SETUP.md, and TROUBLESHOOTING.md**
