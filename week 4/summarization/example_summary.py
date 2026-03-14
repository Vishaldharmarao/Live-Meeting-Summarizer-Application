"""Example usage of the meeting summarization module."""

from __future__ import annotations

import logging

from summarization.evaluation import evaluate_summary
from summarization.summarizer import MeetingSummarizer

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main() -> None:
    """Demonstrate generating and evaluating a meeting summary."""
    transcript = """[Speaker 1]: Let's discuss next quarter goals.
[Speaker 2]: We should increase sales by 20%.
[Speaker 1]: Marketing campaigns can help.
"""

    # Reference summary for evaluation purposes
    reference_summary = """Meeting Summary

Key Points
- Discussion about increasing sales by 20%
- Marketing campaign suggested

Decisions
- Sales target increased

Action Items
- Marketing Team: Prepare campaign proposal
"""

    summarizer = MeetingSummarizer()
    summary = summarizer.summarize(transcript, meeting_type="general")

    print("Generated Summary:\n")
    print(summary)

    eval_metrics = evaluate_summary(reference_summary=reference_summary, generated_summary=summary)
    print("\nEvaluation Metrics:")
    for name, value in eval_metrics.items():
        print(f"- {name}: {value:.4f}")


if __name__ == "__main__":
    main()


# GitHub Push Instructions:
#   git add .
#   git commit -m "Implemented LLM-based meeting summarization module"
#   git push origin submission-fix
