import logging
from src.infrastructure.services.config.loaders.env_loader import EnvLoader

logger = logging.getLogger(__name__)

def test_env_loader_loads_variables():
    """
    Tests that the EnvLoader can be instantiated and successfully
    load environment variables into a dictionary.
    """
    # Arrange
    loader = EnvLoader(logger)

    # Act
    env_vars = loader.load()
    print("Env loaded:", env_vars)

    # Assert
    assert env_vars is not None, "Loaded environment variables should not be None"
    assert isinstance(env_vars, dict), "Loaded environment variables should be a dictionary"
