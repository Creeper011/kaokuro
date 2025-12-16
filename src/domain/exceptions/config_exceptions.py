
class ConfigError(Exception):
    """Base exception for all config-related errors"""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class YamlFailedLoad(ConfigError):
    """Raised when loading configuration from a YAML file fails."""

class EnvFailedLoad(ConfigError):
    """Raised when loading configuration from environment variables fails."""
    