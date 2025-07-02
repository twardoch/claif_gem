# this_file: src/claif_gem/__init__.py
"""CLAIF Gemini wrapper."""

from collections.abc import AsyncIterator

from loguru import logger

try:
    from claif.common import ClaifOptions, Message
except ImportError:
    from claif.common import ClaifOptions, Message
from claif_gem.client import query as gemini_query
from claif_gem.types import GeminiOptions

try:
    from claif_gem.__version__ import __version__
except ImportError:
    __version__ = "0.1.0-dev"


async def query(
    prompt: str,
    options: ClaifOptions | None = None,
) -> AsyncIterator[Message]:
    """Query Gemini usingClaif interface.

    Args:
        prompt: The prompt to send to Gemini
        options: OptionalClaif options

    Yields:
        Messages from Gemini
    """
    if options is None:
        options = ClaifOptions()

    # ConvertClaif options to Gemini options
    gemini_options = GeminiOptions(
        model=options.model,
        temperature=options.temperature,
        system_prompt=options.system_prompt,
        timeout=options.timeout,
        verbose=options.verbose,
    )

    logger.debug(f"Querying Gemini with prompt: {prompt[:100]}...")

    # Pass through to Gemini client
    async for message in gemini_query(prompt, gemini_options):
        yield message


__all__ = ["GeminiOptions", "query"]
