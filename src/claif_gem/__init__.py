"""CLAIF Gemini wrapper."""

from typing import AsyncIterator, Optional

from ..claif.common import Message, ClaifOptions, get_logger
from .client import query as gemini_query
from .types import GeminiOptions


__version__ = "0.1.0"

logger = get_logger(__name__)


async def query(
    prompt: str,
    options: Optional[ClaifOptions] = None,
) -> AsyncIterator[Message]:
    """Query Gemini using CLAIF interface.
    
    Args:
        prompt: The prompt to send to Gemini
        options: Optional CLAIF options
        
    Yields:
        Messages from Gemini
    """
    if options is None:
        options = ClaifOptions()
    
    # Convert CLAIF options to Gemini options
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


__all__ = ["query", "GeminiOptions"]