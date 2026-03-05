# Security Refactoring Summary: Hugging Face Token Management

## Overview
This document summarizes the security improvements made to remove hardcoded API tokens from the codebase and implement secure environment-based token management.

---

## 🔴 Critical Issue Fixed
**Hardcoded Hugging Face Token Detected and Removed**
- **File**: `week 3/main.py` (line 156)
- **Issue**: The code contained a hardcoded Hugging Face API token directly in the source code
- **Risk**: 
  - Token could be exposed when pushing to GitHub or other version control systems
  - Anyone with access to the repository could use the token to access Hugging Face APIs
  - Token could be indexed by search engines or logged in build systems
  
---

## ✅ Changes Made

### 1. **Refactored Token Loading** (`week 3/main.py`)

#### BEFORE (❌ Insecure):
```python
# Load pyannote diarization model
logger.info(f"Loading diarization model: {Config.DIARIZATION_MODEL}")
hf_token = "<YOUR_HF_TOKEN>"  # ❌ HARDCODED TOKEN!
if not hf_token:
    logger.warning("HF_TOKEN not set. Using anonymous access.")

try:
    diarization_pipeline = DiarizationPipeline.from_pretrained(
        Config.DIARIZATION_MODEL,
        token=hf_token
    )
```

#### AFTER (✅ Secure):
```python
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
        "  export HF_TOKEN='<YOUR_HF_TOKEN>'\n\n"
        "Windows (PowerShell):\n"
        "  $env:HF_TOKEN = '<YOUR_HF_TOKEN>'\n\n"
        "Windows (Command Prompt):\n"
        "  set HF_TOKEN=<YOUR_HF_TOKEN>\n\n"
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
```

**Key Improvements**:
- ✅ Token loaded from `os.getenv("HF_TOKEN")` environment variable
- ✅ Clear, actionable error message if token is missing
- ✅ Instructions for all major platforms (Linux, macOS, Windows)
- ✅ Link to Hugging Face token creation page
- ✅ Comments explaining WHY secrets should never be hardcoded

### 2. **Updated .gitignore**

Added entries to prevent accidental commits of `.env` files containing secrets:
```
# Environment variables - NEVER commit .env files that contain secrets!
.env
.env.local
.env.*.local
```

---

## 📋 Setup Instructions for Users

### Step 1: Create .env File
Copy the `.env.example` file and create `.env`:
```bash
cp week\ 3/.env.example .env
```

### Step 2: Get Your Hugging Face Token
1. Visit: https://huggingface.co/settings/tokens
2. Create a new token with **read** permissions
3. Copy the token (format: `<YOUR_HF_TOKEN>`)

(Use environment variable `HF_TOKEN` rather than hardcoding.)

### Step 3: Set the Token in .env
Open `.env` and replace the placeholder:
```env
HF_TOKEN=<YOUR_HF_TOKEN>
CUDA_VISIBLE_DEVICES=0
```

### Step 4: Load Environment Variables

**Option A: Using .env file (Recommended)**
```python
from dotenv import load_dotenv
load_dotenv()  # Loads variables from .env file
```

**Option B: Manual command-line setup**

Linux/macOS:
```bash
export HF_TOKEN='<YOUR_HF_TOKEN>'
python week\ 3/main.py
```

Windows (PowerShell):
```powershell
$env:HF_TOKEN = '<YOUR_HF_TOKEN>'
python "week 3/main.py"
```

Windows (Command Prompt):
```cmd
set HF_TOKEN=<YOUR_HF_TOKEN>
python "week 3/main.py"
```

---

## 🛡️ Security Best Practices Applied

### 1. **Never Store Secrets in Code**
- ❌ Don't hardcode tokens, passwords, or API keys
- ✅ Always use environment variables or secret management systems

### 2. **Environment Variable Pattern**
```python
import os

# Good: Load from environment
token = os.getenv("HF_TOKEN")

# Bad: Hardcoded
token = "<YOUR_HF_TOKEN>"
```

### 3. **.env Files**
- ✅ Keep `.env` files in `.gitignore`
- ✅ Use `.env.example` as a template showing required variables
- ✅ Never commit actual `.env` files to version control

### 4. **Error Handling**
- ✅ Provide clear, actionable error messages when secrets are missing
- ✅ Guide users to set up the required environment variables
- ✅ Fail fast with `EnvironmentError` instead of silently using wrong values

---

## 📁 Related Files

- **Code Changed**: `week 3/main.py` (lines 154-185)
- **Config Template**: `week 3/.env.example`
- **Git Config**: `.gitignore` (updated to exclude .env files)

---

## ✨ Validation Checklist

- [x] Hardcoded token removed from source code
- [x] Token loaded via `os.getenv("HF_TOKEN")`
- [x] Error handling added with clear user instructions
- [x] Comments added explaining security rationale
- [x] `.env` files excluded in `.gitignore`
- [x] `.env.example` template provided
- [x] Instructions for all platforms (Linux, macOS, Windows)
- [x] Code is now safe to push to GitHub

---

## 🔍 Testing

To verify the refactored code works correctly:

1. **Without token (should show error)**:
   ```bash
   python week\ 3/main.py  # Should fail with helpful error message
   ```

2. **With token set**:
   ```bash
   # Linux/macOS
   export HF_TOKEN='<YOUR_HF_TOKEN>'
   python week\ 3/main.py
   
   # Windows PowerShell
   $env:HF_TOKEN = '<YOUR_HF_TOKEN>'
   python "week 3/main.py"
   ```

---

## 📚 Additional Resources

- Hugging Face Tokens: https://huggingface.co/settings/tokens
- OWASP Secrets Management: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- Python-dotenv: https://github.com/theskumar/python-dotenv

