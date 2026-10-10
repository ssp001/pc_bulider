from typing import Any
from types import CoroutineType
from app.service import rune_chatai_servie, rune_search_engnine_service
import logfire
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse

load_dotenv()

logfire.configure()

app = FastAPI()


@app.post("/ai_respones")
async def agent_run(input: str):
    """
    This endpoint receives a user query and runs the AI agent to generate a response.
    The response is streamed back to the client as it is generated.
    """
    try:
        async def stream_response():
            async for chunk in rune_chatai_servie(input=input):
                messsage = chunk["model"]["messages"][-1].content
                yield messsage

        return StreamingResponse(stream_response(), media_type="text/plain")
    except Exception as error:
        logfire.error(f"Error occurred while running the agent: {str(error)}")
        return {"error": "An error occurred while processing your request."}


@app.post("/ai_agent_respones")
async def agent_run(user_input: str):
    """
    This endpoint receives a user query and runs the AI agent to generate a response.
    The response is streamed back to the client as it is generated.
    """
    try:
        respones = await rune_search_engnine_service(input=user_input)
        if isinstance(respones, dict) and "model" in respones:
            messsage = respones["model"]["messages"][-1].content
            return messsage
        else:
            return {
                "error": "chunk is not a dict type varriable",
                "statusCode": 413
            }
    except Exception as error:
        logfire.error(f"Error occurred while running the agent: {str(error)}")
        return {"error": "An error occurred while processing your request."}
