"""
Speaker Diarization + Speech-to-Text Pipeline
Author: Vishal
Week 3 Project: AMI Corpus Analysis

This script performs:
  1. Audio file validation
  2. Speech transcription (Whisper)
  3. Speaker diarization (pyannote)
  4. Result merging with overlap logic
  5. Transcript generation and saving
  6. Performance metrics (optional)
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import json
from datetime import timedelta

import torch
import soundfile as sf
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from pyannote.audio import Pipeline as DiarizationPipeline
from pyannote.core import Segment

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('speaker_diarization.log')
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Configuration for the pipeline."""
    
    # Paths
    WORKSPACE_ROOT = Path(__file__).parent
    AUDIO_DIR = WORKSPACE_ROOT / "audio"
    OUTPUT_DIR = WORKSPACE_ROOT / "output"
    ANNOTATIONS_DIR = WORKSPACE_ROOT / "annotations"
    
    AUDIO_FILE = AUDIO_DIR / "meeting.wav"
    OUTPUT_TRANSCRIPT = OUTPUT_DIR / "final_transcript.txt"
    OUTPUT_METADATA = OUTPUT_DIR / "transcript_metadata.json"
    REFERENCE_RTTM = ANNOTATIONS_DIR / "reference.rttm"
    
    # Models
    WHISPER_MODEL = "base"
    DIARIZATION_MODEL = "pyannote/speaker-diarization-3.0"
    
    # Device
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Diarization parameters
    MIN_OVERLAP = 0.5  # 50% overlap threshold for matching transcription to diarization
    
    @classmethod
    def ensure_dirs(cls):
        """Ensure all required directories exist."""
        cls.AUDIO_DIR.mkdir(parents=True, exist_ok=True)
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.ANNOTATIONS_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured directories exist: {cls.AUDIO_DIR}, {cls.OUTPUT_DIR}, {cls.ANNOTATIONS_DIR}")

# ============================================================================
# AUDIO VALIDATION
# ============================================================================

def validate_audio_file() -> Path:
    """
    Validate audio file exists. If not, provide user instructions.
    
    Returns:
        Path: Path to audio file
        
    Raises:
        FileNotFoundError: If audio file doesn't exist
    """
    Config.ensure_dirs()
    
    if not Config.AUDIO_FILE.exists():
        logger.error(f"Audio file not found: {Config.AUDIO_FILE}")
        print("\n" + "="*70)
        print("AUDIO FILE NOT FOUND")
        print("="*70)
        print(f"\nExpected location: {Config.AUDIO_FILE}")
        print("\nPlease download from AMI Corpus:")
        print("  Meeting: ES2002a")
        print("  Audio Type: Headset Mix")
        print("  Expected filename: ES2002a.Mix-Headset.wav")
        print(f"\nDownload steps:")
        print("  1. Visit: https://groups.inf.ed.ac.uk/ami/corpus/")
        print("  2. Download meeting ES2002a")
        print("  3. Extract the Mix-Headset audio file")
        print(f"  4. Place it in: {Config.AUDIO_DIR}/")
        print(f"  5. Rename to: meeting.wav")
        print("="*70 + "\n")
        raise FileNotFoundError(f"Audio file required at {Config.AUDIO_FILE}")
    
    logger.info(f"Audio file validated: {Config.AUDIO_FILE}")
    return Config.AUDIO_FILE

# ============================================================================
# MODEL LOADING
# ============================================================================

