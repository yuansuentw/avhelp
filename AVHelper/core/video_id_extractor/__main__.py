"""Example usage of the video ID extraction system."""

from result import Err, Ok
from video_id_extractor import VideoIDExtractor

from .config_loading import load_series_config


def main():
    """Example usage of VideoIDExtractor."""

    # Initialize extractor with config loader
    extractor = VideoIDExtractor(load_series_config)

    # Test cases
    test_cases = [
        "SSIS-123",
        "FC2-PPV-1234567",
        "HEYZO-1234",
        "caribbeancom-123456-789",
        "1pondo-123456_789",
        "Tokyo-Hot-318930-313",
        "invalid-text"
    ]

    print(f"Loaded {extractor.get_resolver_count()} resolvers:")
    for name in extractor.get_resolver_names():
        print(f"  - {name}")
    print()

    # Test extraction
    for test_text in test_cases:
        print(f"Testing: '{test_text}'")
        result = extractor.extract(test_text)

        if isinstance(result, Ok):
            data = result.ok_value
            print(f"  ✓ Success: {data.normalized}")
            print(f"    Series: {data.series}")
            print(f"    Number: {data.number}")
            print(f"    Rule: {data.rule_name}")
        elif isinstance(result, Err):
            print(f"  ✗ Failed: {result.err_value}")
        print()


if __name__ == "__main__":
    main()