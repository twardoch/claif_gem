# this_file: src/claif_gem/client.py
"""Client implementation for Gemini."""

from collections.abc import AsyncIterator

from loguru import logger

try:
    from claif.common import Message
except ImportError:
    from claif_gem._compat import Message
from claif_gem.transport import GeminiTransport
from claif_gem.types import GeminiMessage, GeminiOptions, ResultMessage


class GeminiClient:
    """Client for interacting with Gemini."""

    def __init__(self):
        self.transport = GeminiTransport()

    async def query(
        self,
        prompt: str,
        options: GeminiOptions | None = None,
    ) -> AsyncIterator[Message]:
        """Query Gemini and yield messages."""
        if options is None:
            options = GeminiOptions()

        logger.debug(f"Querying Gemini with prompt: {prompt[:100]}...")

        try:
            await self.transport.connect()

            async for response in self.transport.send_query(prompt, options):
                if isinstance(response, GeminiMessage):
                    yield response.to_claif_message()
                elif isinstance(response, ResultMessage) and response.error:
                    logger.error(f"Gemini error: {response.message}")
                    raise Exception(response.message)

        finally:
            await self.transport.disconnect()


# Module-level client instance
_client = GeminiClient()


async def query(
    prompt: str,
    options: GeminiOptions | None = None,
) -> AsyncIterator[Message]:
    """Query Gemini using the default client."""
    async for message in _client.query(prompt, options):
        yield message
