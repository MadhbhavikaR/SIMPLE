from abc import ABC, abstractmethod
from typing import Dict, List, Any
from pathlib import Path

class ServiceStrategy(ABC):
    """All services must implement this contract."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique service identifier."""
        pass
    
    @property
    @abstractmethod
    def category(self) -> str:
        """Service category: core/gateway/database/app."""
        pass
    
    @property
    @abstractmethod
    def networks(self) -> List[str]:
        """Required networks."""
        pass
    
    @abstractmethod
    def get_required_secrets(self) -> List[str]:
        """Secrets this service needs from user."""
        pass
    
    @abstractmethod
    def generate_service_yaml(self, context: Dict[str, Any]) -> str:
        """Generates Docker Compose service YAML."""
        pass
    
    @abstractmethod
    def get_volume_paths(self, context: Dict[str, Any]) -> List[Path]:
        """Returns volume directories to create."""
        pass
