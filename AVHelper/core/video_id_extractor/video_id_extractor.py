"""Video ID extractor using multiple series resolvers."""

from typing import Any, Callable, Dict, List

from result import Err, Ok, Result

from .models import VideoIDData
from .series_resolver import SeriesResolver


class VideoIDExtractor:
    """Extractor that uses multiple SeriesResolver objects to extract video IDs."""

    def __init__(self, config_loader: Callable[[], Dict[str, Any]]):
        """Initialize with a config loader function.

        Args:
            config_loader: Function that returns the configuration dictionary
        """
        self.config_loader = config_loader
        self.resolvers: List[SeriesResolver] = []
        self._load_resolvers()

    def _load_resolvers(self) -> None:
        """Load and initialize resolvers from configuration."""
        try:
            config = self.config_loader()
            resolvers = []

            # Create resolvers for each rule
            for rule_name, rule_config in config.items():
                # Skip non-rule entries (like post_process_functions, full_patterns)
                if isinstance(rule_config, dict) and 'priority' in rule_config:
                    resolver = SeriesResolver(rule_name, rule_config)
                    resolvers.append(resolver)

            # Sort by priority (lower number = higher priority)
            self.resolvers = sorted(resolvers, key=lambda r: r.priority)

        except Exception as e:
            raise RuntimeError(f"Failed to load resolvers: {str(e)}")

    def extract(self, text: str) -> Result[VideoIDData, str]:
        """Extract video ID from text using configured resolvers.

        Args:
            text: Input text to parse

        Returns:
            Result object with extraction results or error
        """
        if not text or not text.strip():
            return Err("Empty input text")

        # Try each resolver in priority order
        for resolver in self.resolvers:
            result = resolver(text)
            if isinstance(result, Ok):
                return result

        # If no resolver succeeded
        return Err(f"No matching pattern found for text: {text}")

    def get_resolver_count(self) -> int:
        """Get the number of loaded resolvers."""
        return len(self.resolvers)

    def get_resolver_names(self) -> List[str]:
        """Get list of resolver names in priority order."""
        return [resolver.rule_name for resolver in self.resolvers]

    def reload_config(self) -> None:
        """Reload configuration and reinitialize resolvers."""
        self._load_resolvers()