def load_models() -> Tuple[object, object]:
    """
    Load Whisper and pyannote diarization models.
    
    Returns:
        Tuple[whisper_pipeline, diarization_pipeline]
    """
    logger.info("Loading models...")
    logger.info(f"Using device: {Config.DEVICE}")
    logger.info("Audio backend: soundfile (libtorchcodec bypass)")
    
    # Load Whisper model
    logger.info(f"Loading Whisper {Config.WHISPER_MODEL} model...")
    device = "cuda" if str(Config.DEVICE) == "cuda" else "cpu"
    device_id = 0 if device == "cuda" else -1
    
    try:
        whisper_pipeline = pipeline(
            "automatic-speech-recognition",
            model=f"openai/whisper-{Config.WHISPER_MODEL}",
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            device=device_id,
            model_kwargs={"use_flash_attention_2": False}
        )
        logger.info(f"Whisper {Config.WHISPER_MODEL} loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load Whisper model: {e}")
        raise
    
    # Load pyannote diarization model
    logger.info(f"Loading diarization model: {Config.DIARIZATION_MODEL}")
    
    # ❌ SECURITY: NEVER hardcode API tokens in source code!
    # Tokens should ALWAYS be loaded from environment variables.
    # This keeps secrets safe and prevents accidental exposure to GitHub/version control.
    hf_token = os.getenv("HF_TOKEN")
    
    if not hf_token:
        error_msg = (
            "\n" + "="*70 + "\n"
            "ERROR: HF_TOKEN environment variable not set!\n"
            "="*70 + "\n"
            "The Hugging Face token is required to download the diarization model.\n\n"
            "To set it, run one of the following commands:\n\n"
            "Linux/macOS:\n"
            "  export HF_TOKEN='hf_xxxxxxxxxxxxxxxxxxxx'\n\n"
            "Windows (PowerShell):\n"
            "  $env:HF_TOKEN = 'hf_xxxxxxxxxxxxxxxxxxxx'\n\n"
            "Windows (Command Prompt):\n"
            "  set HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx\n\n"
            "To get your token:\n"
            "  1. Go to https://huggingface.co/settings/tokens\n"
            "  2. Create a new token with 'read' permissions\n"
            "  3. Set it as the HF_TOKEN environment variable\n"
            "="*70 + "\n"
        )
        logger.error(error_msg)
        raise EnvironmentError(error_msg)
    
    logger.info("HF_TOKEN loaded securely from environment variable.")
    
    try:
        diarization_pipeline = DiarizationPipeline.from_pretrained(
            Config.DIARIZATION_MODEL,
            token=hf_token
        )
        diarization_pipeline.to(Config.DEVICE)
        logger.info(f"Diarization model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load diarization model: {e}")
        raise
    
    return whisper_pipeline, diarization_pipeline

# ============================================================================
# TRANSCRIPTION
# ============================================================================

def transcribe_audio(whisper_pipeline: object, audio_path: Path) -> List[Dict]:
    """
    Transcribe audio using Whisper.
    
    Args:
        whisper_pipeline: Loaded Whisper pipeline
        audio_path: Path to audio file
        
    Returns:
        List of segments: [{"start": float, "end": float, "text": str}, ...]
    """
    logger.info(f"Transcribing audio: {audio_path}")
    
    try:
        # Load audio using soundfile (avoids torchaudio/torchcodec issues)
        audio_data, sr = sf.read(str(audio_path))
        waveform = torch.tensor(audio_data).float()
        
        # Convert stereo to mono if needed
        if waveform.ndim == 2:
            waveform = waveform.mean(dim=1)
        
        logger.info(f"Audio loaded: {sr}Hz, shape={waveform.shape}")
        
        # Transcribe with timestamps (use waveform directly, avoid ffmpeg)
        output = whisper_pipeline({
            "raw": waveform.numpy(),
            "sampling_rate": sr
        },
            return_timestamps=True,
            chunk_length_s=30
        )
        
        if "chunks" in output:
            segments = output["chunks"]
        else:
            # Fallback if chunks not available
            segments = [{"timestamp": [0, None], "text": output.get("text", "")}]
        
        # Process segments to extract start, end, text
        processed_segments = []
        for segment in segments:
            if isinstance(segment, dict):
                if "timestamp" in segment:
                    ts = segment["timestamp"]
                    start = ts[0] if ts[0] is not None else 0.0
                    end = ts[1] if ts[1] is not None else start + 1.0
                elif "start" in segment and "end" in segment:
                    start = segment["start"]
                    end = segment["end"]
                else:
                    # Default timing
                    start = 0.0
                    end = 1.0
                
                processed_segments.append({
                    "start": float(start),
                    "end": float(end),
                    "text": segment.get("text", "").strip()
                })
        
        logger.info(f"Transcription complete: {len(processed_segments)} segments")
        return processed_segments
        
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise

