"""Dataset loader utilities for meeting summarization.

This module provides helpers to load diarized meeting transcripts and their
reference summaries from a simple file-based dataset.

Dataset layout:
    dataset/
        transcript1.txt
        summary1.txt
        transcript2.txt
        summary2.txt
"""

from __future__ import annotations

import glob
import logging
import os
from typing import List

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


def _sorted_files(dataset_path: str, pattern: str) -> List[str]:
    """Return sorted file paths for a glob pattern."""
    search_path = os.path.join(dataset_path, pattern)
    return sorted(glob.glob(search_path))


def load_transcripts(dataset_path: str) -> List[str]:
    """Load all transcripts from the dataset directory.

    Args:
        dataset_path: Path to the dataset directory containing transcript files.

    Returns:
        A list of transcript strings.
    """
    transcript_files = _sorted_files(dataset_path, "transcript*.txt")
    if not transcript_files:
        raise FileNotFoundError(
            f"No transcript files found in dataset path: {dataset_path}"
        )

    transcripts: List[str] = []
    for path in transcript_files:
        LOGGER.debug("Loading transcript: %s", path)
        with open(path, "r", encoding="utf-8") as f:
            transcripts.append(f.read().strip())
    return transcripts


def load_reference_summaries(dataset_path: str) -> List[str]:
    """Load all reference summaries from the dataset directory.

    Args:
        dataset_path: Path to the dataset directory containing summary files.

    Returns:
        A list of reference summary strings.
    """
    summary_files = _sorted_files(dataset_path, "summary*.txt")
    if not summary_files:
        raise FileNotFoundError(
            f"No summary files found in dataset path: {dataset_path}"
        )

    summaries: List[str] = []
    for path in summary_files:
        LOGGER.debug("Loading reference summary: %s", path)
        with open(path, "r", encoding="utf-8") as f:
            summaries.append(f.read().strip())
    return summaries
