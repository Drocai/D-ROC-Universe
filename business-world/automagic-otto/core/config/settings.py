#!/usr/bin/env python3
"""
Unified Configuration System for AutoMagic
Centralized configuration management with validation and environment-specific settings
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from dotenv import load_dotenv
import psutil

# Load environment variables
load_dotenv()

@dataclass
class APIConfig:
    """API configuration with validation"""
    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"
    dalle_model: str = "dall-e-2"
    dalle_image_size: str = "1024x1024"
    
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = ""
    elevenlabs_model_id: str = "eleven_multilingual_v2"
    
    google_api_key: str = ""
    youtube_client_id: str = ""
    youtube_client_secret: str = ""
    youtube_channel_id: str = ""
    youtube_credentials_file: str = "client_secret.json"
    
    # API performance settings
    max_retries: int = 3
    timeout: int = 30
    rate_limit_rpm: int = 60
    connection_pool_size: int = 10

    def __post_init__(self):
        """Load from environment variables"""
        self.openai_api_key = os.getenv("OPENAI_API_KEY", self.openai_api_key)
        self.openai_model = os.getenv("OPENAI_MODEL", self.openai_model)
        self.dalle_model = os.getenv("DALLE_MODEL", self.dalle_model)
        self.dalle_image_size = os.getenv("DALLE_IMAGE_SIZE", self.dalle_image_size)
        
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY", self.elevenlabs_api_key)
        self.elevenlabs_voice_id = os.getenv("ELEVENLABS_VOICE_ID", self.elevenlabs_voice_id)
        self.elevenlabs_model_id = os.getenv("ELEVENLABS_MODEL_ID", self.elevenlabs_model_id)
        
        self.google_api_key = os.getenv("GOOGLE_API_KEY", self.google_api_key)
        self.youtube_client_id = os.getenv("YOUTUBE_CLIENT_ID", self.youtube_client_id)
        self.youtube_client_secret = os.getenv("YOUTUBE_CLIENT_SECRET", self.youtube_client_secret)
        self.youtube_channel_id = os.getenv("YOUTUBE_CHANNEL_ID", self.youtube_channel_id)
        self.youtube_credentials_file = os.getenv("GOOGLE_API_CREDENTIALS_FILE", self.youtube_credentials_file)

    def validate(self) -> List[str]:
        """Validate API configuration and return list of issues"""
        issues = []
        
        if not self.openai_api_key or self.openai_api_key.startswith("YOUR_"):
            issues.append("Missing or invalid OpenAI API key")
            
        if not self.elevenlabs_api_key or self.elevenlabs_api_key.startswith("YOUR_"):
            issues.append("Missing or invalid ElevenLabs API key")
            
        if not self.google_api_key or self.google_api_key.startswith("YOUR_"):
            issues.append("Missing or invalid Google API key")
            
        return issues

@dataclass
class PathConfig:
    """Path configuration with automatic directory creation"""
    base_dir: Path = field(default_factory=lambda: Path.cwd())
    
    # Asset directories
    image_save_path: Path = field(default_factory=lambda: Path("generated_images"))
    audio_save_path: Path = field(default_factory=lambda: Path("generated_audio"))
    video_clips_path: Path = field(default_factory=lambda: Path("generated_video_clips"))
    final_video_path: Path = field(default_factory=lambda: Path("final_videos"))
    thumbnails_path: Path = field(default_factory=lambda: Path("generated_thumbnails"))
    
    # System directories
    logs_path: Path = field(default_factory=lambda: Path("logs"))
    cache_path: Path = field(default_factory=lambda: Path(".cache"))
    temp_path: Path = field(default_factory=lambda: Path("temp"))
    
    def __post_init__(self):
        """Load from environment and create directories"""
        self.image_save_path = Path(os.getenv("IMAGE_SAVE_PATH", str(self.image_save_path)))
        self.audio_save_path = Path(os.getenv("AUDIO_SAVE_PATH", str(self.audio_save_path)))
        self.video_clips_path = Path(os.getenv("VIDEO_CLIP_SAVE_PATH", str(self.video_clips_path)))
        self.final_video_path = Path(os.getenv("FINAL_VIDEO_SAVE_PATH", str(self.final_video_path)))
        
        # Create all directories
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create all required directories"""
        directories = [
            self.image_save_path, self.audio_save_path, self.video_clips_path,
            self.final_video_path, self.thumbnails_path, self.logs_path,
            self.cache_path, self.temp_path
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

@dataclass
class VideoConfig:
    """Video processing configuration"""
    resolution: str = "1080x1920"
    fps: int = 30
    duration: int = 60
    image_duration: int = 5
    
    # FFmpeg optimization
    codec: str = "libx264"
    preset: str = "fast"  # ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
    crf: int = 23  # Lower = better quality, higher file size
    pixel_format: str = "yuv420p"
    
    def __post_init__(self):
        """Load from environment variables"""
        self.resolution = os.getenv("VIDEO_RESOLUTION", self.resolution)
        self.fps = int(os.getenv("VIDEO_FPS", self.fps))
        self.duration = int(os.getenv("MAX_VIDEO_DURATION", self.duration))

@dataclass
class ResourceConfig:
    """Resource management configuration"""
    max_memory_gb: float = 4.0
    max_disk_usage_gb: float = 10.0
    cleanup_after_days: int = 7
    max_concurrent_operations: int = 3
    
    def __post_init__(self):
        """Auto-detect system resources"""
        # Set memory limit to 50% of available RAM
        available_memory = psutil.virtual_memory().total / (1024**3)  # GB
        self.max_memory_gb = min(self.max_memory_gb, available_memory * 0.5)
        
        # Set CPU limit based on available cores
        cpu_count = psutil.cpu_count()
        self.max_concurrent_operations = min(self.max_concurrent_operations, cpu_count)

@dataclass
class ProductionConfig:
    """Production workflow configuration"""
    season: int = 1
    day_number: int = 1
    daily_run_time: str = "09:00"
    
    # Content generation
    content_themes: List[str] = field(default_factory=lambda: [
        "technology", "AI", "creativity", "innovation", "science"
    ])
    
    def __post_init__(self):
        """Load from environment variables"""
        self.season = int(os.getenv("SEASON", self.season))
        self.day_number = int(os.getenv("DAY_NUMBER", self.day_number))
        self.daily_run_time = os.getenv("DAILY_RUN_TIME", self.daily_run_time)

class ConfigManager:
    """Centralized configuration manager"""
    
    def __init__(self):
        self.api = APIConfig()
        self.paths = PathConfig()
        self.video = VideoConfig()
        self.resources = ResourceConfig()
        self.production = ProductionConfig()
        
        # Setup logging
        self.setup_logging()
        self.logger = logging.getLogger("AutoMagic.Config")
        
        # Validate configuration
        self.validate_all()
    
    def setup_logging(self):
        """Setup centralized logging configuration"""
        log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper())
        log_file = self.paths.logs_path / "automagic.log"
        
        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        
        # Configure root logger
        root_logger = logging.getLogger("AutoMagic")
        root_logger.setLevel(log_level)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
    
    def validate_all(self) -> Dict[str, List[str]]:
        """Validate all configuration sections"""
        validation_results = {
            "api": self.api.validate(),
            "system": self._validate_system(),
            "ffmpeg": self._validate_ffmpeg()
        }
        
        # Log validation results
        logger = logging.getLogger("AutoMagic.Config")
        for section, issues in validation_results.items():
            if issues:
                logger.warning(f"{section.upper()} configuration issues: {', '.join(issues)}")
            else:
                logger.info(f"{section.upper()} configuration validated successfully")
        
        return validation_results
    
    def _validate_system(self) -> List[str]:
        """Validate system resources"""
        issues = []
        
        # Check available disk space
        disk_usage = psutil.disk_usage('.')
        available_gb = disk_usage.free / (1024**3)
        if available_gb < 2.0:
            issues.append(f"Low disk space: {available_gb:.1f}GB available")
        
        # Check available memory
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            issues.append(f"High memory usage: {memory.percent}% used")
        
        return issues
    
    def _validate_ffmpeg(self) -> List[str]:
        """Validate FFmpeg installation"""
        issues = []
        
        try:
            import subprocess
            result = subprocess.run(
                ['ffmpeg', '-version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )
            if result.returncode != 0:
                issues.append("FFmpeg not properly installed")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            issues.append("FFmpeg not found in PATH")
        except Exception as e:
            issues.append(f"FFmpeg validation error: {str(e)}")
        
        return issues
    
    def update_production_day(self, new_day: int):
        """Update production day number in environment"""
        self.production.day_number = new_day
        
        # Update .env file
        env_file = Path(".env")
        if env_file.exists():
            content = env_file.read_text()
            lines = content.split('\n')
            
            updated = False
            for i, line in enumerate(lines):
                if line.startswith('DAY_NUMBER='):
                    lines[i] = f'DAY_NUMBER={new_day}'
                    updated = True
                    break
            
            if not updated:
                lines.append(f'DAY_NUMBER={new_day}')
            
            env_file.write_text('\n'.join(lines))
            self.logger.info(f"Updated DAY_NUMBER to {new_day} in .env")
    
    def get_cache_path(self, cache_type: str) -> Path:
        """Get cache path for specific cache type"""
        cache_dir = self.paths.cache_path / cache_type
        cache_dir.mkdir(exist_ok=True)
        return cache_dir
    
    def cleanup_old_files(self, days_old: int = None):
        """Cleanup old generated files"""
        if days_old is None:
            days_old = self.resources.cleanup_after_days
        
        import time
        cutoff_time = time.time() - (days_old * 24 * 3600)
        
        cleanup_dirs = [
            self.paths.image_save_path,
            self.paths.audio_save_path,
            self.paths.video_clips_path,
            self.paths.temp_path
        ]
        
        cleaned_files = 0
        for directory in cleanup_dirs:
            if not directory.exists():
                continue
                
            for file_path in directory.rglob("*"):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        cleaned_files += 1
                    except OSError:
                        continue
        
        self.logger.info(f"Cleaned up {cleaned_files} old files")
        return cleaned_files

# Global configuration instance
config = ConfigManager()

# Convenience functions
def get_config() -> ConfigManager:
    """Get the global configuration instance"""
    return config

def validate_config() -> bool:
    """Validate configuration and return True if all good"""
    results = config.validate_all()
    return not any(issues for issues in results.values())