"""Client implementation for Gemini."""

from typing import AsyncIterator, Optional

from ..claif.common import Message, get_logger
from .types import GeminiOptions, GeminiMessage, ResultMessage
from .transport import GeminiTransport


logger = get_logger(__name__)


class GeminiClient:
    """Client for interacting with Gemini."""
    
    def __init__(self):
        self.transport = GeminiTransport()
    
    async def query(
        self,
        prompt: str,
        options: Optional[GeminiOptions] = None,
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
    options: Optional[GeminiOptions] = None,
) -> AsyncIterator[Message]:
    """Query Gemini using the default client."""
    async for message in _client.query(prompt, options):
        yield message