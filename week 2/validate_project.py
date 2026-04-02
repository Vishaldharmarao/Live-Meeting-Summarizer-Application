"""
Quick validation script to ensure all components are in place.
Run this before starting the system.
"""

import sys
from pathlib import Path

def check_files():
    """Check if all required files exist."""
    required_files = {
        'main.py': 'Core transcription engine',
        'demo.py': 'Interactive demo',
        'benchmark.py': 'Performance benchmarking',
        'setup_check.py': 'System diagnostics',
        'requirements.txt': 'Package dependencies',
        'README.md': 'Full documentation',
        'GETTING_STARTED.md': 'Quick start guide',
        'PROJECT_SUMMARY.md': 'Project overview',
    }
    
    print("Checking project files...")
    print("-" * 70)
    
    all_found = True
    for filename, description in required_files.items():
        filepath = Path(filename)
        if filepath.exists():
            size = filepath.stat().st_size
            print(f"✓ {filename:30} ({size:,} bytes) - {description}")
        else:
            print(f"✗ {filename:30} MISSING - {description}")
            all_found = False
    
    return all_found

def check_imports():
    """Check if core imports work."""
    print("\nChecking Python imports...")
    print("-" * 70)
    
    imports_ok = True
    
    # Try importing main components
    try:
        from main import RealtimeTranscriber
        print("✓ main.py imports successfully")
    except ImportError as e:
        print(f"✗ main.py import failed: {e}")
        imports_ok = False
    
    try:
        import numpy
        print("✓ numpy available")
    except ImportError:
        print("✗ numpy not installed - run: pip install -r requirements.txt")
        imports_ok = False
    
    try:
        import sounddevice
        print("✓ sounddevice available")
    except ImportError:
        print("✗ sounddevice not installed - run: pip install -r requirements.txt")
        imports_ok = False
    
    try:
        from faster_whisper import WhisperModel
        print("✓ faster-whisper available")
    except ImportError:
        print("✗ faster-whisper not installed - run: pip install -r requirements.txt")
        imports_ok = False
    
    try:
        from jiwer import wer
        print("✓ jiwer available (WER calculation enabled)")
    except ImportError:
        print("⚠ jiwer not installed (optional - for WER calculation)")
    
    return imports_ok

def main():
    """Run all validation checks."""
    print("\n" + "=" * 70)
    print("PROJECT VALIDATION".center(70))
    print("=" * 70 + "\n")
    
    files_ok = check_files()
    imports_ok = check_imports()
    
    print("\n" + "=" * 70)
    
    if files_ok and imports_ok:
        print("\n✓ Project is ready to use!")
        print("\nQuick start:")
        print("  1. python main.py          (Start live transcription)")
        print("  2. python demo.py          (Interactive menu)")
        print("  3. python setup_check.py   (System diagnostics)")
        print("  4. python benchmark.py     (Performance testing)")
        return 0
    else:
        print("\n⚠ Some checks failed. Fix the issues above.")
        if not imports_ok:
            print("\nTo install dependencies, run:")
            print("  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
