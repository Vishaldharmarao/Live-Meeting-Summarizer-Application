"""
Speech-to-Text Evaluation System using LibriSpeech dev-clean Dataset
=====================================================================

This module compares Vosk and Whisper STT models by evaluating them on
multiple audio files from the LibriSpeech dev-clean dataset.

Features:
- Converts FLAC audio to WAV format
- Transcribes using Vosk and Whisper models
- Calculates Word Error Rate (WER) for each model
- Generates comprehensive evaluation report
- Provides architecture diagram and analysis

Author: Speech-to-Text Evaluation Team
Date: 2024
"""

import os
import glob
import json
import shutil
import string
import wave
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import logging

# Third-party imports
import librosa
import soundfile as sf
import whisper
from jiwer import wer as calculate_jiwer_wer, Compose, ToLowerCase, RemovePunctuation, RemoveMultipleSpaces, Strip
from vosk import Model, KaldiRecognizer


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Helper function for performance ratings
def _get_performance_rating(wer: float) -> str:
    """
    Get performance rating based on WER score.
    
    Args:
        wer: Word Error Rate (0.0 to 1.0+)
        
    Returns:
        Performance rating string with stars
    """
    if wer <= 0.05:
        return "EXCELLENT (0.00-0.05) ⭐⭐⭐⭐⭐"
    elif wer <= 0.10:
        return "GOOD (0.05-0.10) ⭐⭐⭐⭐"
    elif wer <= 0.20:
        return "ACCEPTABLE (0.10-0.20) ⭐⭐⭐"
    elif wer <= 0.30:
        return "POOR (0.20-0.30) ⭐⭐"
    else:
        return "VERY POOR (0.30+) ⭐"


class AudioProcessor:
    """Handles audio file conversions and processing."""
    
    @staticmethod
    def convert_flac_to_wav(flac_path: str, wav_path: str, target_sr: int = 16000) -> bool:
        """
        Convert FLAC audio to WAV format with specified sample rate.
        
        Args:
            flac_path: Path to input FLAC file
            wav_path: Path to output WAV file
            target_sr: Target sample rate (default: 16000 Hz for most STT models)
            
        Returns:
            bool: True if conversion successful, False otherwise
        """
        try:
            # Load audio with librosa (automatically converts to mono if multi-channel)
            audio_data, sr = librosa.load(flac_path, sr=target_sr, mono=True)
            
            # Save as WAV using soundfile
            sf.write(wav_path, audio_data, target_sr)
            logger.info(f"✓ Converted {flac_path} -> {wav_path}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to convert {flac_path}: {e}")
            return False


