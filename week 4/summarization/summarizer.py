"""Meeting summarization module.

This module provides an opinionated wrapper around an LLM to generate structured
meeting summaries while preserving speaker context.

The primary LLM backend is Groq (llama-3.1-8b-instant). If Groq is unavailable,
optional fallbacks include HuggingFace BART and T5 models.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Optional

import requests

from summarization.prompt_templates import MEETING_PROMPT_TEMPLATES

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


@dataclass
class SummarizerConfig:
    groq_api_key: Optional[str]
    groq_model: str = "llama-3.1-8b-instant"
    temperature: float = 0.3
    groq_api_url: str = "https://api.groq.com/v1"  # fallback endpoint if groq library not installed


class MeetingSummarizer:
    """Generate structured meeting summaries with an LLM."""

    def __init__(self, config: Optional[SummarizerConfig] = None):
        """Initialize the summarizer.

        Args:
            config: Optional configuration object. If not provided, it is built from
                environment variables.
        """
        self._config = config or self._load_config_from_env()
        self._groq_client = self._init_groq_client()

    def _load_config_from_env(self) -> SummarizerConfig:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            LOGGER.warning(
                "GROQ_API_KEY is not set. Falling back to HuggingFace models for generation."
            )

        return SummarizerConfig(groq_api_key=api_key)

    def _init_groq_client(self):
        """Attempt to initialize the Groq SDK client.

        Falls back to a minimal requests-based client if the SDK is not installed.
        """
        if not self._config.groq_api_key:
            LOGGER.debug("No GROQ_API_KEY provided; skipping Groq client initialization.")
            return None

        try:
            from groq import Groq  # type: ignore

            LOGGER.debug("Using Groq SDK for LLM requests.")
            return Groq(api_key=self._config.groq_api_key)
        except ImportError:
            LOGGER.warning(
                "groq SDK not installed; falling back to HTTP requests for Groq API."  # noqa: E501
            )
            return None

    def _get_prompt(self, transcript: str, meeting_type: str) -> str:
        """Select and format the prompt template for the given meeting type."""
        key = meeting_type.strip().lower()
        template = MEETING_PROMPT_TEMPLATES.get(key)
        if not template:
            LOGGER.warning(
                "Meeting type '%s' not recognized. Defaulting to 'general'.", meeting_type
            )
            template = MEETING_PROMPT_TEMPLATES["general"]

        return template.format(transcript=transcript.strip())

    def summarize(self, transcript: str, meeting_type: str = "general") -> str:
        """Generate a structured summary for a diarized transcript.

        Args:
            transcript: The diarized transcript input.
            meeting_type: One of 'general', 'standup', or 'planning'.

        Returns:
            A structured summary string.
        """
        prompt = self._get_prompt(transcript=transcript, meeting_type=meeting_type)

        # Primary: Groq API
        try:
            return self._generate_with_groq(prompt)
        except Exception as exc:  # noqa: BLE001
            LOGGER.exception("Groq generation failed, attempting fallbacks: %s", exc)

        # Fallbacks
        for model in ("facebook/bart-large-cnn", "t5-small"):
            try:
                return self._generate_with_hf(prompt, model_name=model)
            except Exception as exc:  # noqa: BLE001
                LOGGER.warning("Fallback model %s failed: %s", model, exc)

        LOGGER.warning(
            "No LLM models were available; using a simple heuristic summary fallback."
        )
        return self._simple_fallback_summary(transcript)

    def _generate_with_groq(self, prompt: str) -> str:
        """Generate text using the Groq API.

        Uses the Groq SDK if installed; otherwise uses a plain HTTP request.
        """
        try:
            if self._groq_client is not None and self._config.groq_api_key:
                # Using Groq SDK (new API syntax)
                response = self._groq_client.chat.completions.create(
                    model=self._config.groq_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self._config.temperature,
                    max_tokens=500,
                )

                # Extract the assistant response text
                return response.choices[0].message.content.strip()

            # If we don't have an API key, raise to trigger fallback.
            if not self._config.groq_api_key:
                raise RuntimeError("GROQ_API_KEY not set; cannot use Groq. Falling back to HuggingFace.")

            # Fallback to raw HTTP (compatible with the current Groq chat endpoint)
            request_url = f"{self._config.groq_api_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self._config.groq_api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self._config.groq_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self._config.temperature,
                "max_tokens": 500,
            }
            resp = requests.post(request_url, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()

            return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        except Exception as e:
            print("ERROR: Groq generation failed:", e)
            raise

    def _generate_with_hf(self, prompt: str, model_name: str) -> str:
        """Generate text using a HuggingFace transformer model.

        This is a fallback path when Groq is unavailable.
        """
        try:
            from transformers import pipeline
        except ImportError as exc:
            raise RuntimeError("transformers is not installed") from exc

        LOGGER.debug("Using HuggingFace model %s for generation", model_name)
        generator = pipeline(
            "text2text-generation",
            model=model_name,
            device=-1,  # CPU by default
        )
        output = generator(prompt, max_length=512, do_sample=False, return_full_text=False)
        if not output:
            raise RuntimeError("HuggingFace generation returned no output.")
        text = output[0].get("generated_text") or output[0].get("text")
        return (text or "").strip()

    def _simple_fallback_summary(self, transcript: str) -> str:
        """Generate a simple heuristic summary when no LLM models are available."""
        lines = [line.strip() for line in transcript.splitlines() if line.strip()]
        bullets = [f"- {line}" for line in lines[:5]]
        return (
            "Meeting Summary\n\n"
            "Key Points:\n" + "\n".join(bullets) + "\n\n"
            "Decisions:\n- (none)\n\n"
            "Action Items:\n- (none)"
        )
