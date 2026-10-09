from ddgs import DDGS


def duckduckgo_search(query: str) -> list[dict]:
    """
    Perform a web search using DuckDuckGo.
    """
    try:
        return list(
            DDGS().text(
                query,
                max_results=5
            )
        )
    except Exception as error:
        return [{
            "error": "Web search temporarily unavailable",
            "message": str(error)
        }]


search_tool = duckduckgo_search