class TextNormalizer:
    """Handles text normalization for WER calculation using jiwer transformations."""
    
    # Initialize jiwer transformation pipeline for consistent, accurate normalization
    _transformation = Compose([
        ToLowerCase(),           # Convert to lowercase
        RemovePunctuation(),     # Remove punctuation marks
        RemoveMultipleSpaces(),  # Remove multiple consecutive spaces
        Strip()                  # Strip leading/trailing whitespace
    ])
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text for fair WER comparison using jiwer transformations.
        
        This ensures consistent normalization across all texts using the
        industry-standard jiwer library transformations.
        
        Operations:
        - Convert to lowercase
        - Remove punctuation
        - Remove extra whitespace
        - Strip leading/trailing spaces
        
        Args:
            text: Raw text to normalize
            
        Returns:
            str: Normalized text using jiwer transformations
        """
        try:
            return TextNormalizer._transformation(text)
        except Exception as e:
            logger.error(f"Error during text normalization: {e}")
            # Fallback to manual normalization if jiwer transformation fails
            text = text.lower()
            text = text.translate(str.maketrans('', '', string.punctuation))
            text = ' '.join(text.split())
            text = text.strip()
            return text


class LibriSpeechDataset:
    """Manages LibriSpeech dataset preparation and access."""
    
    @staticmethod
    def prepare_librispeech_dataset(raw_path: str, max_files: int = 5) -> List[Tuple[str, str]]:
        """
        Prepare LibriSpeech dev-clean dataset for evaluation.
        
        Process:
        1. Search for .flac files in raw_path/dev-clean
        2. Select first max_files audio files
        3. Convert FLAC to mono 16kHz WAV
        4. Extract corresponding transcripts
        5. Save clean transcripts
        
        Args:
            raw_path: Path to raw_librispeech directory
            max_files: Maximum number of files to process (default: 5)
            
        Returns:
            List[Tuple[str, str]]: List of (wav_path, transcript_path) pairs
            
        Raises:
            FileNotFoundError: If raw_path or dev-clean folder doesn't exist
            ValueError: If no FLAC files found
        """
        dev_clean_path = os.path.join(raw_path, 'dev-clean')
        
        # Validate paths
        if not os.path.exists(raw_path):
            raise FileNotFoundError(f"Raw dataset path not found: {raw_path}")
        
        if not os.path.exists(dev_clean_path):
            raise FileNotFoundError(f"dev-clean subdirectory not found: {dev_clean_path}")
        
        logger.info(f"Searching for FLAC files in {dev_clean_path}...")
        
        # Find all FLAC files (LibriSpeech structure: speaker/chapter/speaker-chapter-seq.flac)
        flac_files = sorted(glob.glob(os.path.join(dev_clean_path, '**/*.flac'), recursive=True))
        
        if not flac_files:
            raise ValueError(f"No FLAC files found in {dev_clean_path}")
        
        # Limit to max_files
        flac_files = flac_files[:max_files]
        logger.info(f"Found {len(flac_files)} FLAC files. Processing first {len(flac_files)}...")
        
        pairs = []
        
        for flac_path in flac_files:
            try:
                # Extract speaker-chapter-seq from filename
                # Example: /path/to/dev-clean/19/198/19-198-0000.flac
                filename = os.path.basename(flac_path)
                file_id = os.path.splitext(filename)[0]  # e.g., "19-198-0000"
                
                # Create output paths
                wav_filename = f"{file_id}.wav"
                txt_filename = f"{file_id}.txt"
                
                wav_path = os.path.join('data/audio', wav_filename)
                transcript_path = os.path.join('data/transcripts', txt_filename)
                
                # Convert FLAC to WAV
                if not AudioProcessor.convert_flac_to_wav(flac_path, wav_path):
                    continue
                
                # Extract transcript from .trans.txt file
                # LibriSpeech structure: speaker/chapter/speaker-chapter.trans.txt
                speaker_chapter = '-'.join(file_id.split('-')[:2])  # "19-198"
                speaker_id = file_id.split('-')[0]  # "19"
                chapter_id = file_id.split('-')[1]  # "198"
                
                trans_file = os.path.join(
                    dev_clean_path,
                    speaker_id,
                    chapter_id,
                    f"{speaker_chapter}.trans.txt"
                )
                
                if not os.path.exists(trans_file):
                    logger.warning(f"Transcript file not found: {trans_file}")
                    continue
                
                # Read transcript line for this file
                transcript = LibriSpeechDataset._extract_transcript(trans_file, file_id)
                
                if not transcript:
                    logger.warning(f"Could not extract transcript for {file_id}")
                    continue
                
                # Save transcript to file
                with open(transcript_path, 'w', encoding='utf-8') as f:
                    f.write(transcript)
                
                logger.info(f"✓ Processed {file_id}: {transcript}")
                pairs.append((wav_path, transcript_path))
                
            except Exception as e:
                logger.error(f"Error processing {flac_path}: {e}")
                continue
        
        if not pairs:
            raise ValueError("No files were successfully processed")
        
        logger.info(f"Dataset preparation complete. Processed {len(pairs)} files.")
        return pairs
    
    @staticmethod
    def _extract_transcript(trans_file: str, file_id: str) -> Optional[str]:
        """
        Extract transcript line for specific file_id from .trans.txt file.
        
        LibriSpeech format: "file_id TRANSCRIPT TEXT HERE"
        Example line: "1272-128104-0000 THIS IS THE TRANSCRIPTION TEXT"
        
        Args:
            trans_file: Path to .trans.txt file
            file_id: File identifier to search for
            
        Returns:
            str: Transcript text (without file ID), or None if not found
        """
        try:
            with open(trans_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(file_id):
                        # Format: "speaker-chapter-seq TRANSCRIPT TEXT"
                        # Split on first space to separate file_id from transcript
                        parts = line.split(' ', 1)
                        if len(parts) == 2:
                            # Return only the transcript text, not the file ID
                            transcript_text = parts[1].strip()
                            return transcript_text if transcript_text else None
        except Exception as e:
            logger.error(f"Error reading transcript file {trans_file}: {e}")
        
        return None


class VoskTranscriber:
    """Handles speech recognition using Vosk model."""
    
    @staticmethod
    def transcribe_vosk(audio_path: str, model_path: str) -> str:
        """
        Transcribe audio using Vosk STT model.
        
        Args:
            audio_path: Path to WAV audio file
            model_path: Path to Vosk model directory
            
        Returns:
            str: Transcribed text
            
        Raises:
            FileNotFoundError: If audio or model path doesn't exist
            ValueError: If audio format is invalid
        """
        # Validate paths
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Vosk model not found: {model_path}")
        
        try:
            # Load Vosk model
            logger.info(f"Loading Vosk model from {model_path}...")
            model = Model(model_path)
            
            # Open WAV file
            with wave.open(audio_path, 'rb') as wf:
                # Verify audio format
                if wf.getnchannels() != 1:
                    raise ValueError("Audio must be mono")
                if wf.getsampwidth() != 2:
                    raise ValueError("Audio must be 16-bit")
                if wf.getframerate() != 16000:
                    raise ValueError("Audio sample rate must be 16000 Hz")
                
                # Create recognizer
                recognizer = KaldiRecognizer(model, wf.getframerate())
                recognizer.SetWords(None)
                
                # Process audio frames
                result_text = ""
                while True:
                    data = wf.readframes(4000)
                    if len(data) == 0:
                        break
                    
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        if 'result' in result:
                            # Extract text from each decoded word using 'term' field (not 'conf')
                            words = [item.get('term') for item in result['result'] if item.get('term')]
                            if words:
                                result_text += ' ' + ' '.join(words)
                
                # Get final result - this is the complete transcription
                final_result = json.loads(recognizer.FinalResult())
                transcription = ""
                
                # Vosk FinalResult returns a simple JSON: {"text": "the actual transcription"}
                if 'text' in final_result:
                    transcription = final_result.get('text', '').strip()
                elif 'result' in final_result and final_result['result']:
                    # Fallback: extract from result array using 'term' field
                    words = [item.get('term') for item in final_result['result'] if item.get('term')]
                    transcription = ' '.join(words) if words else ""
                
                transcription = transcription.strip()
                preview = transcription[:60] if transcription else 'EMPTY'
                logger.info(f"✓ Vosk transcription complete: '{preview}...'")
                return transcription
                
        except Exception as e:
            logger.error(f"Vosk transcription failed for {audio_path}: {e}")
            raise


class WhisperTranscriber:
    """Handles speech recognition using OpenAI Whisper model."""
    
    @staticmethod
    def transcribe_whisper(audio_path: str, model_size: str = "base") -> str:
        """
        Transcribe audio using OpenAI Whisper STT model.
        
        Args:
            audio_path: Path to audio file
            model_size: Whisper model size (tiny, base, small, medium, large)
                       Default: base (optimal balance of speed/accuracy)
            
        Returns:
            str: Transcribed text
            
        Raises:
            FileNotFoundError: If audio file doesn't exist
            ValueError: If model size is invalid
        """
        # Validate path
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        valid_sizes = ["tiny", "base", "small", "medium", "large"]
        if model_size not in valid_sizes:
            raise ValueError(f"Model size must be one of {valid_sizes}")
        
        try:
            logger.info(f"Loading Whisper model: {model_size}...")
            model = whisper.load_model(model_size)
            
            # Load audio with librosa first to bypass ffmpeg requirement
            logger.info(f"Loading audio with librosa...")
            audio_data, sr = librosa.load(audio_path, sr=16000, mono=True)
            
            logger.info(f"Transcribing with Whisper ({model_size})...")
            # Pass numpy array directly to Whisper instead of file path
            result = model.transcribe(audio_data, language="en", verbose=False)
            
            transcription = result['text'].strip()
            logger.info(f"✓ Whisper transcription complete: {transcription[:50]}...")
            return transcription
            
        except Exception as e:
            logger.error(f"Whisper transcription failed for {audio_path}: {e}")
            raise


class WERCalculator:
    """Calculates Word Error Rate (WER) between reference and hypothesis text."""
    
    @staticmethod
    def calculate_wer(reference: str, hypothesis: str, debug: bool = False) -> Tuple[float, Dict]:
        """
        Calculate Word Error Rate (WER) between reference and hypothesis texts.
        
        Formula: WER = (S + D + I) / N
        where:
        - S = number of substitutions
        - D = number of deletions
        - I = number of insertions
        - N = number of words in reference
        
        Args:
            reference: Ground truth text
            hypothesis: Predicted/transcribed text
            debug: If True, return detailed metrics
            
        Returns:
            Tuple of (wer_score, metrics_dict)
            - wer_score: WER score (0.0 to 1.0+ scale)
            - metrics_dict: Dictionary with detailed metrics
        """
        # Normalize both texts using jiwer transformations
        reference_normalized = TextNormalizer.normalize_text(reference)
        hypothesis_normalized = TextNormalizer.normalize_text(hypothesis)
        
        # Create metrics dictionary
        metrics = {
            'reference_raw': reference,
            'hypothesis_raw': hypothesis,
            'reference_normalized': reference_normalized,
            'hypothesis_normalized': hypothesis_normalized,
            'reference_word_count': len(reference_normalized.split()) if reference_normalized else 0,
            'hypothesis_word_count': len(hypothesis_normalized.split()) if hypothesis_normalized else 0,
        }
        
        # Validate normalized texts
        if not reference_normalized:
            logger.warning("⚠ Reference text is empty after normalization")
            metrics['wer'] = 1.0
            metrics['accuracy'] = 0.0
            return 1.0, metrics
        
        if not hypothesis_normalized:
            logger.warning("⚠ Hypothesis text is empty after normalization")
            metrics['wer'] = 1.0
            metrics['accuracy'] = 0.0
            return 1.0, metrics
        
        try:
            # Calculate WER using jiwer
            wer_score = calculate_jiwer_wer(reference_normalized, hypothesis_normalized)
            accuracy = max(0.0, 1.0 - wer_score) * 100  # Convert to percentage
            
            metrics['wer'] = float(wer_score)
            metrics['accuracy_percent'] = float(accuracy)
            
            if debug:
                logger.debug(f"WER Details: ref_words={metrics['reference_word_count']}, "
                           f"hyp_words={metrics['hypothesis_word_count']}, "
                           f"wer={wer_score:.4f}, accuracy={accuracy:.2f}%")
            
            return float(wer_score), metrics
            
        except Exception as e:
            logger.error(f"WER calculation error: {e}")
            metrics['wer'] = 1.0
            metrics['accuracy'] = 0.0
            return 1.0, metrics


class ModelEvaluator:
    """Evaluates STT models on multiple audio files."""
    
    @staticmethod
    def evaluate_models(
        pairs: List[Tuple[str, str]],
        vosk_model_path: str
    ) -> Tuple[List[Dict], float, float]:
        """
        Evaluate both Vosk and Whisper models on multiple audio files.
        
        For each audio file:
        - Transcribe with Vosk
        - Transcribe with Whisper
        - Calculate WER for both
        - Store comparison results
        
        Args:
            pairs: List of (audio_path, transcript_path) tuples
            vosk_model_path: Path to Vosk model directory
            
        Returns:
            Tuple containing:
            - List of result dictionaries with per-file metrics
            - Average Vosk WER
            - Average Whisper WER
        """
        results = []
        vosk_wers = []
        whisper_wers = []
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Starting evaluation on {len(pairs)} files...")
        logger.info(f"{'='*60}\n")
        
        for idx, (audio_path, transcript_path) in enumerate(pairs, 1):
            # Convert to absolute paths (required for Whisper)
            audio_path = os.path.abspath(audio_path)
            transcript_path = os.path.abspath(transcript_path)
            
            filename = os.path.basename(audio_path)
            logger.info(f"\n{'='*70}")
            logger.info(f"[File {idx}/{len(pairs)}] {filename}")
            logger.info(f"{'='*70}")
            
            try:
                # Read reference transcript
                with open(transcript_path, 'r', encoding='utf-8') as f:
                    reference = f.read().strip()
                
                logger.info(f"\n[REFERENCE]")
                logger.info(f"  Raw: {reference}")
                reference_normalized = TextNormalizer.normalize_text(reference)
                logger.info(f"  Normalized: {reference_normalized}")
                
                # Transcribe with Vosk
                logger.info(f"\n[VOSK TRANSCRIPTION]")
                vosk_text = ""
                vosk_wer = 1.0
                vosk_metrics = {}
                try:
                    vosk_text = VoskTranscriber.transcribe_vosk(audio_path, vosk_model_path)
                    
                    # Check if transcription is empty
                    if not vosk_text or not vosk_text.strip():
                        logger.warning("  WARNING: Vosk returned empty transcription - SKIPPING WER")
                        vosk_wer = 1.0
                    else:
                        logger.info(f"  Raw: {vosk_text}")
                        vosk_normalized = TextNormalizer.normalize_text(vosk_text)
                        logger.info(f"  Normalized: {vosk_normalized}")
                        vosk_wer, vosk_metrics = WERCalculator.calculate_wer(reference, vosk_text, debug=True)
                        logger.info(f"  WER: {vosk_wer:.4f} | Accuracy: {100*(1-vosk_wer):.2f}%")
                    
                    vosk_wers.append(vosk_wer)
                except Exception as e:
                    logger.error(f"  ERROR: Vosk failed: {e}")
                    vosk_text = ""
                    vosk_wer = 1.0
                    vosk_wers.append(vosk_wer)
                
                # Transcribe with Whisper
                logger.info(f"\n[WHISPER TRANSCRIPTION]")
                whisper_text = ""
                whisper_wer = 1.0
                whisper_metrics = {}
                try:
                    whisper_text = WhisperTranscriber.transcribe_whisper(audio_path)
                    
                    # Check if transcription is empty
                    if not whisper_text or not whisper_text.strip():
                        logger.warning("  WARNING: Whisper returned empty transcription - SKIPPING WER")
                        whisper_wer = 1.0
                    else:
                        logger.info(f"  Raw: {whisper_text}")
                        whisper_normalized = TextNormalizer.normalize_text(whisper_text)
                        logger.info(f"  Normalized: {whisper_normalized}")
                        whisper_wer, whisper_metrics = WERCalculator.calculate_wer(reference, whisper_text, debug=True)
                        logger.info(f"  WER: {whisper_wer:.4f} | Accuracy: {100*(1-whisper_wer):.2f}%")
                    
                    whisper_wers.append(whisper_wer)
                except Exception as e:
                    logger.error(f"  ERROR: Whisper failed: {e}")
                    whisper_text = ""
                    whisper_wer = 1.0
                    whisper_wers.append(whisper_wer)
                
                # Compare models
                logger.info(f"\n[COMPARISON]")
                if vosk_wer < whisper_wer:
                    logger.info(f"  WINNER: Vosk ({vosk_wer:.4f} < {whisper_wer:.4f})")
                    winner = "Vosk"
                elif whisper_wer < vosk_wer:
                    logger.info(f"  WINNER: Whisper ({whisper_wer:.4f} < {vosk_wer:.4f})")
                    winner = "Whisper"
                else:
                    logger.info(f"  TIE: Both {vosk_wer:.4f}")
                    winner = "Tie"
                
                # Store result with detailed metrics
                result = {
                    'file_index': idx,
                    'filename': filename,
                    'reference': reference,
                    'reference_normalized': reference_normalized,
                    'vosk_transcription': vosk_text,
                    'vosk_wer': vosk_wer,
                    'vosk_accuracy': 100 * (1 - vosk_wer),
                    'vosk_metrics': vosk_metrics,
                    'whisper_transcription': whisper_text,
                    'whisper_wer': whisper_wer,
                    'whisper_accuracy': 100 * (1 - whisper_wer),
                    'whisper_metrics': whisper_metrics,
                    'winner': winner,
                }
                results.append(result)
                
            except Exception as e:
                logger.error(f"Failed to process {audio_path}: {e}")
                continue
        
        # Calculate averages
        avg_vosk_wer = sum(vosk_wers) / len(vosk_wers) if vosk_wers else 1.0
        avg_whisper_wer = sum(whisper_wers) / len(whisper_wers) if whisper_wers else 1.0
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Evaluation Complete!")
        logger.info(f"Average Vosk WER: {avg_vosk_wer:.4f}")
        logger.info(f"Average Whisper WER: {avg_whisper_wer:.4f}")
        logger.info(f"Better Model: {'Whisper' if avg_whisper_wer < avg_vosk_wer else 'Vosk'}")
        logger.info(f"{'='*60}\n")
        
        return results, avg_vosk_wer, avg_whisper_wer


class ReportGenerator:
    """Generates evaluation reports and visualizations."""
    
    @staticmethod
    def generate_report(
        results: List[Dict],
        avg_vosk_wer: float,
        avg_whisper_wer: float,
        output_path: str = "outputs/evaluation_report.txt"
    ) -> None:
        """
        Generate comprehensive evaluation report.
        
        Includes:
        - Per-file comparison results
        - Average WER for each model
        - Best model recommendation
        - Observations and insights
        - Architecture diagram
        
        Args:
            results: List of evaluation result dictionaries
            avg_vosk_wer: Average WER for Vosk model
            avg_whisper_wer: Average WER for Whisper model
            output_path: Path to save report
        """
        # Determine better model
        better_model = "Whisper" if avg_whisper_wer < avg_vosk_wer else "Vosk"
        improvement = abs(avg_vosk_wer - avg_whisper_wer)
        
        report = []
        report.append("=" * 70)
        report.append("SPEECH-TO-TEXT MODEL EVALUATION REPORT")
        report.append("=" * 70)
        report.append(f"\nDataset: LibriSpeech dev-clean")
        report.append(f"Evaluation Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Files Evaluated: {len(results)}")
        
        # Per-file results
        report.append("\n" + "=" * 70)
        report.append("PER-FILE DETAILED RESULTS")
        report.append("=" * 70)
        
        for result in results:
            report.append(f"\nFile {result['file_index']}: {result['filename']}")
            report.append("=" * 70)
            
            report.append(f"\nREFERENCE TRANSCRIPT:")
            report.append(f"  Raw: {result['reference']}")
            report.append(f"  Normalized: {result.get('reference_normalized', TextNormalizer.normalize_text(result['reference']))}")
            
            report.append(f"\nVOSK TRANSCRIPTION:")
            report.append(f"  Raw: {result['vosk_transcription']}")
            report.append(f"  WER Score: {result['vosk_wer']:.4f}")
            report.append(f"  Accuracy: {result.get('vosk_accuracy', 100*(1-result['vosk_wer'])):.2f}%")
            if result.get('vosk_metrics'):
                metrics = result['vosk_metrics']
                report.append(f"  Reference words: {metrics.get('reference_word_count', 0)}")
                report.append(f"  Hypothesis words: {metrics.get('hypothesis_word_count', 0)}")
            
            report.append(f"\nWHISPER TRANSCRIPTION:")
            report.append(f"  Raw: {result['whisper_transcription']}")
            report.append(f"  WER Score: {result['whisper_wer']:.4f}")
            report.append(f"  Accuracy: {result.get('whisper_accuracy', 100*(1-result['whisper_wer'])):.2f}%")
            if result.get('whisper_metrics'):
                metrics = result['whisper_metrics']
                report.append(f"  Reference words: {metrics.get('reference_word_count', 0)}")
                report.append(f"  Hypothesis words: {metrics.get('hypothesis_word_count', 0)}")
            
            # File winner
            winner = result.get('winner', ('Whisper' if result['whisper_wer'] < result['vosk_wer'] else 'Vosk'))
            report.append(f"\nFILE WINNER: {winner}")
        
        # Summary statistics
        report.append("\n" + "=" * 70)
        report.append("SUMMARY STATISTICS")
        report.append("=" * 70)
        
        avg_vosk_accuracy = 100 * (1 - avg_vosk_wer)
        avg_whisper_accuracy = 100 * (1 - avg_whisper_wer)
        
        report.append(f"\nAverage Word Error Rate (WER):")
        report.append(f"  Vosk:    {avg_vosk_wer:.4f} ({avg_vosk_wer*100:.2f}%)")
        report.append(f"  Whisper: {avg_whisper_wer:.4f} ({avg_whisper_wer*100:.2f}%)")
        
        report.append(f"\nAverage Accuracy:")
        report.append(f"  Vosk:    {avg_vosk_accuracy:.2f}%")
        report.append(f"  Whisper: {avg_whisper_accuracy:.2f}%")
        
        report.append(f"\nPerformance Difference:")
        report.append(f"  {better_model} is better by: {improvement:.4f} WER ({improvement*100:.2f}%)")
        
        # Performance ratings
        report.append(f"\nPerformance Ratings:")
        report.append(f"  Vosk WER {avg_vosk_wer:.4f} = {_get_performance_rating(avg_vosk_wer)}")
        report.append(f"  Whisper WER {avg_whisper_wer:.4f} = {_get_performance_rating(avg_whisper_wer)}")
        
        # Recommendations
        report.append("\n" + "=" * 70)
        report.append("RECOMMENDATIONS")
        report.append("=" * 70)
        
        report.append(f"\n>>> RECOMMENDED MODEL: {better_model} <<<")
        
        if better_model == "Whisper":
            report.append(f"\nWhisper outperformed Vosk by {improvement*100:.2f}% in average WER.")
            report.append("\nReasons to use Whisper:")
            report.append("  • Higher accuracy across diverse audio inputs")
            report.append("  • Better handling of accents and speech variations")
            report.append("  • Multilingual support (45+ languages)")
            report.append("  • Robust to background noise")
            report.append("  • Better performance on longer audio files")
            report.append("\nWhen to consider Vosk:")
            report.append("  • Requires offline processing (no API calls)")
            report.append("  • Resource-constrained environments")
            report.append("  • Real-time processing with minimal latency")
        else:
            report.append(f"\nVosk outperformed Whisper by {improvement*100:.2f}% in average WER.")
            report.append("\nReasons to use Vosk:")
            report.append("  • Lightweight and offline capability")
            report.append("  • Lower computational requirements")
            report.append("  • Faster inference speed")
            report.append("  • Good for real-time applications")
            report.append("\nConsider Whisper for:")
            report.append("  • Higher accuracy requirements")
            report.append("  • Multilingual support")
            report.append("  • Non-real-time applications")
        
        # Observations
        report.append("\n" + "=" * 70)
        report.append("OBSERVATIONS & INSIGHTS")
        report.append("=" * 70)
        
        report.append("\n1. Model Characteristics:")
        report.append("   • Vosk: Lightweight, fast, but less accurate for complex speech")
        report.append("   • Whisper: Heavy-weight, slower, but highly accurate")
        
        report.append("\n2. Use Case Scenarios:")
        report.append("   • Mobile/Edge: Prefer Vosk (offline, resource-efficient)")
        report.append("   • Cloud/API: Prefer Whisper (cloud-native, accurate)")
        report.append("   • Voice Commands: Vosk is sufficient")
        report.append("   • Transcription: Whisper is recommended")
        
        report.append("\n3. LibriSpeech Dataset Performance:")
        report.append(f"   • Clean speech samples provide ideal conditions")
        report.append(f"   • Real-world performance may vary with noise/accents")
        
        # Architecture Diagram
        report.append("\n" + "=" * 70)
        report.append("SYSTEM ARCHITECTURE")
        report.append("=" * 70)
        
        report.append("""
              LibriSpeech Audio
                    (FLAC)
                      |
                      v
            ┌─────────────────────┐
            |   Data Preparation  |
            |  (FLAC -> WAV Mono)  |
            └─────────────────────┘
                      |
                      v
            ┌─────────────────────┐
            |    WAV Audio         |
            |   (16kHz, Mono)      |
            └─────────────────────┘
                      |
           ┌──────────┴──────────┐
           v                     v
    ┌────────────────┐  ┌────────────────┐
    |  Vosk Model    |  | Whisper Model  |
    │ (Lightweight)  │  │   (Accurate)   │
    └────────────────┘  └────────────────┘
           |                     |
           v                     v
    ┌────────────────┐  ┌────────────────┐
    |   Vosk Text    |  | Whisper Text   |
    └────────────────┘  └────────────────┘
           |                     |
           └──────────┬──────────┘
                      v
            ┌─────────────────────┐
            |   Text Comparison   |
            |  (WER Calculation)  |
            └─────────────────────┘
                      |
                      v
            ┌─────────────────────┐
            | Evaluation Report   |
            |  & Recommendations  |
            └─────────────────────┘
        """)
        
        # Model comparison table
        report.append("\n" + "=" * 70)
        report.append("MODEL COMPARISON TABLE")
        report.append("=" * 70)
        
        report.append("""
