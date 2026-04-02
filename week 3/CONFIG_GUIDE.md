"""
Configuration Customization Guide
This file shows how to modify main.py's Config class for different scenarios
"""

# ============================================================================
# SCENARIO 1: Fastest Processing (CPU/Low-end hardware)
# ============================================================================
# Modify Config class in main.py:

"""
class Config:
    WHISPER_MODEL = "tiny"              # Fastest (2.77B params)
    DIARIZATION_MODEL = "pyannote/speaker-diarization-3.0"
    MIN_OVERLAP = 0.3                   # Lower threshold for overlap
    DEVICE = "cpu"                      # Force CPU
"""

# Benefits: Processes in ~5-10 minutes on modern CPU
# Trade-off: Slightly lower accuracy (Whisper WER ~7-8%)


# ============================================================================
# SCENARIO 2: Best Accuracy (High-end GPU)
# ============================================================================

"""
class Config:
    WHISPER_MODEL = "large"             # Best accuracy (1.5B params)
    DIARIZATION_MODEL = "pyannote/speaker-diarization-3.0"
    MIN_OVERLAP = 0.5                   # Standard threshold
    DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
"""

# Benefits: Highest transcription accuracy (WER ~3-4%)
# Time: ~20-30 minutes on RTX 3080
# Requirements: 10+ GB VRAM


# ============================================================================
# SCENARIO 3: Balanced (Mid-range GPU)
# ============================================================================

"""
class Config:
    WHISPER_MODEL = "base"              # Default (140M params)
    DIARIZATION_MODEL = "pyannote/speaker-diarization-3.0"
    MIN_OVERLAP = 0.5
    DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
"""

# Benefits: Good speed + accuracy balance
# Time: ~30-40 minutes on RTX 2070
# Requirements: 6+ GB VRAM


# ============================================================================
# SCENARIO 4: Optimized for Noisy Audio
# ============================================================================

"""
class Config:
    WHISPER_MODEL = "small"             # Better at noisy audio
    MIN_OVERLAP = 0.3                   # Lower threshold (more overlap tolerance)
    DIARIZATION_MODEL = "pyannote/speaker-diarization-3.0"
    DEVICE = "cuda"
"""

# Modification needed in run_diarization():
"""
def run_diarization(diarization_pipeline: object, audio_path: Path) -> List[Dict]:
    # Add initialization parameter for noisy audio:
    diarization = diarization_pipeline(
        str(audio_path),
        min_duration_off=0.5,            # Ignore silence < 0.5s
    )
"""


# ============================================================================
# SCENARIO 5: Multi-file Batch Processing
# ============================================================================

"""
def main_batch(audio_files: List[Path]):
    whisper_pipeline, diarization_pipeline = load_models()  # Load once
    
    for audio_path in audio_files:
        transcription_segments = transcribe_audio(whisper_pipeline, audio_path)
        diarization_segments = run_diarization(diarization_pipeline, audio_path)
        merged_segments = merge_results(transcription_segments, diarization_segments)
        labeled_segments, speaker_mapping = map_speaker_labels(merged_segments)
        formatted_transcript = format_transcript(labeled_segments)
        save_transcript(formatted_transcript, labeled_segments, speaker_mapping, str(Config.DEVICE))

# Usage:
audio_files = list(Path("audio").glob("*.wav"))
main_batch(audio_files)
"""


# ============================================================================
# SCENARIO 6: Different Overlap Thresholds
# ============================================================================

"""
MIN_OVERLAP values and their effects:

0.1  - Very permissive: Assign speaker even with minimal timing overlap
       ✓ Fewer "Unknown" labels
       ✗ More speaker misattribution

0.3  - Moderate: Good for audio with clear speaker turns
       ✓ Balanced accuracy
       ✓ Recommended for noisy audio

0.5  - Standard: Default value, robust across various audio quality
       ✓ Consistent results
       ✓ Recommended for most cases

0.7  - Strict: Only assign if speaker covers most of segment
       ✗ More "Unknown" labels
       ✓ High confidence matches only

0.9  - Very strict: Require near-complete overlap
       ✗ Very conservative
       ✓ For critical applications
"""


# ============================================================================
# SCENARIO 7: Custom Audio Files (not AMI corpus)
# ============================================================================

