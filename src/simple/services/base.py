from abc import ABC, abstractmethod
from typing import Dict, List, Any
from pathlib import Path
from simple.config.config_reader import ConfigReader

class ServiceStrategy(ABC):
    """All services must implement this contract."""
    
    def __init__(self):
        """Initialize ConfigReader for template loading."""
        self.config_reader = ConfigReader()
    
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
    
    def generate_service_yaml(self, context: Dict[str, Any], dependencies: List[str] = None) -> str:
        """
        Generates Docker Compose service YAML from template.
        
        Override this method if you need custom logic, otherwise
        it will automatically load from templates/services/{name}/{name}.yaml.jinja
        
        Args:
            context: Configuration context
            dependencies: List of dependency service names (will be handled by engine)
        """
        # Convert Path objects to strings for template rendering
        template_context = {}
        for key, value in context.items():
            if isinstance(value, Path):
                template_context[key] = str(value)
            else:
                template_context[key] = value
        
        # Add dependencies to context (templates can use them if needed)
        if dependencies:
            template_context['DEPENDENCIES'] = dependencies
        
        template_path = f"services/{self.name}/{self.name}.yaml"
        result = self.config_reader.read_template(template_path, template_context)
        
        if not result.success:
            raise ValueError(f"Failed to load template for {self.name}: {result.error}")
        
        return result.data
    
    @abstractmethod
    def get_volume_paths(self, context: Dict[str, Any]) -> List[Path]:
        """Returns volume directories to create."""
        pass
