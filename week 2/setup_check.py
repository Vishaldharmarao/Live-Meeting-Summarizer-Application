"""
Configuration Helper and Test Suite for Real-Time Speech-to-Text
Validates system setup, tests components, and provides diagnostics.
"""

import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(text.center(70))
    print("=" * 70)

def print_section(text):
    """Print formatted section."""
    print(f"\n{text}")
    print("-" * 70)

def check_python_version():
    """Check Python version."""
    print_section("Python Version Check")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("✓ Version is compatible (3.8+)")
        return True
    else:
        print("✗ Python 3.8 or later is required")
        return False

def check_packages():
    """Check if all required packages are installed."""
    print_section("Package Installation Check")
    
    packages = {
        'numpy': '1.24.3+',
        'sounddevice': '0.4.5+',
        'faster_whisper': '0.10.0+',
        'jiwer': '3.0.0+',
    }
    
    all_installed = True
    
    for package, required_version in packages.items():
        try:
            module = __import__(package)
            version = getattr(module, '__version__', 'unknown')
            print(f"✓ {package:20} {version}")
        except ImportError:
            print(f"✗ {package:20} NOT INSTALLED (required: {required_version})")
            all_installed = False
    
    return all_installed

def check_torch_and_cuda():
    """Check PyTorch and CUDA availability."""
    print_section("GPU/CUDA Support")
    
    try:
        import torch
        print(f"✓ PyTorch {torch.__version__} installed")
        
        if torch.cuda.is_available():
            print(f"✓ CUDA is AVAILABLE")
            print(f"  GPU: {torch.cuda.get_device_name(0)}")
            print(f"  Compute Capability: {torch.cuda.get_device_capability(0)}")
            print(f"  Total Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
            return True
        else:
            print("✓ PyTorch installed, but CUDA not available (will use CPU)")
            return False
    except ImportError:
        print("✗ PyTorch not installed")
        print("  For GPU support, install: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
        return False

def check_microphone():
    """Check microphone availability."""
    print_section("Microphone Check")
    
    try:
        import sounddevice as sd
        
        devices = sd.query_devices()
        print(f"Total devices: {len(devices)}")
        
        # Find input devices
        input_devices = []
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices.append((i, device))
        
        if input_devices:
            print(f"✓ {len(input_devices)} input device(s) found:\n")
            for device_id, device in input_devices:
                marker = "→ DEFAULT" if device['id'] == sd.default.device[0] else ""
                print(f"  ID {device_id}: {device['name']}")
                print(f"       Channels: {device['max_input_channels']}, "
                      f"Sample Rate: {device['default_samplerate']} Hz {marker}")
            return True
        else:
            print("✗ No input devices found")
            print("  Plug in a microphone and try again")
            return False
    except Exception as e:
        print(f"✗ Error checking microphone: {e}")
        return False

def check_disk_space():
    """Check available disk space."""
    print_section("Disk Space Check")
    
    try:
        import shutil
        
        disk_usage = shutil.disk_usage(Path.cwd())
        free_gb = disk_usage.free / (1024**3)
        total_gb = disk_usage.total / (1024**3)
        
        print(f"Total: {total_gb:.1f} GB")
        print(f"Free:  {free_gb:.1f} GB")
        
        if free_gb > 5:
            print("✓ Sufficient space for Whisper models")
            return True
        else:
            print("✗ Low disk space (need 5+ GB for models)")
            return False
    except Exception as e:
        print(f"✗ Error checking disk space: {e}")
        return False

def benchmark_microphone():
    """Benchmark microphone input."""
    print_section("Microphone Benchmarking")
    print("Recording 2 seconds of audio from microphone...")
    
    try:
        import sounddevice as sd
        import numpy as np
        
        print("Recording... (please be silent)")
        
        # Record 2 seconds
        duration = 2
        sample_rate = 16000
        audio = sd.rec(int(sample_rate * duration), 
                      samplerate=sample_rate, 
                      channels=1, 
                      dtype=np.float32)
        sd.wait()
        
        # Analyze audio
        audio = audio.flatten()
        rms = np.sqrt(np.mean(audio**2))
        peak = np.max(np.abs(audio))
        
        print(f"\nRecording Analysis:")
        print(f"  RMS Level: {rms:.4f} ({20*np.log10(rms+1e-7):.1f} dB)")
        print(f"  Peak Level: {peak:.4f}")
        
        if rms > 0.01:
            print("✓ Good microphone input level detected")
            return True
        else:
            print("⚠ Very low input level - check microphone connection")
            return False
    except Exception as e:
        print(f"✗ Error benchmarking microphone: {e}")
        return False

def test_whisper_model():
    """Test loading Whisper model."""
    print_section("Whisper Model Test")
    
    try:
        print("Loading Whisper 'tiny' model (for quick test)...")
        from faster_whisper import WhisperModel
        
        model = WhisperModel("tiny", device="cpu")
        print("✓ Whisper model loaded successfully")
        
        # Quick transcription test
        import numpy as np
        test_audio = np.zeros(16000, dtype=np.float32)  # 1 second silence
        
        print("Testing transcription (silence test)...")
        segments, info = model.transcribe(test_audio)
        
        print("✓ Transcription test passed")
        return True
    except Exception as e:
        print(f"✗ Error loading Whisper model: {e}")
        print("  This may happen on first run (downloading model)")
        return False

def test_file_write():
    """Test ability to write output files."""
    print_section("File Writing Test")
    
    try:
        test_file = Path("test_write.txt")
        test_file.write_text("test")
        test_file.unlink()
        print("✓ Can write output files in current directory")
        return True
    except Exception as e:
        print(f"✗ Cannot write files: {e}")
        return False

def run_installation_check():
    """Run installation check and provide next steps."""
    print_header("INSTALLATION CHECK")
    
    results = {
        "Python": check_python_version(),
        "Packages": check_packages(),
        "GPU/CUDA": check_torch_and_cuda(),
        "Microphone": check_microphone(),
        "Disk Space": check_disk_space(),
        "File Writing": test_file_write(),
    }
    
    print_header("SUMMARY")
    
    for check, result in results.items():
        status = "✓ PASS" if result else "⚠ ISSUE"
        print(f"{check:20} {status}")
    
    if all(results.values()):
        print("\n✓ All checks passed! Ready to use.")
        print("\nNext steps:")
        print("  1. Run quick test: python -c \"from main import RealtimeTranscriber\"")
        print("  2. Start recording: python main.py")
        print("  3. For menu options: python demo.py")
    else:
        print("\n⚠ Some checks failed. See above for details.")
        print("\nTo fix:")
        if not results["Packages"]:
            print("  pip install -r requirements.txt")
        if not results["GPU/CUDA"]:
            print("  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
        if not results["Microphone"]:
            print("  Ensure microphone is plugged in and not in use by another app")

def run_full_diagnostics():
    """Run full diagnostic suite."""
    print_header("FULL SYSTEM DIAGNOSTICS")
    
    check_python_version()
    check_packages()
    check_torch_and_cuda()
    check_microphone()
    check_disk_space()
    test_file_write()
    
    # Optional: microphone benchmark
    print_section("Optional Tests")
    try:
        benchmark_micro = input("\nBenchmark microphone input? (y/n): ").lower().strip()
        if benchmark_micro == 'y':
            benchmark_microphone()
    except KeyboardInterrupt:
        pass
    
    # Optional: model test
    try:
        test_model = input("\nTest Whisper model loading? (y/n, may download 500MB): ").lower().strip()
        if test_model == 'y':
            test_whisper_model()
    except KeyboardInterrupt:
        pass

def main():
    """Main entry point."""
    print_header("REAL-TIME SPEECH-TO-TEXT SYSTEM")
    print("Configuration Helper & Diagnostic Tool")
    
    print("\nOptions:")
    print("  1. Quick Installation Check")
    print("  2. Full System Diagnostics")
    print("  3. Microphone Benchmark")
    print("  4. Test Whisper Model Load")
    print("  5. Test File Writing")
    print("  6. Exit")
    
    print("\n" + "-" * 70)
    
    while True:
        choice = input("\nSelect option (1-6): ").strip()
        
        try:
            if choice == '1':
                run_installation_check()
            elif choice == '2':
                run_full_diagnostics()
            elif choice == '3':
                benchmark_microphone()
            elif choice == '4':
                test_whisper_model()
            elif choice == '5':
                test_file_write()
            elif choice == '6':
                print("\nGoodbye!")
                break
            else:
                print("[ERROR] Invalid option")
        except KeyboardInterrupt:
            print("\n[INFO] Cancelled by user")
        except Exception as e:
            print(f"[ERROR] {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted.")
        sys.exit(0)
