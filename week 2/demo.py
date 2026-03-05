"""
Demonstration and Testing Script for Real-Time Speech-to-Text
Provides utilities for testing the system and calculating WER with reference text.
"""

import sys
import os
from pathlib import Path
from main import RealtimeTranscriber, print_performance_report, calculate_wer, SAMPLE_RATE, MODEL_NAME

def demo_live_transcription():
    """
    Interactive demo of live real-time transcription.
    Records and transcribes speech continuously until Ctrl+C.
    """
    print("\n" + "=" * 70)
    print("REAL-TIME SPEECH-TO-TEXT DEMO".center(70))
    print("=" * 70)
    print("\nThis demo will:")
    print("  1. Record audio from your microphone")
    print("  2. Transcribe speech in real-time using Whisper")
    print("  3. Display live transcription (like live captions)")
    print("  4. Save results to transcription_log.txt")
    print("  5. Calculate accuracy metrics")
    print("\nNote: First run may take longer as model is downloaded/loaded.")
    
    input("\nPress ENTER to start recording (or Ctrl+C to cancel)...")
    
    # Run main transcription
    transcriber = RealtimeTranscriber(
        model_name=MODEL_NAME,
        sample_rate=SAMPLE_RATE
    )
    
    try:
        transcriber.start()
        
        # Keep running until interrupted
        import threading
        while transcriber.is_running:
            try:
                threading.Event().wait(0.1)
            except KeyboardInterrupt:
                raise
    
    except KeyboardInterrupt:
        print("\n[INFO] Recording stopped by user.")
    
    finally:
        transcriber.stop()
        
        # Save and report
        transcription = transcriber.get_transcription()
        transcriber.save_transcription()
        print_performance_report(transcription)


def test_with_reference():
    """
    Test transcription with reference text for WER calculation.
    User provides reference text and audio is recorded.
    """
    print("\n" + "=" * 70)
    print("WER TEST MODE".center(70))
    print("=" * 70)
    
    print("\nEnter the reference text that you will speak:")
    print("(Press Enter twice when done):\n")
    
    lines = []
    while True:
        line = input()
        if line == "":
            if lines and lines[-1] == "":
                lines.pop()
                break
            lines.append(line)
        else:
            lines.append(line)
    
    reference_text = "\n".join(lines).strip()
    
    if not reference_text:
        print("[ERROR] Reference text cannot be empty.")
        return
    
    print(f"\nReference text ({len(reference_text)} chars):")
    print("-" * 70)
    print(reference_text)
    print("-" * 70)
    
    input("\nPress ENTER to start recording (speak the above text)...")
    
    # Run transcription
    transcriber = RealtimeTranscriber(
        model_name=MODEL_NAME,
        sample_rate=SAMPLE_RATE
    )
    
    try:
        transcriber.start()
        
        import threading
        while transcriber.is_running:
            try:
                threading.Event().wait(0.1)
            except KeyboardInterrupt:
                raise
    
    except KeyboardInterrupt:
        print("\n[INFO] Recording stopped by user.")
    
    finally:
        transcriber.stop()
        transcription = transcriber.get_transcription()
        transcriber.save_transcription()
        print_performance_report(transcription, reference_text)


def check_system():
    """
    Check system requirements and available resources.
    """
    print("\n" + "=" * 70)
    print("SYSTEM CHECK".center(70))
    print("=" * 70)
    
    # Check Python version
    print(f"\nPython Version: {sys.version.split()[0]}")
    
    # Check required packages
    print("\nRequired Packages:")
    packages = {
        'numpy': 'Audio processing',
        'sounddevice': 'Microphone input',
        'faster_whisper': 'Speech-to-text',
        'jiwer': 'WER calculation (optional)',
    }
    
    for package, description in packages.items():
        try:
            __import__(package)
            print(f"  ✓ {package:20} - {description}")
        except ImportError:
            print(f"  ✗ {package:20} - {description} [NOT INSTALLED]")
    
    # Check CUDA
    print("\nGPU Support:")
    try:
        import torch
        if torch.cuda.is_available():
            print(f"  ✓ CUDA Available ({torch.cuda.get_device_name(0)})")
        else:
            print(f"  ✗ CUDA Not Available (will use CPU)")
    except ImportError:
        print(f"  ✗ PyTorch not available (will use CPU)")
    
    # Check microphone
    print("\nMicrophone:")
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        if input_devices:
            print(f"  ✓ {len(input_devices)} input device(s) found")
            for i, device in enumerate(input_devices[:3]):
                print(f"    - {device['name']} (ID: {i})")
        else:
            print(f"  ✗ No input devices found")
    except Exception as e:
        print(f"  ✗ Error checking microphone: {e}")
    
    print("\n" + "=" * 70)


def main():
    """Menu-driven main interface."""
    
    while True:
        print("\n" + "=" * 70)
        print("REAL-TIME SPEECH-TO-TEXT SYSTEM".center(70))
        print("=" * 70)
        print("\nOptions:")
        print("  1. Start Live Transcription Demo")
        print("  2. Test with Reference Text (for WER Calculation)")
        print("  3. System Check")
        print("  4. Exit")
        print("\n" + "-" * 70)
        
        choice = input("Select option (1-4): ").strip()
        
        if choice == '1':
            demo_live_transcription()
        elif choice == '2':
            test_with_reference()
        elif choice == '3':
            check_system()
        elif choice == '4':
            print("\nGoodbye!")
            break
        else:
            print("[ERROR] Invalid option. Please try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user.")
        sys.exit(0)
