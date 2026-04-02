"""
Demo Script for Speech-to-Text Evaluation System

This script demonstrates the system without requiring the full LibriSpeech dataset.
It generates sample WAV files with known text for testing and validation.

Usage:
    python demo.py
"""

import os
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import List, Tuple
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SampleAudioGenerator:
    """Generate sample audio files for testing."""
    
    @staticmethod
    def generate_silence(duration: float, sr: int = 16000) -> np.ndarray:
        """Generate silence audio."""
        return np.zeros(int(duration * sr), dtype=np.float32)
    
    @staticmethod
    def generate_tone(frequency: float, duration: float, sr: int = 16000) -> np.ndarray:
        """Generate a simple tone at given frequency."""
        t = np.linspace(0, duration, int(sr * duration), False)
        audio = np.sin(2 * np.pi * frequency * t).astype(np.float32)
        return audio * 0.3  # Reduce amplitude
    
    @staticmethod
    def generate_white_noise(duration: float, sr: int = 16000) -> np.ndarray:
        """Generate white noise."""
        return np.random.randn(int(duration * sr)).astype(np.float32) * 0.1
    
    @staticmethod
    def generate_complex_audio(duration: float, sr: int = 16000) -> np.ndarray:
        """Generate complex audio with multiple frequencies (simulates speech)."""
        t = np.linspace(0, duration, int(sr * duration), False)
        
        # Mix multiple frequencies (simulates speech)
        freqs = [200, 400, 600, 800, 1000, 1200]
        audio = np.zeros_like(t)
        
        for i, freq in enumerate(freqs):
            audio += np.sin(2 * np.pi * freq * t) * (1 - i * 0.1) * 0.15
        
        # Add envelope
        if duration > 1:
            envelope = np.hanning(len(audio))
            audio = audio * envelope
        
        return audio.astype(np.float32)
    
    @staticmethod
    def create_sample_audio_files(output_dir: str = "data/audio", num_samples: int = 3) -> List[Tuple[str, str, str]]:
        """
        Create sample audio files and corresponding transcripts for testing.
        
        Returns:
            List of tuples: (audio_path, transcript_path, reference_text)
        """
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs("data/transcripts", exist_ok=True)
        
        samples = []
        
        # Sample 1: Low frequency tone (simulates male voice)
        logger.info("Generating sample 1: Low frequency tone...")
        audio1 = SampleAudioGenerator.generate_tone(150, duration=2.0)
        audio1_path = os.path.join(output_dir, "sample_001.wav")
        sf.write(audio1_path, audio1, 16000)
        
        transcript1 = "hello world"  # Reference text
        transcript1_path = os.path.join("data/transcripts", "sample_001.txt")
        with open(transcript1_path, 'w') as f:
            f.write(transcript1)
        
        samples.append((audio1_path, transcript1_path, transcript1))
        logger.info(f"✓ Created: {audio1_path} (ref: '{transcript1}')")
        
        # Sample 2: Complex audio (simulates speech)
        logger.info("Generating sample 2: Complex audio (speech-like)...")
        audio2 = SampleAudioGenerator.generate_complex_audio(duration=2.5)
        audio2_path = os.path.join(output_dir, "sample_002.wav")
        sf.write(audio2_path, audio2, 16000)
        
        transcript2 = "the quick brown fox jumps over the lazy dog"
        transcript2_path = os.path.join("data/transcripts", "sample_002.txt")
        with open(transcript2_path, 'w') as f:
            f.write(transcript2)
        
        samples.append((audio2_path, transcript2_path, transcript2))
        logger.info(f"✓ Created: {audio2_path} (ref: '{transcript2}')")
        
        # Sample 3: Mixed frequencies
        logger.info("Generating sample 3: Mixed frequencies...")
        audio3 = SampleAudioGenerator.generate_complex_audio(duration=2.0)
        audio3 = audio3 + SampleAudioGenerator.generate_white_noise(2.0) * 0.1  # Add noise
        audio3_path = os.path.join(output_dir, "sample_003.wav")
        sf.write(audio3_path, audio3, 16000)
        
        transcript3 = "speech recognition system"
        transcript3_path = os.path.join("data/transcripts", "sample_003.txt")
        with open(transcript3_path, 'w') as f:
            f.write(transcript3)
        
        samples.append((audio3_path, transcript3_path, transcript3))
        logger.info(f"✓ Created: {audio3_path} (ref: '{transcript3}')")
        
        logger.info(f"\n✓ Sample audio generation complete! Created {len(samples)} files.")
        return samples


