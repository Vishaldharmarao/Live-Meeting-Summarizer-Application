"""
Performance Benchmarking and Testing Tool
Measures latency, accuracy, throughput of the real-time transcription system.
"""

import time
import numpy as np
from pathlib import Path
from main import RealtimeTranscriber, calculate_wer, SAMPLE_RATE, MODEL_NAME

def generate_test_audio(duration_seconds, frequency=440):
    """
    Generate synthetic test audio (sine wave).
    
    Args:
        duration_seconds: Length of audio in seconds
        frequency: Frequency of sine wave in Hz
    
    Returns:
        numpy array of audio samples
    """
    t = np.linspace(0, duration_seconds, int(SAMPLE_RATE * duration_seconds))
    audio = 0.3 * np.sin(2 * np.pi * frequency * t).astype(np.float32)
    return audio

def benchmark_model_loading():
    """Benchmark model loading time."""
    print("\n" + "=" * 70)
    print("MODEL LOADING BENCHMARK")
    print("=" * 70)
    
    print(f"\nLoading model: {MODEL_NAME}")
    start_time = time.time()
    
    transcriber = RealtimeTranscriber(model_name=MODEL_NAME)
    
    elapsed = time.time() - start_time
    print(f"✓ Model loaded in {elapsed:.2f} seconds")
    
    return transcriber

def benchmark_transcription_latency(transcriber):
    """Benchmark transcription latency for different audio lengths."""
    print("\n" + "=" * 70)
    print("TRANSCRIPTION LATENCY BENCHMARK")
    print("=" * 70)
    
    durations = [0.5, 1.0, 2.0, 5.0, 10.0]
    results = {}
    
    for duration in durations:
        print(f"\nTesting {duration}s of audio...")
        
        # Generate test audio
        audio = generate_test_audio(duration)
        
        # Measure transcription time
        start_time = time.time()
        segments, info = transcriber.model.transcribe(audio, language="en")
        elapsed = time.time() - start_time
        
        # Calculate real-time factor
        rtf = elapsed / duration
        
        print(f"  Transcription time: {elapsed:.3f}s")
        print(f"  Real-time factor: {rtf:.2f}x")
        print(f"  Speed: {duration/elapsed:.1f}x faster than real-time")
        
        results[duration] = {
            'time': elapsed,
            'rtf': rtf,
            'speed': duration / elapsed
        }
    
    return results

def benchmark_memory_usage():
    """Benchmark memory usage during transcription."""
    print("\n" + "=" * 70)
    print("MEMORY USAGE BENCHMARK")
    print("=" * 70)
    
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Get initial memory
        initial_memory = process.memory_info().rss / (1024 * 1024)
        print(f"\nInitial memory: {initial_memory:.1f} MB")
        
        # Create transcriber (this loads large model)
        print("Loading model...")
        transcriber = RealtimeTranscriber(model_name=MODEL_NAME)
        
        # Get memory after model load
        after_load = process.memory_info().rss / (1024 * 1024)
        print(f"After model load: {after_load:.1f} MB")
        print(f"Model memory: {after_load - initial_memory:.1f} MB")
        
        # Transcribe several samples
        print("Transcribing samples...")
        for i in range(3):
            audio = generate_test_audio(5.0)
            segments, info = transcriber.model.transcribe(audio)
            current = process.memory_info().rss / (1024 * 1024)
            print(f"  Sample {i+1}: {current:.1f} MB")
        
        peak_memory = process.memory_info().rss / (1024 * 1024)
        print(f"\nPeak memory: {peak_memory:.1f} MB")
        print(f"Total usage: {peak_memory - initial_memory:.1f} MB")
        
        return {
            'initial': initial_memory,
            'after_load': after_load,
            'peak': peak_memory,
            'model_size': after_load - initial_memory,
        }
    except ImportError:
        print("psutil not available for memory profiling")
        print("Install with: pip install psutil")
        return None

def benchmark_accuracy():
    """Benchmark transcription accuracy with known samples."""
    print("\n" + "=" * 70)
    print("TRANSCRIPTION ACCURACY BENCHMARK")
    print("=" * 70)
    
    test_cases = [
        "the quick brown fox jumps over the lazy dog",
        "hello world this is a test",
        "artificial intelligence and machine learning",
    ]
    
    print("\nNote: These are synthetic tests.")
    print("Accuracy depends on audio quality and model training.")
    print("Real-world WER < 15% on clear English speech is typical.\n")
    
    transcriber = RealtimeTranscriber(model_name=MODEL_NAME)
    
    results = {}
    
    for i, reference_text in enumerate(test_cases, 1):
        print(f"Test case {i}: '{reference_text}'")
        print("  (In real use, you would speak this text into the microphone)")
        
        # For benchmarking, we just show the expected WER target
        print(f"  Expected WER: < 15% on clear audio")
        results[f'test_{i}'] = reference_text
    
    print("\nTo actually test accuracy:")
    print("  1. Run: python demo.py")
    print("  2. Select option 2: 'Test with Reference Text'")
    print("  3. Read the reference text clearly")
    print("  4. System calculates actual WER automatically")
    
    return results

