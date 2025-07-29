"""Series resolver for video ID parsing."""

import re
from typing import Any, Dict

from result import Err, Ok, Result

from .models import VideoIDData


def success_result(series: str, number: str, raw: str, normalized: str, rule_name: str) -> Result[VideoIDData, str]:
    """Create a successful result."""
    data = VideoIDData(
        series=series,
        number=number,
        raw=raw,
        normalized=normalized,
        rule_name=rule_name
    )
    return Ok(data)


class SeriesResolver:
    """Resolver for extracting video ID components based on configured rules."""

    def __init__(self, rule_name: str, rule_config: Dict[str, Any]):
        """Initialize the resolver with a specific rule configuration."""
        self.rule_name = rule_name
        self.priority = rule_config.get('priority', 999)

        # Compile regex patterns
        self.series_pattern = re.compile(rule_config['series']['pattern'])
        self.splitter_pattern = re.compile(rule_config['splitter']['pattern'])
        self.number_pattern = re.compile(rule_config['number']['pattern'])

        # Store post-processing functions
        self.series_post_process = rule_config['series'].get('post_process', 'keep_original')
        self.splitter_post_process = rule_config['splitter'].get('post_process', 'keep_original')
        self.number_post_process = rule_config['number'].get('post_process', 'keep_original')

        # Store post-processing arguments
        self.series_post_process_args = rule_config['series'].get('post_process_args', [])
        self.splitter_post_process_args = rule_config['splitter'].get('post_process_args', [])
        self.number_post_process_args = rule_config['number'].get('post_process_args', [])

    def __call__(self, text: str) -> Result[VideoIDData, str]:
        """Extract video ID components from text."""
        return self.resolve(text)

    def resolve(self, text: str) -> Result[VideoIDData, str]:
        """Resolve video ID components from text with validation."""
        # Create combined pattern to find the complete video ID string first
        series_pattern_str = self.series_pattern.pattern
        splitter_pattern_str = self.splitter_pattern.pattern
        number_pattern_str = self.number_pattern.pattern
        
        # Build combined pattern with capturing groups and word boundaries
        # Ensure the pattern is not preceded or followed by alphanumeric characters
        combined_pattern = rf"(?<![a-zA-Z0-9])({series_pattern_str})({splitter_pattern_str})({number_pattern_str})(?![a-zA-Z0-9])"
        combined_regex = re.compile(combined_pattern, re.IGNORECASE)
        
        # Search for all matches to ensure only one exists
        all_matches = list(combined_regex.finditer(text))
        if not all_matches:
            return Err(f"Complete pattern not matched for rule {self.rule_name}")
        
        # Reject if multiple matches are found
        if len(all_matches) > 1:
            matches_info = [f"'{match.group(0)}' at position {match.start()}" for match in all_matches]
            return Err(f"Multiple matches found for rule {self.rule_name}: {', '.join(matches_info)}")
        
        # Use the single match
        combined_match = all_matches[0]
        
        # Since patterns may have multiple groups, we need to find the actual series, splitter, and number
        # The first group is always the series (may contain sub-groups)
        # The last group is always the number
        # The splitter is the group just before the number
        groups = combined_match.groups()
        raw_series = groups[0]  # First group is the entire series match
        raw_number = groups[-1]  # Last group is the number
        raw_splitter = groups[-2]  # Second to last group is the splitter
        
        # Debug: print groups for troubleshooting
        # print(f"DEBUG {self.rule_name}: groups={groups}, series='{raw_series}', splitter='{raw_splitter}', number='{raw_number}'")
        
        # The complete raw match (for debugging/reference)
        complete_raw_match = combined_match.group(0)

        # Apply post-processing
        processed_series = self._apply_post_process(raw_series, self.series_post_process, self.series_post_process_args, text)
        processed_number = self._apply_post_process(raw_number, self.number_post_process, self.number_post_process_args, text)
        processed_splitter = self._apply_post_process(raw_splitter, self.splitter_post_process, self.splitter_post_process_args, text)

        # Create normalized format
        normalized = f"{processed_series}{processed_splitter}{processed_number}"

        return success_result(
            series=processed_series,
            number=processed_number,
            raw=complete_raw_match,  # Use the complete matched string as raw
            normalized=normalized,
            rule_name=self.rule_name
        )

    def _apply_post_process(self, value: str, process_type: str, process_args: list, context: str) -> str:
        """Apply post-processing to extracted value."""
        if process_type == 'to_uppercase':
            return value.upper()
        elif process_type == 'replace':
            if len(process_args) >= 1:
                # If only one argument, replace the entire value
                return process_args[0]
            elif len(process_args) >= 2:
                # If two arguments, replace first with second
                return value.replace(process_args[0], process_args[1])
            return value
        elif process_type == 'extract_digits_only':
            return ''.join(re.findall(r'\d+', value))
        elif process_type == 'keep_original':
            return value
        else:
            return value