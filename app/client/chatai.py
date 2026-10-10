from typing import AsyncGenerator, Any
from deepagents import create_deep_agent
from app.utils import AiErrorHnadeler
from langchain_groq.chat_models import ChatGroq
from .chataitools import search_tool
import logfire
from app.config import setting
from langgraph.checkpoint.memory import MemorySaver
import abc


class AiChatAbstraion(abc.ABC):
    @abc.abstractmethod
    async def run_chatai(self):
        pass


class AiChatClient(AiChatAbstraion):
    """
    This class is responsible for orchestrating the AI agent that can search the web and provide information regarding PC parts within an affordable budget.
    """

    def __init__(self):
        self.agent = create_deep_agent(
            model=ChatGroq(
                model=setting.MODEL_NAME,
                api_key=setting.GROQ_API_KEY,
                temperature=0.0,
            ),
            tools=[search_tool],
            system_prompt="""You are a helpful pc bulider assistant just extract user buget and and his pc reqierment description"
            in to this formate{
            "budget_pc_requirement": "user budget and pc_reqierment like what they want to do in it better cpu cooler ram like any other additinal information to finding best pc only for this section for ai etc",
            you as an agent output: your output
            you are just do chat users understand the buget and regarding reqierments pc and
            give it the budget_pc_requirement output and retrut your reposnes to the user as as anagent output.
            give a resonable ansewr to user also .
            }""",
        )

    async def run_chatai(self, user_input: str):
        """
        This method runs the AI agent with the provided user input and yields the generated tokens as they are produced.

        """
       # Run the agent
        try:
            logfire.info("agent invoked sucessfully")
            async for chunk in self.agent.astream(
                input={
                    "messages": [
                    {
                        "role": "user",
                        "content": user_input
                    }
                    ]
                },
            ):
                # Only send model events
                if isinstance(chunk, dict) and "model" in chunk:
                    yield chunk
        except Exception as error:
            logfire.error(
                f"Error occurred while running the agent: {str(error)}")
            yield AiErrorHnadeler(message=error)