def full_system_benchmark():
    """Run complete system benchmark."""
    print("\n" * 2)
    print("█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "REAL-TIME SPEECH-TO-TEXT SYSTEM BENCHMARK".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)
    
    print(f"\nModel: {MODEL_NAME}")
    print(f"Sample Rate: {SAMPLE_RATE} Hz")
    
    # 1. Model Loading
    transcriber = benchmark_model_loading()
    
    # 2. Latency
    latency_results = benchmark_transcription_latency(transcriber)
    
    # 3. Memory
    memory_results = benchmark_memory_usage()
    
    # 4. Accuracy guidance
    benchmark_accuracy()
    
    # Summary
    print("\n" + "=" * 70)
    print("BENCHMARK SUMMARY")
    print("=" * 70)
    
    print(f"\nModel: {MODEL_NAME}")
    print(f"Status: ✓ All benchmarks completed")
    
    print("\nKey Metrics:")
    if latency_results:
        # Get 1s transcription
        result_1s = latency_results.get(1.0, {})
        if result_1s:
            print(f"  • 1s transcription: {result_1s['time']:.3f}s "
                  f"({result_1s['speed']:.0f}x real-time)")
    
    if memory_results:
        print(f"  • Model size: {memory_results['model_size']:.0f} MB")
        print(f"  • Peak memory: {memory_results['peak']:.0f} MB")
    
    print("\nFor real-world WER testing:")
    print("  Run: python demo.py")
    print("  Then select option 2: Test with Reference Text")
    
    print("\n" + "=" * 70)

def compare_models():
    """Compare performance across different model sizes."""
    print("\n" + "=" * 70)
    print("MODEL COMPARISON")
    print("=" * 70)
    
    print("\nModel Performance Characteristics:")
    print("-" * 70)
    
    models_info = {
        "tiny": {
            "size": "39 MB",
            "memory": "~1 GB",
            "speed": "⚡⚡⚡ Very Fast",
            "accuracy": "⭐⭐ Low",
        },
        "small": {
            "size": "140 MB",
            "memory": "~2 GB",
            "speed": "⚡⚡ Fast",
            "accuracy": "⭐⭐⭐⭐ High",
        },
        "base": {
            "size": "140 MB",
            "memory": "~3 GB",
            "speed": "⚡ Medium",
            "accuracy": "⭐⭐⭐⭐ High",
        },
        "medium": {
            "size": "769 MB",
            "memory": "~6 GB",
            "speed": "🐢 Slow",
            "accuracy": "⭐⭐⭐⭐⭐ Very High",
        },
        "large": {
            "size": "2.9 GB",
            "memory": "~10 GB",
            "speed": "🐢🐢 Very Slow",
            "accuracy": "⭐⭐⭐⭐⭐ Very High",
        },
    }
    
    for model, info in models_info.items():
        print(f"\n{model.upper()}")
        for key, value in info.items():
            print(f"  {key:12} {value}")
    
    print("\n" + "=" * 70)
    print("RECOMMENDATION: Use 'small' model for optimal balance")
    print("=" * 70)

def main():
    """Main entry point for benchmarking tool."""
    import sys
    
    print("\n" + "=" * 70)
    print("BENCHMARKING TOOL".center(70))
    print("=" * 70)
    
    print("\nOptions:")
    print("  1. Full System Benchmark")
    print("  2. Model Loading Benchmark")
    print("  3. Transcription Latency Benchmark")
    print("  4. Memory Usage Benchmark")
    print("  5. Accuracy Benchmark Guide")
    print("  6. Compare Model Sizes")
    print("  7. Exit")
    
    print("\n" + "-" * 70)
    
    while True:
        choice = input("\nSelect option (1-7): ").strip()
        
        try:
            if choice == '1':
                full_system_benchmark()
            elif choice == '2':
                benchmark_model_loading()
            elif choice == '3':
                transcriber = RealtimeTranscriber(model_name=MODEL_NAME)
                benchmark_transcription_latency(transcriber)
            elif choice == '4':
                benchmark_memory_usage()
            elif choice == '5':
                benchmark_accuracy()
            elif choice == '6':
                compare_models()
            elif choice == '7':
                print("\nGoodbye!")
                break
            else:
                print("[ERROR] Invalid option")
        except KeyboardInterrupt:
            print("\n[INFO] Benchmark cancelled by user")
        except Exception as e:
            print(f"[ERROR] {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBenchmarking tool interrupted.")
        sys.exit(0)
