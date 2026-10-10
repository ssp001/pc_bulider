from app.client import AiChatClient
from app.utils import AiErrorHnadeler
from pyresilience import RetryConfig, TimeoutConfig, resilient
from typing import AsyncGenerator, Any, Dict
import logfire


@resilient(
    timeout=TimeoutConfig(
        seconds=60
    ),

    retry=RetryConfig(
        max_attempts=3,
        backoff_factor=20
    )
)
async def rune_chatai_servie(input: str) -> AsyncGenerator[Dict | AiErrorHnadeler, Any]:
    """
    This function runs the AI agent service with the provided input. It handles exceptions and logs errors if they occur.
    """
    try:
        async for token in AiChatClient().run_chatai(user_input=input):
            yield token
    except AiErrorHnadeler as error:
        logfire.error(str(error))
        raise RuntimeError(
            "agent can't be excuted at the moment please try again after some time") from error
