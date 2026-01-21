#!/usr/bin/env python3
"""
Optimized Video Processing Pipeline
High-performance video creation with parallel processing, streaming, and resource management
"""

import asyncio
import logging
import tempfile
import time
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass
import subprocess
import json
import ffmpeg
from PIL import Image
import concurrent.futures
from ..config import get_config
from ..utils.resource_manager import managed_operation

logger = logging.getLogger("AutoMagic.VideoProcessor")

@dataclass
class VideoSettings:
    """Video processing settings"""
    width: int = 1280
    height: int = 720
    fps: int = 30
    duration: int = 60
    codec: str = "libx264"
    preset: str = "fast"
    crf: int = 23
    pixel_format: str = "yuv420p"
    
    @classmethod
    def from_config(cls):
        """Create settings from global config"""
        config = get_config()
        width, height = map(int, config.video.resolution.split('x'))
        
        return cls(
            width=width,
            height=height,
            fps=config.video.fps,
            duration=config.video.duration,
            codec=config.video.codec,
            preset=config.video.preset,
            crf=config.video.crf,
            pixel_format=config.video.pixel_format
        )

class OptimizedVideoProcessor:
    """High-performance video processor with streaming and parallel processing"""
    
    def __init__(self, settings: Optional[VideoSettings] = None):
        self.config = get_config()
        self.settings = settings or VideoSettings.from_config()
        self.temp_dir = Path(tempfile.mkdtemp(prefix="automagic_video_"))
        
        # Performance settings
        self.max_workers = min(4, self.config.resources.max_concurrent_operations)
        self.thread_executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
        
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup"""
        await self.cleanup()
    
    async def cleanup(self):
        """Clean up temporary files and resources"""
        try:
            if self.temp_dir.exists():
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                logger.debug(f"Cleaned up temp directory: {self.temp_dir}")
        except Exception as e:
            logger.error(f"Failed to cleanup temp directory: {e}")
        
        # Shutdown thread executor
        self.thread_executor.shutdown(wait=True)
    
    async def create_video_from_assets(self, 
                                     image_paths: List[str], 
                                     audio_path: str,
                                     output_path: Optional[str] = None) -> str:
        """Create video from images and audio with optimized processing"""
        async with managed_operation("video_creation"):
            if not output_path:
                timestamp = int(time.time())
                output_path = str(self.config.paths.final_video_path / f"video_{timestamp}.mp4")
            
            logger.info(f"Creating video with {len(image_paths)} images and audio")
            
            try:
                # Validate and prepare assets
                validated_images = await self._validate_and_prepare_images(image_paths)
                validated_audio = await self._validate_and_prepare_audio(audio_path)
                
                if not validated_images:
                    raise ValueError("No valid images provided for video creation")
                
                # Create video in stages for better memory management
                silent_video_path = await self._create_silent_video(validated_images)
                final_video_path = await self._add_audio_to_video(silent_video_path, validated_audio, output_path)
                
                # Verify output
                if not await self._verify_video(final_video_path):
                    raise RuntimeError("Created video failed verification")
                
                logger.info(f"Video created successfully: {final_video_path}")
                return final_video_path
                
            except Exception as e:
                logger.error(f"Video creation failed: {e}")
                raise
    
    async def _validate_and_prepare_images(self, image_paths: List[str]) -> List[str]:
        """Validate and prepare images for video processing"""
        validated_images = []
        
        # Process images in parallel
        tasks = []
        for i, image_path in enumerate(image_paths):
            task = asyncio.create_task(self._process_image(image_path, i))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, str) and result:
                validated_images.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Image processing failed: {result}")
        
        logger.info(f"Validated {len(validated_images)} images out of {len(image_paths)}")
        return validated_images
    
    async def _process_image(self, image_path: str, index: int) -> str:
        """Process and validate a single image"""
        try:
            path = Path(image_path)
            if not path.exists():
                raise FileNotFoundError(f"Image not found: {image_path}")
            
            # Run image processing in thread to avoid blocking
            loop = asyncio.get_event_loop()
            processed_path = await loop.run_in_executor(
                self.thread_executor,
                self._process_image_sync,
                str(path),
                index
            )
            
            return processed_path
            
        except Exception as e:
            logger.error(f"Failed to process image {image_path}: {e}")
            return ""
    
    def _process_image_sync(self, image_path: str, index: int) -> str:
        """Synchronous image processing"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize to target dimensions
                target_size = (self.settings.width, self.settings.height)
                if img.size != target_size:
                    # Maintain aspect ratio and center crop
                    img_aspect = img.width / img.height
                    target_aspect = self.settings.width / self.settings.height
                    
                    if img_aspect > target_aspect:
                        # Image is wider, crop width
                        new_width = int(img.height * target_aspect)
                        left = (img.width - new_width) // 2
                        img = img.crop((left, 0, left + new_width, img.height))
                    else:
                        # Image is taller, crop height
                        new_height = int(img.width / target_aspect)
                        top = (img.height - new_height) // 2
                        img = img.crop((0, top, img.width, top + new_height))
                    
                    # Resize to exact target
                    img = img.resize(target_size, Image.Resampling.LANCZOS)
                
                # Save processed image
                processed_path = self.temp_dir / f"processed_image_{index:03d}.jpg"
                img.save(processed_path, "JPEG", quality=85, optimize=True)
                
                return str(processed_path)
                
        except Exception as e:
            logger.error(f"Sync image processing failed for {image_path}: {e}")
            return ""
    
    async def _validate_and_prepare_audio(self, audio_path: str) -> str:
        """Validate and prepare audio for video processing"""
        if not audio_path or not Path(audio_path).exists():
            logger.warning("No valid audio provided, creating silent audio")
            return await self._create_silent_audio()
        
        try:
            # Validate audio with ffprobe
            probe_result = await self._probe_media(audio_path)
            
            if not self._has_audio_stream(probe_result):
                logger.warning("Audio file has no valid audio stream, creating silent audio")
                return await self._create_silent_audio()
            
            # Normalize audio if needed
            normalized_path = await self._normalize_audio(audio_path)
            return normalized_path
            
        except Exception as e:
            logger.error(f"Audio validation failed: {e}, creating silent audio")
            return await self._create_silent_audio()
    
    async def _probe_media(self, file_path: str) -> Dict[str, Any]:
        """Probe media file with ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', file_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise RuntimeError(f"ffprobe failed: {stderr.decode()}")
            
            return json.loads(stdout.decode())
            
        except Exception as e:
            logger.error(f"Media probing failed: {e}")
            return {}
    
    def _has_audio_stream(self, probe_result: Dict[str, Any]) -> bool:
        """Check if media has valid audio stream"""
        streams = probe_result.get('streams', [])
        return any(stream.get('codec_type') == 'audio' for stream in streams)
    
    async def _normalize_audio(self, audio_path: str) -> str:
        """Normalize audio for consistent output"""
        normalized_path = self.temp_dir / "normalized_audio.mp3"
        
        try:
            # Use ffmpeg for audio normalization
            cmd = [
                'ffmpeg', '-i', audio_path,
                '-ar', '44100',          # Sample rate
                '-ac', '2',              # Stereo
                '-b:a', '128k',          # Bitrate
                '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',  # Loudness normalization
                '-y',                    # Overwrite output
                str(normalized_path)
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Audio normalization failed: {stderr.decode()}")
                return audio_path  # Return original if normalization fails
            
            logger.debug("Audio normalized successfully")
            return str(normalized_path)
            
        except Exception as e:
            logger.error(f"Audio normalization error: {e}")
            return audio_path
    
    async def _create_silent_audio(self) -> str:
        """Create silent audio track"""
        silent_audio_path = self.temp_dir / "silent_audio.mp3"
        
        try:
            cmd = [
                'ffmpeg', '-f', 'lavfi',
                '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100',
                '-t', str(self.settings.duration),
                '-c:a', 'libmp3lame',
                '-b:a', '128k',
                '-y',
                str(silent_audio_path)
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            if process.returncode == 0:
                logger.debug("Silent audio created successfully")
                return str(silent_audio_path)
            else:
                raise RuntimeError("Failed to create silent audio")
                
        except Exception as e:
            logger.error(f"Silent audio creation failed: {e}")
            raise
    
    async def _create_silent_video(self, image_paths: List[str]) -> str:
        """Create silent video from images using optimized FFmpeg"""
        silent_video_path = self.temp_dir / "silent_video.mp4"
        
        try:
            # Calculate timing
            image_duration = self.settings.duration / len(image_paths)
            
            # Create concat file
            concat_file_path = self.temp_dir / "concat.txt"
            with open(concat_file_path, 'w') as f:
                for image_path in image_paths:
                    f.write(f"file '{image_path}'\n")
                    f.write(f"duration {image_duration}\n")
                # Repeat last image to reach exact duration
                if image_paths:
                    f.write(f"file '{image_paths[-1]}'\n")
            
            # Optimized FFmpeg command for video creation
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(concat_file_path),
                '-vf', f'fps={self.settings.fps},scale={self.settings.width}:{self.settings.height}:force_original_aspect_ratio=decrease,pad={self.settings.width}:{self.settings.height}:(ow-iw)/2:(oh-ih)/2',
                '-c:v', self.settings.codec,
                '-preset', self.settings.preset,
                '-crf', str(self.settings.crf),
                '-pix_fmt', self.settings.pixel_format,
                '-movflags', '+faststart',  # Optimize for streaming
                '-threads', str(self.max_workers),
                '-y',
                str(silent_video_path)
            ]
            
            logger.debug(f"Creating silent video with command: {' '.join(cmd[:5])}...")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise RuntimeError(f"Silent video creation failed: {error_msg}")
            
            if not silent_video_path.exists() or silent_video_path.stat().st_size < 1000:
                raise RuntimeError("Silent video creation produced invalid output")
            
            logger.info("Silent video created successfully")
            return str(silent_video_path)
            
        except Exception as e:
            logger.error(f"Silent video creation failed: {e}")
            raise
    
    async def _add_audio_to_video(self, video_path: str, audio_path: str, output_path: str) -> str:
        """Add audio to video using optimized FFmpeg"""
        try:
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Optimized FFmpeg command for audio mixing
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',          # Copy video stream (no re-encoding)
                '-c:a', 'aac',           # Audio codec
                '-b:a', '128k',          # Audio bitrate
                '-map', '0:v:0',         # Map video from first input
                '-map', '1:a:0',         # Map audio from second input
                '-shortest',             # Stop at shortest stream
                '-movflags', '+faststart',
                '-threads', str(self.max_workers),
                '-y',
                output_path
            ]
            
            logger.debug(f"Adding audio with command: {' '.join(cmd[:5])}...")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise RuntimeError(f"Audio mixing failed: {error_msg}")
            
            if not Path(output_path).exists() or Path(output_path).stat().st_size < 1000:
                raise RuntimeError("Audio mixing produced invalid output")
            
            logger.info("Audio added to video successfully")
            return output_path
            
        except Exception as e:
            logger.error(f"Adding audio to video failed: {e}")
            raise
    
    async def _verify_video(self, video_path: str) -> bool:
        """Verify the created video is valid"""
        try:
            if not Path(video_path).exists():
                return False
            
            # Check file size
            file_size = Path(video_path).stat().st_size
            if file_size < 10000:  # Less than 10KB is likely invalid
                logger.error(f"Video file too small: {file_size} bytes")
                return False
            
            # Probe video with ffprobe
            probe_result = await self._probe_media(video_path)
            
            if not probe_result:
                return False
            
            # Check for video and audio streams
            streams = probe_result.get('streams', [])
            has_video = any(s.get('codec_type') == 'video' for s in streams)
            has_audio = any(s.get('codec_type') == 'audio' for s in streams)
            
            if not has_video:
                logger.error("Video verification failed: no video stream")
                return False
            
            # Audio is optional but warn if missing
            if not has_audio:
                logger.warning("Video has no audio stream")
            
            # Check duration
            format_info = probe_result.get('format', {})
            duration = float(format_info.get('duration', 0))
            
            if duration < 1:
                logger.error(f"Video duration too short: {duration}s")
                return False
            
            logger.info(f"Video verification passed: {duration:.1f}s duration, {file_size:,} bytes")
            return True
            
        except Exception as e:
            logger.error(f"Video verification failed: {e}")
            return False
    
    async def optimize_video_for_platform(self, input_path: str, platform: str) -> str:
        """Optimize video for specific platform (YouTube, TikTok, etc.)"""
        platform_settings = {
            'youtube': {
                'resolution': '1920x1080',
                'fps': 30,
                'bitrate': '8000k',
                'format': 'mp4'
            },
            'tiktok': {
                'resolution': '1080x1920',
                'fps': 30,
                'bitrate': '6000k',
                'format': 'mp4'
            },
            'instagram': {
                'resolution': '1080x1080',
                'fps': 30,
                'bitrate': '5000k',
                'format': 'mp4'
            }
        }
        
        if platform not in platform_settings:
            raise ValueError(f"Unsupported platform: {platform}")
        
        settings = platform_settings[platform]
        output_path = str(Path(input_path).with_suffix(f'_{platform}.mp4'))
        
        try:
            width, height = settings['resolution'].split('x')
            
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2',
                '-r', str(settings['fps']),
                '-b:v', settings['bitrate'],
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-movflags', '+faststart',
                '-y',
                output_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"Video optimized for {platform}: {output_path}")
                return output_path
            else:
                raise RuntimeError(f"Platform optimization failed for {platform}")
                
        except Exception as e:
            logger.error(f"Video optimization for {platform} failed: {e}")
            raise

# Convenience function for video creation
async def create_video_from_assets(image_paths: List[str], 
                                 audio_path: str,
                                 output_path: Optional[str] = None,
                                 settings: Optional[VideoSettings] = None) -> str:
    """Create video from assets using optimized processor"""
    async with OptimizedVideoProcessor(settings) as processor:
        return await processor.create_video_from_assets(image_paths, audio_path, output_path)