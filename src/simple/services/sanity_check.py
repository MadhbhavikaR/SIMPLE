#!/usr/bin/env python3
"""
Service Sanity Check Base Class
===============================

This module contains the base SanityCheck class that all sanity checks inherit from.
"""

from typing import List, Dict, Any, Callable
from pathlib import Path
import yaml
import re

from simple.config.config_reader import ConfigReader

class SanityCheck:
    """
    Base class for all sanity checks.

    Each sanity check should implement the run() method and return
    a tuple of (success: bool, message: str).
    """

    def __init__(self, name: str, description: str):
        """
        Initialize a sanity check.

        Args:
            name: Short name/identifier for the check
            description: Human-readable description of what this check validates
        """
        self.name = name
        self.description = description

    def run(self) -> tuple[bool, str]:
        """
        Run the sanity check.

        Returns:
            Tuple of (success, message) where success indicates if check passed
            and message provides details about the result
        """
        raise NotImplementedError("Subclasses must implement run() method")