# ============================================================================
# DIARIZATION
# ============================================================================

def run_diarization(diarization_pipeline: object, audio_path: Path) -> List[Dict]:
    """
    Run speaker diarization using pyannote.
    
    Args:
        diarization_pipeline: Loaded diarization pipeline
        audio_path: Path to audio file
        
    Returns:
        List of speaker segments: [{"start": float, "end": float, "speaker": str}, ...]
    """
    logger.info(f"Running diarization on: {audio_path}")
    
    try:
        # Load audio manually to avoid torchaudio/torchcodec ffmpeg dependency
        waveform_np, sr = sf.read(str(audio_path))
        waveform = torch.tensor(waveform_np).float()

        # Convert stereo to mono if necessary
        if waveform.ndim == 2:
            waveform = waveform.mean(dim=1)

        logger.info(f"Audio loaded for diarization: {sr}Hz, shape={waveform.shape}")

        # Pass waveform and sample_rate directly to the pipeline (bypass file-based loader)
        diarization = diarization_pipeline({
            "waveform": waveform.unsqueeze(0),
            "sample_rate": sr
        })

        # Extract speaker segments from DiarizeOutput via speaker_diarization annotation
        annotation = diarization.speaker_diarization
        speaker_segments = []
        for segment, _, speaker in annotation.itertracks(yield_label=True):
            speaker_segments.append({
                "start": float(segment.start),
                "end": float(segment.end),
                "speaker": str(speaker)
            })

        # Sort by start time
        speaker_segments.sort(key=lambda x: x["start"])

        logger.info(f"Diarization complete: {len(speaker_segments)} speaker segments")
        return speaker_segments

    except Exception as e:
        logger.error(f"Diarization failed: {e}")
        raise

# ============================================================================
# RESULT MERGING
# ============================================================================

def calculate_overlap(segment1: Dict, segment2: Dict) -> float:
    """
    Calculate overlap ratio between two segments.
    
    Args:
        segment1, segment2: Segments with "start" and "end" keys
        
    Returns:
        float: Overlap ratio (0.0 to 1.0)
    """
    start1, end1 = segment1["start"], segment1["end"]
    start2, end2 = segment2["start"], segment2["end"]
    
    overlap_start = max(start1, start2)
    overlap_end = min(end1, end2)
    
    if overlap_start >= overlap_end:
        return 0.0
    
    overlap_duration = overlap_end - overlap_start
    segment1_duration = end1 - start1
    
    # Return overlap ratio relative to segment1
    return overlap_duration / segment1_duration if segment1_duration > 0 else 0.0

def merge_results(
    transcription_segments: List[Dict],
    diarization_segments: List[Dict],
    min_overlap_threshold: float = 0.5
) -> List[Dict]:
    """
    Merge transcription and diarization results.
    
    For each transcription segment, find the diarization segment with
    maximum overlap. If overlap exceeds threshold, assign that speaker.
    
    Args:
        transcription_segments: Output from Whisper
        diarization_segments: Output from diarization model
        min_overlap_threshold: Minimum overlap ratio (0.0-1.0)
        
    Returns:
        List of merged segments with speaker labels
    """
    logger.info("Merging transcription and diarization results...")
    
    merged_segments = []
    
    for trans_seg in transcription_segments:
        if not trans_seg.get("text") or not trans_seg["text"].strip():
            continue
        
        # Find diarization segment with maximum overlap
        max_overlap = 0.0
        best_speaker = "Unknown"
        
        for dia_seg in diarization_segments:
            overlap = calculate_overlap(trans_seg, dia_seg)
            if overlap > max_overlap:
                max_overlap = overlap
                best_speaker = dia_seg["speaker"]
        
        # Use speaker only if overlap exceeds threshold
        if max_overlap < min_overlap_threshold:
            best_speaker = "Unknown"
        
        merged_segments.append({
            "start": trans_seg["start"],
            "end": trans_seg["end"],
            "text": trans_seg["text"],
            "speaker": best_speaker,
            "overlap_confidence": max_overlap
        })
    
    logger.info(f"Merged {len(merged_segments)} segments")
    return merged_segments

