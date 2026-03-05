#!/usr/bin/env python
"""
Quick Setup Guide for Speaker Diarization Pipeline
Run this script to validate your environment and download models
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Verify Python 3.8+"""
    print("✓ Checking Python version...")
    if sys.version_info < (3, 8):
        print(f"  ✗ Python 3.8+ required, found {sys.version}")
        return False
    print(f"  ✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_directories():
    """Verify project structure"""
    print("\n✓ Checking project structure...")
    root = Path(__file__).parent
    dirs = {
        "audio": root / "audio",
        "output": root / "output",
        "annotations": root / "annotations"
    }
    
    for name, path in dirs.items():
        if path.exists():
            print(f"  ✓ {name}/ exists")
        else:
            print(f"  ℹ {name}/ will be created automatically")
    
    return True

def check_main_script():
    """Verify main.py exists"""
    print("\n✓ Checking main script...")
    main_file = Path(__file__).parent / "main.py"
    if main_file.exists():
        print(f"  ✓ main.py found ({main_file.stat().st_size / 1024:.1f} KB)")
        return True
    else:
        print(f"  ✗ main.py not found")
        return False

def check_dependencies():
    """Check installed packages"""
    print("\n✓ Checking dependencies...")
    
    required = {
        "torch": "PyTorch",
        "torchaudio": "TorchAudio",
        "transformers": "Transformers",
        "pyannote": "pyannote.audio",
        "huggingface_hub": "HuggingFace Hub"
    }
    
    missing = []
    for module, name in required.items():
        try:
            __import__(module)
            print(f"  ✓ {name} installed")
        except ImportError:
            print(f"  ✗ {name} NOT found")
            missing.append(module)
    
    if missing:
        print(f"\n  Install missing packages:")
        print(f"  pip install -r requirements.txt")
        return False
    return True

def check_audio_file():
    """Check if audio file exists"""
    print("\n✓ Checking audio file...")
    audio_file = Path(__file__).parent / "audio" / "meeting.wav"
    if audio_file.exists():
        size_mb = audio_file.stat().st_size / (1024 * 1024)
        print(f"  ✓ meeting.wav found ({size_mb:.1f} MB)")
        return True
    else:
        print(f"  ⓘ meeting.wav NOT found")
        print(f"\n  Download from AMI Corpus:")
        print(f"    1. Visit: https://groups.inf.ed.ac.uk/ami/corpus/")
        print(f"    2. Download: ES2002a.Mix-Headset.wav")
        print(f"    3. Place in: audio/meeting.wav")
        return False

def check_hf_token():
    """Check HuggingFace token"""
    print("\n✓ Checking HuggingFace token...")
    token = os.getenv("HF_TOKEN")
    if token:
        masked = token[:10] + "..." + token[-4:]
        print(f"  ✓ HF_TOKEN set ({masked})")
        return True
    else:
        print(f"  ⓘ HF_TOKEN not set (optional)")
        print(f"\n  To set HF_TOKEN:")
        print(f"    PowerShell: $env:HF_TOKEN = 'hf_xxxxxxxxxxxxxxxxxxxx'")
        print(f"    Cmd:       set HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx")
        return True  # Not required, just helpful

def check_gpu():
    """Check GPU availability"""
    print("\n✓ Checking GPU...")
    try:
        import torch
        if torch.cuda.is_available():
            print(f"  ✓ CUDA available: {torch.cuda.get_device_name(0)}")
            print(f"    Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
            return True
        else:
            print(f"  ⓘ CUDA not available (will use CPU)")
            print(f"    For faster processing, install NVIDIA CUDA Toolkit")
            return True
    except Exception as e:
        print(f"  ⓘ GPU check failed: {e}")
        return True

def main():
    print("="*60)
    print("SPEAKER DIARIZATION PIPELINE - SETUP VERIFICATION")
    print("="*60)
    
    checks = [
        ("Python version", check_python_version),
        ("Project structure", check_directories),
        ("Main script", check_main_script),
        ("Audio file", check_audio_file),
        ("HuggingFace token", check_hf_token),
        ("GPU support", check_gpu),
        ("Dependencies", check_dependencies),
    ]
    
    results = {}
    for name, check_fn in checks:
        try:
            results[name] = check_fn()
        except Exception as e:
            print(f"  ✗ Check failed: {e}")
            results[name] = False
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    critical_checks = {
        "Python version": True,
        "Main script": True,
        "Dependencies": True,
        "Audio file": False  # Can be added later
    }
    
    all_critical_pass = all(
        results.get(check, False)
        for check, critical in critical_checks.items()
        if critical
    )
    
    if all_critical_pass:
        print("\n✓ Everything looks good!")
        print("\nTo start the pipeline, run:")
        print("  python main.py")
        print("\n" + "="*60)
        return 0
    else:
        print("\n✗ Some checks failed. Please resolve issues above.")
        print("\n" + "="*60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
