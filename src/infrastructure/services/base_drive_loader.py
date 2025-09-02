from abc import ABC, abstractmethod
from typing import Optional
from src.infrastructure.services.drive import Drive

class BaseDriveLoader(ABC):
    """Abstract interface for Drive dependency loader"""
    
    @abstractmethod
    def load_drive(self, folder: Optional[str] = None) -> Drive:
        """
        Loads and returns a Drive instance with proper configuration.
        
        Args:
            folder (str): Optional folder name for the Drive instance
            
        Returns:
            Drive: Configured Drive instance
        """
        pass
    
    @abstractmethod
    def get_drive(self) -> Drive:
        """
        Returns the current Drive instance.
        Creates one if it doesn't exist.
        
        Returns:
            Drive: Current Drive instance
        """
        pass
    
    @abstractmethod
    def reset_drive(self) -> None:
        """
        Resets the Drive instance (useful for testing or reconfiguration)
        """
        pass
