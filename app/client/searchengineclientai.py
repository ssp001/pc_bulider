from abc import ABC, abstractmethod
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider
from app.utils import AiErrorHnadeler
from typing import AsyncGenerator, Any
from app.config import setting
from .tools import image_search_tool
import logfire


class AiclientToolType(ABC):
    @abstractmethod
    async def run_agent(self, ai_input: str):
        pass


class SearchEningClientAi(AiclientToolType):
    """
    This class is responsible for orchestrating the AI agent that can search the web and provide information regarding PC parts within an affordable budget.
    """

    def __init__(self):
        gmodel = GroqModel(
            model_name=setting.MODEL_NAME,
            provider=GroqProvider(
                api_key=setting.GROQ_API_KEY
            )
        )
        self.agent = Agent(
            model=gmodel,
            tools=[
                image_search_tool
            ],
            instructions=(
                "You are an AI assistant pc-bulider that can search the web and provide information regarding pc parts in there afforadable budget. "
                "You will receive a budget and pc description and you should return an image on that images you choose to show the user , "
                "you have to give a description, and a shopping link related to the query."
            ),
            max_concurrency=10,
        )
        logfire.info("agent incilized sucessfully")

    async def run_agent(self, user_query: str) -> AsyncGenerator[Any, Any]:
        """
        This method runs the AI agent with the provided user query and yields the generated tokens as they are produced.
        """
        try:
            async with self.agent.run_stream(user_prompt=user_query) as respones:
                async for token in respones.stream_text():
                    logfire.info("agent genarated token yield sucessfully")
                    yield token
        except Exception as error:
            logfire.error(f"{str(error)}")
            raise AiErrorHnadeler(
                message="an excetion occured is the high level code in agent at runtime"
            )
