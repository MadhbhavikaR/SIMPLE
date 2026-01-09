# simple/core/os_native_security.py
from typing import Dict, Any

class SecurityEnforcerBase:
    """
    Minimal common base for native security enforcers.

    Concrete enforcers must implement:
      - detect(): check availability of the capability/tooling
      - process(): prepare whatever is needed (returns a payload/plan)
      - apply(payload, dry_run=False): perform the action using the prepared payload

    Keep implementations small and use dependency injection (context or helper objects)
    via the constructor when needed.
    """
    def __init__(self, context: Dict[str, Any]):
        self.context = context

    def detect(self) -> bool:
        """Return True if this enforcer is applicable on this system."""
        raise NotImplementedError

    def process(self) -> object:
        """
        Prepare and return a payload/plan to be applied.
        Examples: list of firewall rules, path to a profile file, etc.
        """
        raise NotImplementedError

    def apply(self, payload: object, dry_run: bool = False) -> bool:
        """
        Apply the previously prepared payload.
        Return True on success, False on error.
        """
        raise NotImplementedError
