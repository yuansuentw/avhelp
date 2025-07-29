# from ..utils.config_loader import load_yaml
from functools import partial
from pathlib import Path
from typing import Any, Dict

import yaml


def load_yaml(file_path: str) -> Dict[str, Any]:
    """Load YAML configuration file and return as dictionary.

    Args:
        file_path: Path to the YAML file

    Returns:
        Dictionary containing the YAML content

    Raises:
        FileNotFoundError: If the file doesn't exist
        yaml.YAMLError: If the file is not valid YAML
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")

    with open(path, 'r', encoding='utf-8') as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML file {file_path}: {e}")
# Default configuration file path
DEFAULT_CONFIG_PATH = Path(__file__).parent / "series_resolve_rules.yaml"

# Partial function with predefined config path
load_series_config = partial(load_yaml, str(DEFAULT_CONFIG_PATH))