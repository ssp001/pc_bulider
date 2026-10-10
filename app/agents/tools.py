from tavily import TavilyClient
from app.config import setting

tavily_client = TavilyClient(api_key=setting.TRAVILY_API)

"""
def internet_search(
    query: str,
    max_results: int = 5,
    include_raw_content: bool = False,
):
Run a web search
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
    )


subagent_for_image = {
    "name": "image-search-agent",
    "description": "Used to search images of pc parts",
    "system_prompt": "You are a image finder agent",
    "tools": [internet_search],
    # Optional override, defaults to main agent model
    "model": "groq:openai/gpt-oss-20b",
}

subagent_for_shopin_link_and_price = {
    "name": "shoping-link-search-agent",
    "description": "Used to search trusted shoping links for pc parts like amezone and pc-parts price ",
    "system_prompt": "You are a online shoping link and pc parts price finder agent for pc parts ",
    "tools": [internet_search],
    # Optional override, defaults to main agent model
    "model": "groq:openai/gpt-oss-20b",
}

subagent_for_description = {
    "name": "description-search-agent",
    "description": "Used to find relaible and right knowladge and cost in rupees about the pc parts",
    "system_prompts": "You are a description and cost finder finder agent",
    "tools": [internet_search],
    # Optional override, defaults to main agent model
    "model": "groq:openai/gpt-oss-20b",
}

"""


def subagent_for_image(
    query: str,
    max_results: int = 5,
    include_raw_content: bool = False,
):
    """Run a image search"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
    )


def subagent_for_shopin_link_and_price(
    query: str,
    max_results: int = 5,
    include_raw_content: bool = False,
):
    """
    Run a shoping link and price search
    """
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
    )


def subagent_for_description(
    query: str,
    max_results: int = 5,
    include_raw_content: bool = False,
):
    """
    Run a description search
    """
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
    )
