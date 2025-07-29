# this_file: claif_gem/src/claif_gem/__init__.py
"""Claif provider for Google Gemini with OpenAI Responses API compatibility."""

from claif_gem.__version__ import __version__
from claif_gem.client import GeminiClient

__all__ = ["GeminiClient", "__version__"]
