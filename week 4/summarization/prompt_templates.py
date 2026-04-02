"""Prompt templates for meeting summarization.

This module provides template strings that are used to prompt an LLM to generate
structured summaries for different meeting types.

Templates are intentionally concise and structured to make parsing easier.
"""

from __future__ import annotations

from typing import Dict


MEETING_PROMPT_TEMPLATES: Dict[str, str] = {
    "general": """You are a helpful assistant that summarizes a meeting transcript.

Input Transcript:
{transcript}

Output Format:
Meeting Summary

Key Points:
- ...

Decisions:
- ...

Action Items:
- Person: Task

Please preserve speaker context when relevant (e.g., \"Speaker 1 suggested...\").
""",

    "standup": """You are a helpful assistant that summarizes a daily standup transcript.

Input Transcript:
{transcript}

Output Format:
Standup Summary

Yesterday Progress:
- ...

Today's Plan:
- ...

Blockers:
- ...

Please preserve speaker context when relevant.
""",

    "planning": """You are a helpful assistant that summarizes a project planning meeting transcript.

Input Transcript:
{transcript}

Output Format:
Planning Summary

Goals:
- ...

Tasks Assigned:
- ...

Deadlines:
- ...

Please preserve speaker context when relevant.
""",
}
