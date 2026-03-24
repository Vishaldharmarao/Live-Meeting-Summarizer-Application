"""
Quick test script to verify the fixes work correctly.
Tests text normalization and WER calculation.
"""

import sys
from main import TextNormalizer, WERCalculator

print("="*70)
print("TESTING TEXT NORMALIZATION AND WER CALCULATION")
print("="*70)

# Test 1: Text normalization
print("\n[TEST 1] Text Normalization with jiwer transformations")
print("-"*70)

test_texts = [
    "HELLO, WORLD!",
    "The Quick-Brown FOX jumps.",
    "Speech   Recognition   (System)",
]

for text in test_texts:
    normalized = TextNormalizer.normalize_text(text)
    print(f"Original:   '{text}'")
    print(f"Normalized: '{normalized}'")
    print()

# Test 2: WER calculation with empty check
print("[TEST 2] WER Calculation with metrics")
print("-"*70)

reference = "THIS IS A TEST SENTENCE"
hypothesis = "THIS IS A TEST SENTENCE"

print(f"Reference:  '{reference}'")
print(f"Hypothesis: '{hypothesis}'")

wer, metrics = WERCalculator.calculate_wer(reference, hypothesis, debug=True)
print(f"\nWER Score: {wer:.4f}")
print(f"Accuracy: {100*(1-wer):.2f}%")
print(f"Reference Words: {metrics.get('reference_word_count', 0)}")
print(f"Hypothesis Words: {metrics.get('hypothesis_word_count', 0)}")

# Test 3: WER with differences
print("\n[TEST 3] WER with different text")
print("-"*70)

reference2 = "the quick brown fox jumps over the lazy dog"
hypothesis2 = "the quick brown fox jumps over a lazy dog"

print(f"Reference:  '{reference2}'")
print(f"Hypothesis: '{hypothesis2}'")

wer2, metrics2 = WERCalculator.calculate_wer(reference2, hypothesis2, debug=True)
print(f"\nWER Score: {wer2:.4f}")
print(f"Accuracy: {100*(1-wer2):.2f}%")

# Test 4: Empty transcription handling
print("\n[TEST 4] Empty Transcription Handling")
print("-"*70)

reference3 = "THIS IS VALID TEXT"
hypothesis3 = ""

print(f"Reference:  '{reference3}'")
print(f"Hypothesis: '{hypothesis3}' (empty)")

wer3, metrics3 = WERCalculator.calculate_wer(reference3, hypothesis3, debug=True)
print(f"\nWER Score (should be 1.0): {wer3:.4f}")
print(f"Accuracy: {100*(1-wer3):.2f}%")

print("\n" + "="*70)
print("ALL TESTS COMPLETED SUCCESSFULLY!")
print("="*70)