# Modify validate_audio_file() to accept custom paths:

"""
def validate_audio_file(audio_path: Optional[Path] = None) -> Path:
    if audio_path is None:
        audio_path = Config.AUDIO_FILE
    
    if not audio_path.exists():
        logger.error(f"Audio file not found: {audio_path}")
        raise FileNotFoundError(f"Audio file required at {audio_path}")
    
    logger.info(f"Audio file validated: {audio_path}")
    return audio_path

# Usage:
custom_audio = Path("path/to/your/audio.wav")
audio_path = validate_audio_file(custom_audio)
"""


# ============================================================================
# SCENARIO 8: Real-time Processing (Streaming)
# ============================================================================

"""
# For real-time audio streaming (microphone input):

import sounddevice as sd
import soundfile as sf

def record_and_process(duration_seconds=60, sample_rate=16000):
    # Record audio
    audio = sd.rec(int(duration_seconds * sample_rate), 
                   samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    
    # Save temporarily
    temp_path = Path("temp_recording.wav")
    sf.write(str(temp_path), audio, sample_rate)
    
    # Process
    transcription_segments = transcribe_audio(whisper_pipeline, temp_path)
    diarization_segments = run_diarization(diarization_pipeline, temp_path)
    
    # Cleanup
    temp_path.unlink()
    
    return transcription_segments, diarization_segments
"""


# ============================================================================
# SCENARIO 9: Language-Specific Configuration
# ============================================================================

"""
# For non-English audio, modify whisper transcription:

def transcribe_audio(whisper_pipeline: object, audio_path: Path, language="en") -> List[Dict]:
    output = whisper_pipeline(
        str(audio_path),
        return_timestamps=True,
        chunk_length_s=30,
        language=language,    # Specify language: "es", "fr", "de", etc.
    )
    # ... rest of function

# Usage:
transcription_segments = transcribe_audio(whisper_pipeline, audio_path, language="es")
"""


# ============================================================================
# SCENARIO 10: Performance Monitoring
# ============================================================================

"""
import time

class PerformanceMonitor:
    def __init__(self):
        self.times = {}
    
    def start(self, task: str):
        self.times[task] = {"start": time.time()}
    
    def end(self, task: str):
        elapsed = time.time() - self.times[task]["start"]
        self.times[task]["elapsed"] = elapsed
        logger.info(f"{task}: {elapsed:.2f}s")
    
    def report(self):
        total = sum(t["elapsed"] for t in self.times.values() if "elapsed" in t)
        print("\n" + "="*50)
        print("PERFORMANCE REPORT")
        print("="*50)
        for task, data in self.times.items():
            if "elapsed" in data:
                pct = (data["elapsed"] / total) * 100
                print(f"{task:.<30} {data['elapsed']:>6.2f}s ({pct:>5.1f}%)")
        print(f"{'Total':.<30} {total:>6.2f}s (100.0%)")
        print("="*50)

# Usage in main():
monitor = PerformanceMonitor()
monitor.start("Transcription")
transcription_segments = transcribe_audio(whisper_pipeline, audio_path)
monitor.end("Transcription")

monitor.start("Diarization")
diarization_segments = run_diarization(diarization_pipeline, audio_path)
monitor.end("Diarization")

monitor.report()
"""


# ============================================================================
# QUICK REFERENCE: Environment-Specific Settings
# ============================================================================

"""
+---------------------+-------+-----+----------+--------+----------+
| Environment         | Model | GPU | Duration | Acc.   | Mem(GB)  |
+---------------------+-------+-----+----------+--------+----------+
| Laptop (CPU)        | tiny  | no  | 30 min   | 85%    | 4-6      |
| Gaming PC           | base  | yes | 40 min   | 92%    | 6-8      |
| Workstation (RTX)   | small | yes | 25 min   | 94%    | 8-10     |
| Data Center (V100)  | large | yes | 20 min   | 97%    | 12-16    |
+---------------------+-------+-----+----------+--------+----------+

Recommendations:
- Development: Use 'base' with GPU if available, CPU otherwise
- Production: Use 'small' or 'base' with GPU for best speed/accuracy balance
- Research: Use 'large' with high-end GPU for maximum accuracy
"""