# ============================================================================
# SPEAKER MAPPING
# ============================================================================

def map_speaker_labels(merged_segments: List[Dict]) -> Tuple[List[Dict], Dict]:
    """
    Map speaker IDs to human-readable labels.
    
    Converts SPEAKER_00 → Speaker 1, SPEAKER_01 → Speaker 2, etc.
    
    Args:
        merged_segments: Merged segments with speaker IDs
        
    Returns:
        Tuple of (updated_segments, speaker_mapping_dict)
    """
    logger.info("Mapping speaker labels...")
    
    # Extract unique speakers
    unique_speakers = set()
    for seg in merged_segments:
        if seg["speaker"] != "Unknown":
            unique_speakers.add(seg["speaker"])
    
    # Sort for consistent mapping
    sorted_speakers = sorted(list(unique_speakers))
    
    # Create mapping
    speaker_mapping = {}
    for idx, speaker_id in enumerate(sorted_speakers):
        speaker_mapping[speaker_id] = f"Speaker {idx + 1}"
    
    # Apply mapping
    updated_segments = []
    for seg in merged_segments:
        new_seg = seg.copy()
        if seg["speaker"] in speaker_mapping:
            new_seg["speaker_label"] = speaker_mapping[seg["speaker"]]
        else:
            new_seg["speaker_label"] = "Unknown"
        updated_segments.append(new_seg)
    
    logger.info(f"Mapped {len(speaker_mapping)} speakers")
    logger.info(f"Speaker mapping: {speaker_mapping}")
    
    return updated_segments, speaker_mapping

# ============================================================================
# TRANSCRIPT FORMATTING
# ============================================================================

def format_timestamp(seconds: float) -> str:
    """Format seconds as HH:MM:SS.mmm"""
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

def format_transcript(segments: List[Dict]) -> str:
    """
    Format merged segments into readable transcript.
    
    Args:
        segments: Merged and speaker-mapped segments
        
    Returns:
        Formatted transcript string
    """
    lines = []
    current_speaker = None
    
    for seg in segments:
        speaker = seg.get("speaker_label", "Unknown")
        text = seg.get("text", "").strip()
        timestamp = format_timestamp(seg["start"])
        
        if not text:
            continue
        
        # Add speaker change indicator
        if speaker != current_speaker:
            lines.append("")  # Blank line for readability
            current_speaker = speaker
        
        # Format: [timestamp] Speaker: Text
        line = f"[{timestamp}] {speaker}: {text}"
        lines.append(line)
    
    return "\n".join(lines)

# ============================================================================
# SAVING RESULTS
# ============================================================================

