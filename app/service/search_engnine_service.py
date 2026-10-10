from pyresilience import resilient, TimeoutConfig, RetryConfig
from app.agents.agent import AiAgentClient
from app.utils import AiErrorHnadeler
from typing import Any
from types import CoroutineType
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
async def rune_search_engnine_service(input: str) -> CoroutineType[Any, Any, dict[str, Any] | Any]:
    """
    This function runs the AI agent service with the provided input. It handles exceptions and logs errors if they occur.
    """
    try:
        respones = await AiAgentClient().run_agent(user_input=input)
        return respones
    except AiErrorHnadeler as error:
        logfire.error(str(error))
        raise RuntimeError(
            "agent can't be excuted at the moment please try agqain after some time") from error
