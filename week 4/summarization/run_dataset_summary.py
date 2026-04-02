"""Run meeting summarization over a dataset and evaluate results."""

from __future__ import annotations

import logging
import os
import statistics
import sys

# Ensure the repository root is on sys.path so that running this file directly works.
# When executing a script, Python sets sys.path[0] to the script directory (summarization/).
# The package root is one level up, so we add it here.
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from dotenv import load_dotenv

from summarization.dataset_loader import load_reference_summaries, load_transcripts
from summarization.evaluation import evaluate_summary
from summarization.summarizer import MeetingSummarizer

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def main() -> None:
    """Load a dataset, summarize each transcript, and evaluate the results."""
    # Load environment variables (e.g., GROQ_API_KEY)
    load_dotenv()

    dataset_path = os.path.join(os.path.dirname(__file__), "..", "dataset")
    dataset_path = os.path.abspath(dataset_path)

    transcripts = load_transcripts(dataset_path)
    reference_summaries = load_reference_summaries(dataset_path)

    if len(transcripts) != len(reference_summaries):
        raise RuntimeError(
            "Number of transcripts does not match number of reference summaries."
        )

    summarizer = MeetingSummarizer()

    rouge1_scores: list[float] = []
    rougeL_scores: list[float] = []
    bleu_scores: list[float] = []

    for idx, (transcript, reference) in enumerate(
        zip(transcripts, reference_summaries), start=1
    ):
        print(f"\nTranscript {idx} Summary:")
        try:
            generated = summarizer.summarize(transcript, meeting_type="general")
        except Exception as exc:
            LOGGER.exception("Failed to generate summary for transcript %d: %s", idx, exc)
            continue

        print(generated)

        scores = evaluate_summary(reference, generated)
        rouge1_scores.append(scores["rouge1"])
        rougeL_scores.append(scores["rougeL"])
        bleu_scores.append(scores["bleu"])

        print("\nEvaluation:")
        print(f"ROUGE-1: {scores['rouge1']:.2f}")
        print(f"ROUGE-L: {scores['rougeL']:.2f}")
        print(f"BLEU: {scores['bleu']:.2f}")

    if rouge1_scores:
        avg_rouge1 = statistics.mean(rouge1_scores)
        avg_rougeL = statistics.mean(rougeL_scores)
        avg_bleu = statistics.mean(bleu_scores)

        print("\nAverage Evaluation Scores:")
        print(f"ROUGE-1: {avg_rouge1:.2f}")
        print(f"ROUGE-L: {avg_rougeL:.2f}")
        print(f"BLEU: {avg_bleu:.2f}")

        if avg_rouge1 < 0.4:
            LOGGER.warning(
                "Average ROUGE-1 score is below 0.4 (%.2f). Review prompt templates and data."
                % avg_rouge1
            )


if __name__ == "__main__":
    main()
