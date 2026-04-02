"""Summarization package entry point."""

from __future__ import annotations

from .evaluation import evaluate_summary
from .summarizer import MeetingSummarizer

__all__ = ["MeetingSummarizer", "evaluate_summary"]
