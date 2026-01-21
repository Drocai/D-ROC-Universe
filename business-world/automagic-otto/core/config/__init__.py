"""
Configuration module for AutoMagic
Provides centralized configuration management
"""

from .settings import (
    config,
    get_config,
    validate_config,
    APIConfig,
    PathConfig,
    VideoConfig,
    ResourceConfig,
    ProductionConfig,
    ConfigManager
)

__all__ = [
    "config",
    "get_config", 
    "validate_config",
    "APIConfig",
    "PathConfig", 
    "VideoConfig",
    "ResourceConfig",
    "ProductionConfig",
    "ConfigManager"
]