"""
Configuration Module for Speech-to-Text Evaluation System

This module contains all configurable parameters for the evaluation system.
Modify these values to customize the behavior of the evaluation pipeline.
"""

# ============================================================================
# DATASET CONFIGURATION
# ============================================================================

# Path to LibriSpeech raw dataset
DATASET_RAW_PATH = "data/raw_librispeech"

# Path to directory where audio files will be saved
DATASET_AUDIO_OUTPUT_PATH = "data/audio"

# Path to directory where transcripts will be saved
DATASET_TRANSCRIPT_OUTPUT_PATH = "data/transcripts"

# Maximum number of files from LibriSpeech to evaluate
# Increase for more comprehensive evaluation, decrease for faster testing
MAX_FILES_TO_PROCESS = 5

# ============================================================================
# AUDIO PROCESSING CONFIGURATION
# ============================================================================

# Target sample rate for audio files (Hz)
# Most STT models expect 16000 Hz (16kHz)
AUDIO_TARGET_SAMPLE_RATE = 16000

# Audio format for processing
# Note: Must be WAV for most STT models
AUDIO_FORMAT = "wav"

# Audio channels (1=mono, 2=stereo)
# Most STT models work best with mono audio
AUDIO_CHANNELS = 1

# Audio sample width in bytes (2 bytes = 16-bit)
AUDIO_SAMPLE_WIDTH = 2

# ============================================================================
# VOSK CONFIGURATION
# ============================================================================

# Path to Vosk model directory
VOSK_MODEL_PATH = "models/vosk-model-small-en-us-0.15"

# Vosk model is optimized for these settings:
# - 16kHz sample rate
# - 16-bit audio
# - Mono channel

# Vosk frame size for processing (bytes)
VOSK_FRAME_SIZE = 4000

# ============================================================================
# WHISPER CONFIGURATION
# ============================================================================

# Whisper model size
# Options: "tiny", "base", "small", "medium", "large"
# Larger = more accurate but slower and heavier
WHISPER_MODEL_SIZE = "base"

# Whisper language code (ISO 639-1)
WHISPER_LANGUAGE = "en"  # English

# Whisper device
# Options: "cuda" (GPU), "cpu", "mps" (Apple Silicon)
WHISPER_DEVICE = "cpu"

# Whisper processing settings
WHISPER_VERBOSE = False  # Show detailed processing info
WHISPER_TEMPERATURE = 0.0  # Lower = more deterministic

# Model characteristics (for reference)
WHISPER_MODEL_INFO = {
    "tiny": {"size_mb": 39, "params_m": 39, "english_only": True},
    "base": {"size_mb": 140, "params_m": 74, "english_only": False},
    "small": {"size_mb": 466, "params_m": 244, "english_only": False},
    "medium": {"size_mb": 1530, "params_m": 769, "english_only": False},
    "large": {"size_mb": 2950, "params_m": 1550, "english_only": False},
}

# ============================================================================
# TEXT PROCESSING CONFIGURATION
# ============================================================================

# Normalize text for WER calculation
# Operations: lowercase, remove punctuation, remove extra whitespace
TEXT_NORMALIZATION_ENABLED = True

# Remove punctuation characters during normalization
TEXT_REMOVE_PUNCTUATION = True

# Convert to lowercase
TEXT_LOWERCASE = True

# Remove extra whitespace
TEXT_CLEAN_WHITESPACE = True

# ============================================================================
# EVALUATION CONFIGURATION
# ============================================================================

# WER thresholds for reporting (for reference)
WER_EXCELLENT = 0.05    # 5% - Excellent performance
WER_GOOD = 0.10         # 10% - Good performance
WER_ACCEPTABLE = 0.20   # 20% - Acceptable performance
WER_POOR = 0.30         # 30% - Poor performance

# Performance rating function
def get_performance_rating(wer_score: float) -> str:
    """Rate performance based on WER score."""
    if wer_score <= WER_EXCELLENT:
        return "Excellent ⭐⭐⭐⭐⭐"
    elif wer_score <= WER_GOOD:
        return "Good ⭐⭐⭐⭐"
    elif wer_score <= WER_ACCEPTABLE:
        return "Acceptable ⭐⭐⭐"
    elif wer_score <= WER_POOR:
        return "Poor ⭐⭐"
    else:
        return "Very Poor ⭐"

# ============================================================================
# OUTPUT CONFIGURATION
# ============================================================================

# Path to output directory
OUTPUT_DIRECTORY = "outputs"

# Filename for evaluation report
REPORT_FILENAME = "evaluation_report.txt"

