from app.service import rune_agent_servie
import asyncio
import logfire
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

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
            async for chunk in rune_agent_servie(input=input):
                yield chunk

        return StreamingResponse(stream_response(), media_type="text/plain")
    except Exception as error:
        logfire.error(f"Error occurred while running the agent: {str(error)}")
        return {"error": "An error occurred while processing your request."}
