import logging
from duckduckgo_search import DDGS # Import the search library


logger = logging.getLogger(__name__)

class DuckDuckGoSearchTool:
    """
    A wrapper for the duckduckgo_search library.
    Provides a simple interface for performing web searches.
    """
    def __init__(self, max_results: int = 3):
        """
        Initializes the search tool.

        Args:
            max_results (int): Maximum number of results to return per search.
        """
        self.max_results = max_results

    def search(self, query: str) -> list:
        """
        Performs a web search using DuckDuckGo.

        Args:
            query (str): The search query string.

        Returns:
            list: A list of dictionaries containing search results.
                  Each dictionary typically has 'title', 'href', 'body' keys.
                  Returns an empty list on error.
        """
        logger.debug(f"Searching DuckDuckGo for: {query}")
        try:
            results = DDGS().text(query, max_results=self.max_results)
            logger.debug(f"DuckDuckGo search returned {len(results)} results.")
            return list(results) # Convert generator to list
        except Exception as e:
            logger.error(f"Error during DuckDuckGo search: {e}")
            return [] # Return empty list on failure

