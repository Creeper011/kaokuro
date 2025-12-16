import pytest
import yaml
import logging
from pathlib import Path
from unittest.mock import mock_open, patch
from src.infrastructure.services.config.loaders.yaml_loader import YamlLoader

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@pytest.fixture
def yaml_loader():
    """Provides a YamlLoader instance for tests."""
    return YamlLoader(logger)

def test_yaml_loader_loads_valid_file(yaml_loader):
    """
    Tests that the YamlLoader correctly loads data from a valid YAML file.
    """
    # Arrange
    mock_yaml_content = """
key1: value1
key2:
  nested_key: nested_value
"""
    expected_data = {
        "key1": "value1",
        "key2": {
            "nested_key": "nested_value"
        }
    }
    mock_config_path = Path("test_config.yml")

    with patch("builtins.open", mock_open(read_data=mock_yaml_content)) as mock_file:
        # Act
        data = yaml_loader.load(mock_config_path)

        # Assert
        mock_file.assert_called_once_with(file=mock_config_path, mode="r", encoding="UTF-8")
        assert data == expected_data

def test_yaml_loader_handles_empty_file(yaml_loader):
    """
    Tests that the YamlLoader returns an empty dictionary for an empty YAML file.
    """
    # Arrange
    mock_yaml_content = ""
    expected_data = {}
    mock_config_path = Path("empty_config.yml")

    with patch("builtins.open", mock_open(read_data=mock_yaml_content)) as mock_file:
        # Act
        data = yaml_loader.load(mock_config_path)

        # Assert
        mock_file.assert_called_once_with(file=mock_config_path, mode="r", encoding="UTF-8")
        assert data == expected_data

def test_yaml_loader_raises_file_not_found_error(yaml_loader):
    """
    Tests that the YamlLoader raises FileNotFoundError when the file does not exist.
    """
    # Arrange
    mock_config_path = Path("non_existent_config.yml")

    with patch("builtins.open", side_effect=FileNotFoundError) as mock_file:
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            yaml_loader.load(mock_config_path)
        mock_file.assert_called_once_with(file=mock_config_path, mode="r", encoding="UTF-8")

def test_yaml_loader_raises_yaml_error_for_invalid_yaml(yaml_loader):
    """
    Tests that the YamlLoader raises yaml.YAMLError for an invalid YAML file.
    """
    # Arrange
    mock_invalid_yaml_content = """
key1: value1
- : invalid_key # This is a syntax error in YAML
"""
    mock_config_path = Path("invalid_config.yml")

    with patch("builtins.open", mock_open(read_data=mock_invalid_yaml_content)) as mock_file:
        # Act & Assert
        with pytest.raises(yaml.YAMLError):
            yaml_loader.load(mock_config_path)
        mock_file.assert_called_once_with(file=mock_config_path, mode="r", encoding="UTF-8")
