"""
Quick Start Guide for Speech-to-Text Evaluation System

This script provides an interactive setup and execution guide.
Run this to get started quickly with the evaluation system.
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(text.center(70))
    print("=" * 70 + "\n")


def print_section(text: str):
    """Print a formatted section header."""
    print(f"\n{'─' * 70}")
    print(f"  {text}")
    print(f"{'─' * 70}\n")


def check_python_version():
    """Check if Python version is 3.10 or higher."""
    print_section("✓ Checking Python Version")
    version = sys.version_info
    required_version = (3, 10)
    
    if version[:2] >= required_version:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor} found")
        print(f"✗ Python 3.10+ required")
        return False


def check_directory_structure():
    """Check if required directories exist."""
    print_section("✓ Checking Directory Structure")
    
    required_dirs = [
        "data/raw_librispeech",
        "data/audio",
        "data/transcripts",
        "models",
        "outputs"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✓ {dir_path}/")
        else:
            print(f"✗ {dir_path}/ - Creating...")
            os.makedirs(dir_path, exist_ok=True)
            print(f"✓ {dir_path}/ - Created")
            all_exist = False
    
    return all_exist


def check_dependencies():
    """Check if required Python packages are installed."""
    print_section("✓ Checking Dependencies")
    
    required_packages = {
        'librosa': 'librosa',
        'soundfile': 'soundfile',
        'whisper': 'openai-whisper',
        'vosk': 'vosk',
        'jiwer': 'jiwer',
    }
    
    missing_packages = []
    
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - NOT installed")
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(f"\n✗ Missing packages: {', '.join(missing_packages)}")
        print(f"\nTo install, run:")
        print(f"  pip install -r requirements.txt")
        return False
    
    return True


def check_models():
    """Check if required models are downloaded."""
    print_section("✓ Checking Models")
    
    # Check Vosk model
    vosk_model_path = "models/vosk-model-small-en-us-0.15"
    if os.path.exists(vosk_model_path):
        print(f"✓ Vosk model found: {vosk_model_path}/")
    else:
        print(f"⚠ Vosk model NOT found: {vosk_model_path}/")
        print(f"\n  Download from: https://alphacephei.com/vosk/models")
        print(f"  Extract to: {vosk_model_path}/")
    
    print(f"\n  Whisper models will be downloaded automatically on first run")
    print(f"  (~500MB for 'base' model - change WHISPER_MODEL_SIZE in config.py)")


def check_dataset():
    """Check if LibriSpeech dataset is available."""
    print_section("✓ Checking LibriSpeech Dataset")
    
    dataset_path = "data/raw_librispeech/dev-clean"
    
    if os.path.exists(dataset_path):
        flac_files = list(Path(dataset_path).glob("**/*.flac"))
        if flac_files:
            print(f"✓ LibriSpeech dev-clean found")
            print(f"  Location: {dataset_path}/")
            print(f"  Audio files: {len(flac_files)} FLAC files detected")
            return True
        else:
            print(f"✗ No FLAC files found in: {dataset_path}/")
    else:
        print(f"✗ Dataset NOT found: {dataset_path}/")
    
    print(f"\n  Download from: https://www.openslr.org/12")
    print(f"  Extract 'dev-clean' to: data/raw_librispeech/dev-clean/")
    print(f"\n  Folder structure should be:")
    print(f"    data/raw_librispeech/dev-clean/")
    print(f"      ├── 1272/")
    print(f"      │   ├── 128104/")
    print(f"      │   │   ├── 1272-128104-0000.flac")
    print(f"      │   │   └── 1272-128104.trans.txt")
    print(f"      │   └── ...")
    print(f"      └── ...")
    
    return False


def show_configuration():
    """Show current configuration."""
    print_section("✓ Current Configuration")
    
    try:
        from config import get_config_summary
        print(get_config_summary())
    except ImportError:
        print("Note: Run config.py to view full configuration")


def run_evaluation():
    """Run the evaluation system."""
    print_section("Starting Evaluation System")
    
    try:
        from main import main
        main()
    except Exception as e:
        print(f"✗ Error running evaluation: {e}")
        return False
    
    return True


def main_menu():
    """Display main menu and get user choice."""
    print_header("SPEECH-TO-TEXT EVALUATION SYSTEM")
    
    print("Welcome! Let's set up and run your evaluation system.\n")
    
    print("What would you like to do?\n")
    print("  1. Run full setup and checks")
    print("  2. Check system requirements only")
    print("  3. View configuration")
    print("  4. Download instructions")
    print("  5. Run evaluation (if setup complete)")
    print("  6. Exit")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    return choice


def download_instructions():
    """Show download instructions."""
    print_section("Download Instructions")
    
    print("STEP 1: Download LibriSpeech dev-clean (~1.6GB)")
    print("  1. Go to: https://www.openslr.org/12")
    print("  2. Download the 'dev-clean' file")
    print("  3. Extract to: data/raw_librispeech/dev-clean/")
    print("  4. Verify structure has speaker/chapter/audio.flac files")
    
    print("\n\nSTEP 2: Download Vosk Model (~50MB)")
    print("  1. Go to: https://alphacephei.com/vosk/models")
    print("  2. Download 'vosk-model-small-en-us-0.15'")
    print("  3. Extract to: models/vosk-model-small-en-us-0.15/")
    print("  4. Verify it has: am/, conf/, graph/, ivector/ directories")
    
    print("\n\nSTEP 3: Install Python Dependencies")
    print("  Run: pip install -r requirements.txt")
    
    print("\n\nSTEP 4: Run Evaluation")
    print("  Run: python main.py")
    
    print("\nWhisper models will be auto-downloaded (~500MB+)")


def run_setup_checks():
    """Run all setup checks."""
    print_header("SETUP VERIFICATION")
    
    checks = [
        ("Python Version", check_python_version),
        ("Directory Structure", check_directory_structure),
        ("Dependencies", check_dependencies),
        ("Models", check_models),
        ("Dataset", check_dataset),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Error in {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 70)
    print("SETUP CHECK SUMMARY")
    print("=" * 70 + "\n")
    
    for name, result in results:
        status = "✓ OK" if result else "✗ NEEDS ATTENTION"
        print(f"  {name:.<50} {status}")
    
    all_ok = all(result for _, result in results)
    
    if all_ok:
        print("\n✓ All checks passed! Ready to run evaluation.")
    else:
        print("\n⚠ Some checks need attention. See above for details.")
    
    return all_ok


def main_interactive():
    """Main interactive menu loop."""
    while True:
        choice = main_menu()
        
        if choice == "1":
            all_ok = run_setup_checks()
            if all_ok:
                response = input("\nSetup complete! Run evaluation now? (y/n): ").strip().lower()
                if response == 'y':
                    run_evaluation()
        
        elif choice == "2":
            run_setup_checks()
        
        elif choice == "3":
            show_configuration()
        
        elif choice == "4":
            download_instructions()
        
        elif choice == "5":
            run_evaluation()
        
        elif choice == "6":
            print("\n✓ Thank you for using Speech-to-Text Evaluation System!")
            break
        
        else:
            print("✗ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main_interactive()
    except KeyboardInterrupt:
        print("\n\n✗ Setup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")
        sys.exit(1)
