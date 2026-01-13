from typing import Optional
from dataclasses import dataclass

@dataclass
class ServerDetectionResult:
    """Server detection result structure."""
    keyword: str
    detected_port: Optional[int]
    process_name: Optional[str]
