"""Result utilities for video ID extraction using PyPI result library."""
from dataclasses import dataclass


@dataclass
class VideoIDData:
    """Data structure for successful video ID extraction."""
    series: str
    number: str
    raw: str
    normalized: str
    rule_name: str


