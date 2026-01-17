#!/usr/bin/env python3
"""
Config Manager - Main Module
============================

This module provides the main entry point for configuration management.
It imports and exposes all configuration classes from their individual modules.
"""

from .config_manager_main import ConfigManager
from .service_definition import ServiceDefinition
from .service_repository import ServiceRepository

__all__ = [
    'ConfigManager',
    'ServiceDefinition',
    'ServiceRepository'
]

# Maintain backward compatibility by exposing classes directly
ConfigManager = ConfigManager
ServiceDefinition = ServiceDefinition
ServiceRepository = ServiceRepository