┌─────────────────┬────────────────┬────────────────┐
│ Characteristic  │     Vosk       │    Whisper     │
├─────────────────┼────────────────┼────────────────┤
│ Accuracy        │     Medium     │     High       │
│ Speed           │     Fast       │    Moderate    │
│ Model Size      │   Small (50MB) │  Large (500MB+)│
│ Memory Usage    │     Low        │     High       │
│ Offline Support │     Yes        │     No*        │
│ Multilingual    │     Limited    │     Yes (45+)  │
│ Noise Robustness│     Moderate   │     Good       │
│ Cloud Ready     │     No         │     Yes        │
└─────────────────┴────────────────┴────────────────┘
* Whisper can run offline with proper setup, but requires GPU for speed
        """)
        
        report.append("\n" + "=" * 70)
        report.append("CONCLUSION")
        report.append("=" * 70)
        
        report.append(f"\nBased on evaluation of {len(results)} audio files from LibriSpeech dev-clean:")
        report.append(f"\n{better_model} is the recommended model with:")
        report.append(f"  • Average WER: {min(avg_vosk_wer, avg_whisper_wer):.4f}")
        report.append(f"  • Accuracy: {(1 - min(avg_vosk_wer, avg_whisper_wer))*100:.2f}%")
        report.append(f"  • Performance margin: {improvement*100:.2f}%")
        
        report.append("\n" + "=" * 70)
        report.append("END OF REPORT")
        report.append("=" * 70)
        
        # Write report to file
        report_text = '\n'.join(report)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        logger.info(f"\n✓ Report saved to {output_path}")
        print("\n" + report_text)


def main():
    """
    Main execution function orchestrating the complete evaluation pipeline.
    
    Pipeline:
    1. Define paths
    2. Prepare dataset (FLAC -> WAV conversion)
    3. Evaluate models (Vosk + Whisper)
    4. Generate report
    5. Display results
    """
    try:
        logger.info("\n" + "="*70)
        logger.info("SPEECH-TO-TEXT EVALUATION SYSTEM")
        logger.info("="*70 + "\n")
        
        # Step 1: Define paths
        logger.info("Step 1: Configuration")
        logger.info("-" * 70)
        
        raw_dataset_path = "data/raw_librispeech"
        vosk_model_path = "models/vosk-model-small-en-us-0.15"
        output_report_path = "outputs/evaluation_report.txt"
        
        logger.info(f"Raw dataset path: {raw_dataset_path}")
        logger.info(f"Vosk model path: {vosk_model_path}")
        logger.info(f"Output report path: {output_report_path}")
        
        # Validate Vosk model exists
        if not os.path.exists(vosk_model_path):
            logger.warning(f"\n⚠ Vosk model not found at {vosk_model_path}")
            logger.warning("Download from: https://alphacephei.com/vosk/models")
            logger.warning("Extract to: models/vosk-model-small-en-us-0.15")
        
        # Step 2: Prepare dataset
        logger.info("\n\nStep 2: Dataset Preparation")
        logger.info("-" * 70)
        
        try:
            pairs = LibriSpeechDataset.prepare_librispeech_dataset(
                raw_dataset_path,
                max_files=5
            )
            logger.info(f"\n✓ Dataset ready: {len(pairs)} file pairs prepared")
        except Exception as e:
            logger.error(f"\n✗ Dataset preparation failed: {e}")
            logger.error("\nTo use this system:")
            logger.error("1. Download LibriSpeech dev-clean from: https://www.openslr.org/12")
            logger.error("2. Extract to: data/raw_librispeech/dev-clean/")
            logger.error("3. Ensure structure: data/raw_librispeech/dev-clean/speaker/chapter/*.flac")
            return
        
        # Step 3: Evaluate models
        logger.info("\n\nStep 3: Model Evaluation")
        logger.info("-" * 70)
        
        try:
            results, avg_vosk_wer, avg_whisper_wer = ModelEvaluator.evaluate_models(
                pairs,
                vosk_model_path
            )
        except Exception as e:
            logger.error(f"\n✗ Model evaluation failed: {e}")
            return
        
        # Step 4: Generate report
        logger.info("\n\nStep 4: Report Generation")
        logger.info("-" * 70)
        
        try:
            ReportGenerator.generate_report(
                results,
                avg_vosk_wer,
                avg_whisper_wer,
                output_report_path
            )
        except Exception as e:
            logger.error(f"\n✗ Report generation failed: {e}")
            return
        
        # Step 5: Print summary
        logger.info("\n\nStep 5: Execution Summary")
        logger.info("-" * 70)
        
        logger.info(f"✓ Files processed: {len(pairs)}")
        logger.info(f"✓ Vosk Average WER: {avg_vosk_wer:.4f} ({avg_vosk_wer*100:.2f}%)")
        logger.info(f"✓ Whisper Average WER: {avg_whisper_wer:.4f} ({avg_whisper_wer*100:.2f}%)")
        
        better_model = "Whisper" if avg_whisper_wer < avg_vosk_wer else "Vosk"
        improvement = abs(avg_vosk_wer - avg_whisper_wer)
        logger.info(f"✓ Better Model: {better_model} (+{improvement*100:.2f}% improvement)")
        logger.info(f"✓ Report saved: {output_report_path}")
        
        logger.info("\n" + "="*70)
        logger.info("EVALUATION COMPLETE - SYSTEM READY")
        logger.info("="*70 + "\n")
        
    except Exception as e:
        logger.error(f"\nFatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
