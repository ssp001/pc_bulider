from deepagents import create_deep_agent
import os
from langchain_groq.chat_models import ChatGroq
from .subaent import subagents
import abc
import logfire
from app.config import setting
from app.utils import AiErrorHnadeler
from .subaent import (
    subagent_for_shopin_link_and_price,
    subagent_for_description,
    subagent_for_image,
)


class AiAgentClientAbstraion(abc.ABC):
    @abc.abstractmethod
    async def run_agent(self):
        pass


class AiAgentClient(AiAgentClientAbstraion):
    def __init__(self):
        self.agent = create_deep_agent(
            model=ChatGroq(
                model=setting.MODEL_NAME,
                api_key=os.getenv("GROQ_API_KEY"),
                temperature=0.0
            ),
            system_prompt="""
            you are a agent that will find opc parts images description and shoping link with affordable buget and give a strucher respones
            your task is only to find out the realm time price of the pc parts of which you will get as inptu
            and the strict formate is-
            {
            pc-part-name,
            image,
            description,
            price,
            shoping-link,
            total-price-of-the-bulid
            }
            don't burn ant token you are just a tool who will just give the relatime data is the specific formate only.
            more strict insructions-
            don't ask anything give the data what you have at that moment.
            don't act like an ai agent.
            a tool call just give the strict formate in json and done,no more anything.
            show an image it self not an link to see the image in a perticular website 
            """,
            subagents=subagents
        )

    async def run_agent(self, user_input: str):
        """
          This method runs the AI agent with the provided user input and yields the generated tokens as they are produced.
          """
        try:
            logfire.info("agent invoked sucesfully")
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
                if isinstance(chunk, dict) and "model" in chunk:
                    print(repr(chunk))
                    yield chunk
        except Exception as error:
            logfire.error("Agent execution failed: {error}", error=str(error))
            yield AiErrorHnadeler(message="can't run agent client error occured")
