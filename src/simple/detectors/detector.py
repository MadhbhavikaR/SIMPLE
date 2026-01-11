
import os
from pathlib import Path
from typing import Dict, List, Optional
from abc import ABC, abstractmethod

from simple.config.config_reader import ConfigReader
from simple.config.models import PrereqConfig

class Detector:
    """Base detection class."""
    
    def __init__(self, config_reader: ConfigReader):
        self.config_reader = config_reader
    
    def _find_paths(self, paths: List[str], is_binary: bool = False) -> Optional[str]:
        """Find first existing path."""
        validator = lambda p: p.exists() and (not is_binary or os.access(p, os.X_OK))
        for path in paths:
            if validator(Path(path)):
                return str(path)
        return None

    @abstractmethod
    def detect(self) -> Dict[str, PrereqConfig]:
        pass

    @abstractmethod
    def print_summary(self) -> bool:
        pass