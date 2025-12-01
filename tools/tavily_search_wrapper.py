import logging
import os
from tavily import TavilyClient # Import the Tavily client
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
load_dotenv()  # Load environment variables from .env file

logger = logging.getLogger(__name__)

class TavilySearchTool:
    """
    A wrapper for the tavily-python library.
    Provides a simple interface for performing AI-focused web searches.
    Requires TAVILY_API_KEY environment variable to be set.
    """
    def __init__(self, max_results: int = 3, search_depth: str = "advanced"):
        """
        Initializes the Tavily search tool.

        Args:
            max_results (int): Maximum number of results to return per search.
            search_depth (str): "basic" or "advanced". Advanced provides more thorough results.
        """
        self.max_results = max_results
        self.search_depth = search_depth
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY environment variable is not set.")
        self.client = TavilyClient(api_key=api_key)

    def search(self, query: str) -> list:
        """
        Performs a web search using Tavily.

        Args:
            query (str): The search query string.

        Returns:
            list: A list of dictionaries containing search results.
                  Each dictionary typically has 'url', 'content', 'title' keys.
                  Returns an empty list on error.
        """
        logger.debug(f"Searching Tavily for: {query}")
        try:
            response = self.client.search(
                query=query,
                max_results=self.max_results,
                search_depth=self.search_depth,
            )
            results = response.get('results', [])
            logger.debug(f"Tavily search returned {len(results)} results.")
            return results
        except Exception as e:
            logger.error(f"Error during Tavily search: {e}")
            return [] # Return empty list on failure

