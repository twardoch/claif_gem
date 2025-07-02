# this_file: src/claif_gem/client.py
"""Client implementation for Gemini."""

from collections.abc import AsyncIterator

from loguru import logger

try:
    from claif.common import Message
except ImportError:
    from claif.common import Message
from claif_gem.transport import GeminiTransport
from claif_gem.types import GeminiMessage, GeminiOptions, ResultMessage


def _is_cli_missing_error(error: Exception) -> bool:
    """Check if error indicates missing CLI tool."""
    error_str = str(error).lower()
    error_indicators = [
        "command not found",
        "no such file or directory",
        "is not recognized as an internal or external command",
        "cannot find",
        "not found",
        "executable not found",
        "gemini not found",
        "permission denied",
        "filenotfounderror",
    ]
    return any(indicator in error_str for indicator in error_indicators)


class GeminiClient:
    """Client for interacting with Gemini."""

    def __init__(self):
        self.transport = GeminiTransport()

    async def query(
        self,
        prompt: str,
        options: GeminiOptions | None = None,
    ) -> AsyncIterator[Message]:
        """Query Gemini and yield messages with auto-install on missing tools."""
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

        except Exception as e:
            # Check if this is a missing CLI tool error
            if _is_cli_missing_error(e):
                logger.info("Gemini CLI not found, attempting auto-install...")

                # Import and run install
                from claif_gem.install import install_gemini

                install_result = install_gemini()

                if install_result.get("installed"):
                    logger.info("Gemini CLI installed, retrying query...")

                    # Retry the query with new transport instance
                    retry_transport = GeminiTransport()
                    try:
                        await retry_transport.connect()

                        async for response in retry_transport.send_query(prompt, options):
                            if isinstance(response, GeminiMessage):
                                yield response.to_claif_message()
                            elif isinstance(response, ResultMessage) and response.error:
                                logger.error(f"Gemini error: {response.message}")
                                raise Exception(response.message)

                    finally:
                        await retry_transport.disconnect()

                else:
                    error_msg = install_result.get("message", "Unknown installation error")
                    logger.error(f"Auto-install failed: {error_msg}")
                    msg = f"Gemini CLI not found and auto-install failed: {error_msg}"
                    raise Exception(msg) from e
            else:
                # Re-raise non-CLI-missing errors unchanged
                raise e
        finally:
            await self.transport.disconnect()


# Module-level client instance (lazy-loaded)
_client = None


def _get_client() -> GeminiClient:
    """Get or create the client instance."""
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client


async def query(
    prompt: str,
    options: GeminiOptions | None = None,
) -> AsyncIterator[Message]:
    """Query Gemini using the default client with auto-install support."""
    client = _get_client()
    async for message in client.query(prompt, options):
        yield message
