"""Evaluation utilities for meeting summarization."""

from __future__ import annotations

import logging
from typing import Dict

from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


def evaluate_summary(reference_summary: str, generated_summary: str) -> Dict[str, float]:
    """Evaluate a generated summary against a reference summary.

    Computes ROUGE-1, ROUGE-L, and BLEU scores.

    Args:
        reference_summary: The ground-truth summary text.
        generated_summary: The generated summary text.

    Returns:
        A dict with keys: rouge1, rougeL, bleu.
    """
    reference_sentences = [reference_summary.strip()]
    candidate_sentence = generated_summary.strip()

    scorer = rouge_scorer.RougeScorer(["rouge1", "rougeL"], use_stemmer=True)
    scores = scorer.score(reference_summary, generated_summary)

    smoothing = SmoothingFunction().method2
    try:
        bleu_score = sentence_bleu(
            [reference_summary.split()],
            candidate_sentence.split(),
            smoothing_function=smoothing,
        )
    except Exception as exc:  # noqa: BLE001
        LOGGER.warning("BLEU computation failed: %s", exc)
        bleu_score = 0.0

    return {
        "rouge1": scores["rouge1"].fmeasure,
        "rougeL": scores["rougeL"].fmeasure,
        "bleu": bleu_score,
    }
