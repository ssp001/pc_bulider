
from ddgs import DDGS


def search_images(query: str) -> list[dict]:
    """
    Perform an image search using DuckDuckGo.
    """
    try:
        results = DDGS().images(
            query=query,
            max_results=5
        )

        return [
            {
                "title": result.get("title"),
                "image_url": result.get("image"),
                "thumbnail_url": result.get("thumbnail"),
                "source_url": result.get("url"),
            }
            for result in results
        ]
    except Exception as error:
        return [
            {
                "error": "Image search is temporarily unavailable",
                "details": str(error),
            }
        ]


image_search_tool = search_images