def save_transcript(
    formatted_transcript: str,
    segments: List[Dict],
    speaker_mapping: Dict,
    device: str
) -> None:
    """
    Save transcript and metadata to files.
    
    Args:
        formatted_transcript: Formatted transcript string
        segments: Merged segments
        speaker_mapping: Speaker ID to label mapping
        device: Device used (cuda/cpu)
    """
    logger.info("Saving results...")
    
    Config.ensure_dirs()
    
    # Save formatted transcript
    with open(Config.OUTPUT_TRANSCRIPT, "w", encoding="utf-8") as f:
        f.write(formatted_transcript)
    logger.info(f"Transcript saved to: {Config.OUTPUT_TRANSCRIPT}")
    
    # Save metadata
    metadata = {
        "device": device,
        "num_speakers": len(speaker_mapping),
        "num_segments": len(segments),
        "speaker_mapping": speaker_mapping,
        "duration_seconds": max([s["end"] for s in segments]) if segments else 0,
        "segments": segments
    }
    
    with open(Config.OUTPUT_METADATA, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Metadata saved to: {Config.OUTPUT_METADATA}")

# ============================================================================
# METRICS (OPTIONAL)
# ============================================================================

def calculate_der(diarization_segments: List[Dict]) -> Optional[Dict]:
    """
    Calculate Diarization Error Rate (DER) if reference RTTM available.
    
    Args:
        diarization_segments: Diarization output
        
    Returns:
        Dictionary with DER metrics or None
    """
    if not Config.REFERENCE_RTTM.exists():
        logger.info("No reference RTTM file found. Skipping DER calculation.")
        return None
    
    try:
        from pyannote.metrics.diarization import DiarizationErrorRate
        from pyannote.database.util import load_rttm
        
        logger.info(f"Computing DER using reference: {Config.REFERENCE_RTTM}")
        
        # Load reference
        reference = load_rttm(str(Config.REFERENCE_RTTM))
        
        # This is a simplified version - full implementation would need
        # to properly format the hypothesis from diarization_segments
        logger.info("DER calculation requires proper reference RTTM format")
        return None
        
    except Exception as e:
        logger.warning(f"Could not calculate DER: {e}")
        return None

# ============================================================================
# SUMMARY REPORT
# ============================================================================

def print_summary(
    segments: List[Dict],
    speaker_mapping: Dict,
    device: str,
    metadata: Dict
) -> None:
    """
    Print pipeline summary report.
    
    Args:
        segments: Final merged segments
        speaker_mapping: Speaker mapping dict
        device: Device used
        metadata: Metadata dictionary
    """
    duration = metadata.get("duration_seconds", 0)
    minutes = int(duration) // 60
    seconds = int(duration) % 60
    
    print("\n" + "="*70)
    print("SPEAKER DIARIZATION + SPEECH-TO-TEXT SUMMARY")
    print("="*70)
    print(f"Device Used:              {device.upper()}")
    print(f"Total Speakers Detected:  {len(speaker_mapping)}")
    print(f"Total Speech Segments:    {len(segments)}")
    print(f"Total Duration:           {minutes}:{seconds:02d}")
    print(f"\nSpeaker Mapping:")
    for speaker_id, speaker_label in sorted(speaker_mapping.items()):
        print(f"  {speaker_id} → {speaker_label}")
    print(f"\nOutput Files:")
    print(f"  Transcript:  {Config.OUTPUT_TRANSCRIPT}")
    print(f"  Metadata:    {Config.OUTPUT_METADATA}")
    print("="*70 + "\n")

# ============================================================================
# MAIN PIPELINE
# ============================================================================

def main():
    """Execute the complete speaker diarization pipeline."""
    try:
        logger.info("="*70)
        logger.info("Starting Speaker Diarization + Speech-to-Text Pipeline")
        logger.info("="*70)
        
        # Step 1: Validate audio file
        audio_path = validate_audio_file()
        
        # Step 2: Load models
        whisper_pipeline, diarization_pipeline = load_models()
        
        # Step 3: Transcribe audio
        transcription_segments = transcribe_audio(whisper_pipeline, audio_path)
        
        # Step 4: Run diarization
        diarization_segments = run_diarization(diarization_pipeline, audio_path)
        
        # Step 5: Merge results
        merged_segments = merge_results(
            transcription_segments,
            diarization_segments,
            min_overlap_threshold=Config.MIN_OVERLAP
        )
        
        # Step 6: Map speaker labels
        labeled_segments, speaker_mapping = map_speaker_labels(merged_segments)
        
        # Step 7: Format transcript
        formatted_transcript = format_transcript(labeled_segments)
        
        # Step 8: Save results
        device_name = str(Config.DEVICE).upper()
        save_transcript(formatted_transcript, labeled_segments, speaker_mapping, device_name)
        
        # Step 9: Calculate metrics (optional)
        der_metrics = calculate_der(diarization_segments)
        
        # Step 10: Print summary
        metadata = {
            "device": device_name,
            "num_speakers": len(speaker_mapping),
            "num_segments": len(labeled_segments),
            "duration_seconds": max([s["end"] for s in labeled_segments]) if labeled_segments else 0
        }
        print_summary(labeled_segments, speaker_mapping, device_name, metadata)
        
        logger.info("="*70)
        logger.info("Pipeline completed successfully!")
        logger.info("="*70)
        
    except FileNotFoundError as e:
        logger.critical(f"File error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
