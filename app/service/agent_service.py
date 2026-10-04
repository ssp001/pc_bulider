from app.client import AgentResponesOrcaStrator
from app.utils import AiErrorHnadeler
from pyresilience import RetryConfig, TimeoutConfig, resilient
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
async def rune_agent_servie(input: str):
    """
    This function runs the AI agent service with the provided input. It handles exceptions and logs errors if they occur.
    """
    try:
        async for token in AgentResponesOrcaStrator().run_agent(user_query=input):
            yield token
    except AiErrorHnadeler as error:
        logfire.error(str(error))
        raise RuntimeError(
            "agent can't be excuted at the moment please try agqain after some time") from error
