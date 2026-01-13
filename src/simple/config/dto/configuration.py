from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

ConfigData = Dict[str, Any]

@dataclass
class Configuration:
    """Standardized config load result."""
    success: bool
    data: Optional[ConfigData] = None
    error: Optional[str] = None
    path: Optional[Path] = None