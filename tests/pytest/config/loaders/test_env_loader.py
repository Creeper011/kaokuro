from unittest.mock import MagicMock, mock_open, patch
from pathlib import Path
from src.core.constants import DEFAULT_ENV_CONFIG_PATH
from src.infrastructure.services.config.loaders.env_loader import EnvLoader

def test_env_loader_load_success() -> None:
    mock_env_content = "key1=value1\nkey2=value2"
    logger_mock = MagicMock()
    env_loader = EnvLoader(logger=logger_mock, config_path=DEFAULT_ENV_CONFIG_PATH)

    with patch("builtins.open", mock_open(read_data=mock_env_content)):
        data = env_loader.load()

    assert data == {"key1": "value1", "key2": "value2"}
    logger_mock.debug.assert_called_with(
        f"Loaded {len(data)} variables from {DEFAULT_ENV_CONFIG_PATH.name}"
    )

def test_env_loader_with_invalid_path() -> None:
    """Tests loading env loader with a invalid path"""
    logger_mock = MagicMock()
    invalid_path = Path(DEFAULT_ENV_CONFIG_PATH.parent / "n/o/n/.env")
    env_loader = EnvLoader(logger=logger_mock, config_path=invalid_path)
    
    try:
        env_loader.load()
    except Exception as error:
        assert str(error) == f".env file not found at path: {invalid_path.resolve()}"
        logger_mock.warning.assert_called_with(f".env file not found at path: {invalid_path.resolve()}")

def test_env_loader_with_malformed_yaml() -> None:
    logger_mock = MagicMock()
    malformed_yaml_content = "key1: value1\nkey2 value2"  # Missing colon

    with patch("builtins.open", mock_open(read_data=malformed_yaml_content)):
        try:
            env_loader = EnvLoader(logger=logger_mock, config_path=DEFAULT_ENV_CONFIG_PATH)
            env_loader.load()
        except Exception as error:
            assert str(error).startswith("Error loading .env file: while scanning a simple key")

def test_env_loader_with_empty_yaml() -> None:
    logger_mock = MagicMock()
    empty_yaml_content = ""

    with patch("builtins.open", mock_open(read_data=empty_yaml_content)):
        env_loader = EnvLoader(logger=logger_mock, config_path=DEFAULT_ENV_CONFIG_PATH)
        data = env_loader.load()
    assert data == {}

    
def test_env_loader_logger() -> None:
    logger_mock = MagicMock()
    env_loader = EnvLoader(logger=logger_mock, config_path=DEFAULT_ENV_CONFIG_PATH)

    assert env_loader.logger == logger_mock

def test_env_loader_with_a_non_utf8_file() -> None:
    malformed_yaml_content = b"\x80\x81\x82"  # Invalid UTF-8 bytes
    logger_mock = MagicMock()

    with patch("builtins.open", mock_open(read_data=malformed_yaml_content)):
        try:
            env_loader = EnvLoader(logger=logger_mock, config_path=DEFAULT_ENV_CONFIG_PATH)
            env_loader.load()
        except Exception as error:
            assert str(error).startswith("Error loading .env file: cannot use a string pattern on a bytes-like object")