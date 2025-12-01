import logging
import wikipedia # The Wikipedia-API Python library (installed via pip install wikipedia)
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class WikiFetcher:
    """
    A class to fetch summaries from Wikipedia based on class labels or location hints.
    """
    def __init__(self, max_sentences: int = 5):
        """
        Initializes the WikiFetcher.

        Args:
            max_sentences (int): Maximum number of sentences to retrieve from the summary.
        """
        self.max_sentences = max_sentences

    def fetch_summary(self, search_term: str, max_chars: int = 1000) -> Optional[str]:
        """
        Fetches the summary of a Wikipedia page for a given search term.

        Args:
            search_term (str): The term to search for on Wikipedia (e.g., 'Tropical rainforest', 'Andalusia').
            max_chars (int): Maximum number of characters to return from the summary.

        Returns:
            Optional[str]: The summary text, or None if not found or an error occurs.
        """
        if not search_term:
            logger.warning("WikiFetcher: Empty search term provided.")
            return None

        logger.debug(f"WikiFetcher: Searching Wikipedia for '{search_term}'.")

        try:
            page_title = wikipedia.search(search_term, results=1)
            if not page_title:
                logger.info(f"WikiFetcher: No Wikipedia page found for search term '{search_term}'.")
                return None

            page_title = page_title[0] # Get the first result
            logger.debug(f"WikiFetcher: Found Wikipedia page: '{page_title}' for term '{search_term}'.")

            summary = wikipedia.summary(page_title, sentences=self.max_sentences, auto_suggest=True, redirect=True)
            logger.info(f"WikiFetcher: Retrieved summary for '{page_title}' (first {len(summary)} chars).")

            if len(summary) > max_chars:
                summary = summary[:max_chars] + "... [Truncated]"

            return summary

        except wikipedia.exceptions.DisambiguationError as e:
            logger.warning(f"Wikipedia disambiguation error for '{search_term}': {e.options[:5]}...") # Log first 5 options
            try:
                first_option = e.options[0]
                logger.info(f"WikiFetcher: Taking first disambiguation option: '{first_option}' for '{search_term}'.")
                summary = wikipedia.summary(first_option, sentences=self.max_sentences, auto_suggest=True, redirect=True)
                if len(summary) > max_chars:
                    summary = summary[:max_chars] + "... [Truncated]"
                return summary
            except Exception as inner_e:
                logger.error(f"WikiFetcher: Error fetching disambiguation option '{first_option}': {inner_e}")
                return None

        except wikipedia.exceptions.PageError:
            logger.info(f"WikiFetcher: Wikipedia page does not exist for '{search_term}'.")
            return None
        except Exception as e:
            logger.error(f"WikiFetcher: Error fetching Wikipedia summary for '{search_term}': {e}")
            return None