# Full path to report (auto-constructed)
REPORT_OUTPUT_PATH = f"{OUTPUT_DIRECTORY}/{REPORT_FILENAME}"

# Include architecture diagram in report
INCLUDE_ARCHITECTURE_DIAGRAM = True

# Include comparison table in report
INCLUDE_COMPARISON_TABLE = True

# Include per-file detailed results
INCLUDE_PER_FILE_RESULTS = True

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOGGING_LEVEL = "INFO"

# Logging format
LOGGING_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# Log to console
LOGGING_CONSOLE_ENABLED = True

# Log to file (optional)
LOGGING_FILE_ENABLED = False
LOGGING_FILE_PATH = "outputs/evaluation.log"

# ============================================================================
# ERROR HANDLING CONFIGURATION
# ============================================================================

# Raise exceptions on errors (True) or continue processing (False)
RAISE_ON_ERROR = False

# Skip files that fail transcription and continue with next file
SKIP_FAILED_FILES = True

# Timeout for transcription operations (seconds)
# Set to 0 for no timeout
TRANSCRIPTION_TIMEOUT = 300  # 5 minutes

# ============================================================================
# PERFORMANCE OPTIMIZATION CONFIGURATION
# ============================================================================

# Enable GPU acceleration if available
USE_GPU_IF_AVAILABLE = True

# Number of CPU threads for parallel processing
NUM_THREADS = 4

# Enable caching of model objects
ENABLE_MODEL_CACHING = True

# Batch processing size (number of files to process together)
BATCH_SIZE = 1

# ============================================================================
# VALIDATION CONFIGURATION
# ============================================================================

# Validate audio files before processing
VALIDATE_AUDIO_FILES = True

# Minimum audio duration (seconds)
MIN_AUDIO_DURATION = 0.5

# Maximum audio duration (seconds) - set to 0 for no limit
MAX_AUDIO_DURATION = 600  # 10 minutes

# Validate Vosk and Whisper models exist
VALIDATE_MODELS_EXIST = True

# ============================================================================
# ADVANCED CONFIGURATION
# ============================================================================

# Enable experimental features
EXPERIMENTAL_FEATURES_ENABLED = False

# Enable profiling of function execution
ENABLE_PROFILING = False

# Save intermediate transcriptions
SAVE_INTERMEDIATE_RESULTS = False
INTERMEDIATE_RESULTS_PATH = "outputs/intermediate/"

# Comparison mode
# "strict" = exact comparison, "lenient" = normalized comparison
COMPARISON_MODE = "lenient"

# ============================================================================
# FUNCTION HELPERS
# ============================================================================

def get_config_summary() -> str:
    """Generate a summary of current configuration."""
    summary = """
    ╔════════════════════════════════════════════════════════╗
    ║     SPEECH-TO-TEXT EVALUATION SYSTEM CONFIGURATION    ║
    ╚════════════════════════════════════════════════════════╝
    
    DATASET:
      • Input: {raw_path}
      • Audio output: {audio_path}
      • Transcript output: {transcript_path}
      • Max files: {max_files}
    
    AUDIO PROCESSING:
      • Sample rate: {sr} Hz
      • Format: {fmt}
      • Channels: {ch}
      • Sample width: {sw} bytes
    
    MODELS:
      • Vosk: {vosk_model}
      • Whisper: {whisper_model}
    
    OUTPUT:
      • Report path: {report_path}
      • Include diagram: {include_diag}
      • Include table: {include_table}
    
    LOGGING:
      • Level: {log_level}
      • Console enabled: {console_log}
    """.format(
        raw_path=DATASET_RAW_PATH,
        audio_path=DATASET_AUDIO_OUTPUT_PATH,
        transcript_path=DATASET_TRANSCRIPT_OUTPUT_PATH,
        max_files=MAX_FILES_TO_PROCESS,
        sr=AUDIO_TARGET_SAMPLE_RATE,
        fmt=AUDIO_FORMAT,
        ch=AUDIO_CHANNELS,
        sw=AUDIO_SAMPLE_WIDTH,
        vosk_model=VOSK_MODEL_PATH,
        whisper_model=WHISPER_MODEL_SIZE,
        report_path=REPORT_OUTPUT_PATH,
        include_diag=INCLUDE_ARCHITECTURE_DIAGRAM,
        include_table=INCLUDE_COMPARISON_TABLE,
        log_level=LOGGING_LEVEL,
        console_log=LOGGING_CONSOLE_ENABLED,
    )
    return summary.strip()


if __name__ == "__main__":
    # Print configuration summary when module is run directly
    print(get_config_summary())