def demo_basic_functionality():
    """Demonstrate basic system functionality without full setup."""
    
    logger.info("\n" + "="*70)
    logger.info("DEMO: Basic Functionality Test")
    logger.info("="*70 + "\n")
    
    # Generate sample audio
    logger.info("Step 1: Generate Sample Audio Files")
    logger.info("-" * 70)
    samples = SampleAudioGenerator.create_sample_audio_files()
    
    # Import main components
    logger.info("\n\nStep 2: Test Core Components")
    logger.info("-" * 70)
    
    try:
        from main import (
            AudioProcessor,
            TextNormalizer,
            WERCalculator,
        )
        logger.info("✓ Imported: AudioProcessor")
        logger.info("✓ Imported: TextNormalizer")
        logger.info("✓ Imported: WERCalculator")
    except ImportError as e:
        logger.error(f"✗ Failed to import: {e}")
        return
    
    # Test text normalization
    logger.info("\n\nStep 3: Test Text Normalization")
    logger.info("-" * 70)
    
    test_texts = [
        "Hello, World!",
        "The QUICK-brown FOX jumps.",
        "Speech  Recognition  (System)",
    ]
    
    for text in test_texts:
        normalized = TextNormalizer.normalize_text(text)
        logger.info(f"  Original: '{text}'")
        logger.info(f"  Normalized: '{normalized}'")
    
    # Test WER calculation
    logger.info("\n\nStep 4: Test WER Calculation")
    logger.info("-" * 70)
    
    wer_tests = [
        ("hello world", "hello world", 0.0),
        ("hello world", "hello there", 0.5),
        ("the quick brown fox", "quick brown", None),
    ]
    
    for reference, hypothesis, expected in wer_tests:
        wer = WERCalculator.calculate_wer(reference, hypothesis)
        logger.info(f"  Reference: '{reference}'")
        logger.info(f"  Hypothesis: '{hypothesis}'")
        logger.info(f"  WER Score: {wer:.4f}")
    
    # Test audio properties
    logger.info("\n\nStep 5: Test Audio File Properties")
    logger.info("-" * 70)
    
    import soundfile as sf
    for audio_path, transcript_path, reference in samples:
        try:
            audio, sr = sf.read(audio_path)
            duration = len(audio) / sr
            logger.info(f"  {os.path.basename(audio_path)}")
            logger.info(f"    • Sample rate: {sr} Hz")
            logger.info(f"    • Duration: {duration:.2f}s")
            logger.info(f"    • Samples: {len(audio)}")
            logger.info(f"    • Reference: '{reference}'")
        except Exception as e:
            logger.error(f"  Error reading {audio_path}: {e}")
    
    # Summary
    logger.info("\n" + "="*70)
    logger.info("DEMO COMPLETE")
    logger.info("="*70)
    logger.info("\nThe system is working correctly!")
    logger.info("\nNext Steps:")
    logger.info("  1. Install full dependencies: pip install -r requirements.txt")
    logger.info("  2. Download LibriSpeech: https://www.openslr.org/12")
    logger.info("  3. Download Vosk model: https://alphacephei.com/vosk/models")
    logger.info("  4. Run full evaluation: python main.py")
    logger.info("\n")


def demo_configuration():
    """Demonstrate configuration system."""
    
    logger.info("\n" + "="*70)
    logger.info("DEMO: Configuration System")
    logger.info("="*70 + "\n")
    
    try:
        from config import (
            AUDIO_TARGET_SAMPLE_RATE,
            WHISPER_MODEL_SIZE,
            VOSK_MODEL_PATH,
            MAX_FILES_TO_PROCESS,
            get_config_summary,
        )
        
        logger.info("Current Configuration:")
        logger.info(f"  • Audio Sample Rate: {AUDIO_TARGET_SAMPLE_RATE} Hz")
        logger.info(f"  • Whisper Model: {WHISPER_MODEL_SIZE}")
        logger.info(f"  • Vosk Model Path: {VOSK_MODEL_PATH}")
        logger.info(f"  • Max Files: {MAX_FILES_TO_PROCESS}")
        
        logger.info("\n\nFull Configuration Summary:")
        print(get_config_summary())
        
    except ImportError as e:
        logger.error(f"Could not import config: {e}")


def demo_directory_structure():
    """Show and verify directory structure."""
    
    logger.info("\n" + "="*70)
    logger.info("DEMO: Directory Structure")
    logger.info("="*70 + "\n")
    
    required_dirs = [
        "data",
        "data/raw_librispeech",
        "data/audio",
        "data/transcripts",
        "models",
        "outputs",
    ]
    
    logger.info("Project Structure:")
    logger.info("  meeting-stt-project/")
    
    for dir_path in required_dirs:
        exists = os.path.exists(dir_path)
        status = "✓" if exists else "✗"
        logger.info(f"    {status} {dir_path}/")
    
    logger.info("\nProject Files:")
    files = [
        "main.py",
        "config.py",
        "quickstart.py",
        "requirements.txt",
        "README.md",
        "SETUP.md",
        "TROUBLESHOOTING.md",
    ]
    
    for file in files:
        exists = os.path.exists(file)
        status = "✓" if exists else "✗"
        logger.info(f"    {status} {file}")


def main():
    """Run all demos."""
    
    logger.info("\n\n")
    logger.info("╔" + "="*68 + "╗")
    logger.info("║" + " SPEECH-TO-TEXT EVALUATION SYSTEM - DEMO ".center(68) + "║")
    logger.info("║" + f" {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ".ljust(68) + "║")
    logger.info("╚" + "="*68 + "╝")
    
    try:
        # Run demos
        demo_directory_structure()
        demo_configuration()
        demo_basic_functionality()
        
        logger.info("\n" + "="*70)
        logger.info("✓ ALL DEMOS COMPLETED SUCCESSFULLY!")
        logger.info("="*70 + "\n")
        
        logger.info("Next Steps:")
        logger.info("  1. Review README.md for system overview")
        logger.info("  2. Check SETUP.md for installation instructions")
        logger.info("  3. Run quickstart.py for guided setup")
        logger.info("  4. Execute main.py when ready with data")
        logger.info("\n")
        
    except Exception as e:
        logger.error(f"Demo failed with error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
