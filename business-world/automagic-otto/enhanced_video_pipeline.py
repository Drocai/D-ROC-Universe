"""
Enhanced video assembly pipeline with improved performance, reliability, and features
"""
import os
import json
import time
import logging
import subprocess
import tempfile
import concurrent.futures
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
import threading
from queue import Queue
import hashlib

# Video processing imports
try:
    from moviepy.editor import (
        VideoFileClip, ImageClip, AudioFileClip, TextClip, 
        CompositeVideoClip, concatenate_videoclips, ColorClip
    )
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    logging.warning("MoviePy not available - using FFmpeg fallback only")

try:
    import ffmpeg
    FFMPEG_PYTHON_AVAILABLE = True
except ImportError:
    FFMPEG_PYTHON_AVAILABLE = False
    logging.warning("ffmpeg-python not available")

logger = logging.getLogger("AutoMagic.Pipeline")

class VideoProcessingError(Exception):
    """Custom exception for video processing errors"""
    pass

class EnhancedVideoAssembler:
    """Enhanced video assembly with multiple methods and optimizations"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="automagic_")
        self.processing_queue = Queue()
        self.cache_dir = os.path.join(self.temp_dir, "cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Configuration
        self.default_fps = 24
        self.default_resolution = (1280, 720)
        self.max_workers = min(4, os.cpu_count() or 1)
        
        logger.info(f"Enhanced Video Assembler initialized with {self.max_workers} workers")
        
    def __del__(self):
        """Cleanup temporary files"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def assemble_video_enhanced(
        self, 
        image_paths: List[str], 
        audio_path: str, 
        output_path: str,
        **kwargs
    ) -> Optional[str]:
        """
        Enhanced video assembly with multiple fallback methods
        
        Args:
            image_paths: List of image file paths
            audio_path: Path to audio file
            output_path: Output video path
            **kwargs: Additional options (fps, resolution, duration_per_image, etc.)
        """
        
        logger.info(f"Starting enhanced video assembly: {len(image_paths)} images + audio")
        
        # Validate inputs
        if not self._validate_inputs(image_paths, audio_path):
            return None
        
        # Extract parameters
        fps = kwargs.get('fps', self.default_fps)
        resolution = kwargs.get('resolution', self.default_resolution)
        duration_per_image = kwargs.get('duration_per_image', None)
        add_transitions = kwargs.get('add_transitions', True)
        add_effects = kwargs.get('add_effects', True)
        
        # Try different assembly methods in order of preference
        methods = [
            ('moviepy_enhanced', self._assemble_with_moviepy_enhanced),
            ('ffmpeg_python', self._assemble_with_ffmpeg_python),
            ('ffmpeg_direct', self._assemble_with_ffmpeg_direct),
            ('basic_fallback', self._assemble_basic_fallback)
        ]
        
        for method_name, method_func in methods:
            try:
                logger.info(f"Attempting video assembly with {method_name}")
                
                result = method_func(
                    image_paths, audio_path, output_path,
                    fps=fps, resolution=resolution, 
                    duration_per_image=duration_per_image,
                    add_transitions=add_transitions,
                    add_effects=add_effects
                )
                
                if result and self._validate_output(result):
                    logger.info(f"Video assembly successful with {method_name}: {result}")
                    return result
                else:
                    logger.warning(f"Method {method_name} failed or produced invalid output")
                    
            except Exception as e:
                logger.warning(f"Method {method_name} failed: {e}")
                continue
        
        logger.error("All video assembly methods failed")
        return None
    
    def _validate_inputs(self, image_paths: List[str], audio_path: str) -> bool:
        """Validate input files"""
        # Check images
        if not image_paths:
            logger.error("No image paths provided")
            return False
        
        valid_images = 0
        for img_path in image_paths:
            if os.path.exists(img_path) and self._is_valid_image(img_path):
                valid_images += 1
            else:
                logger.warning(f"Invalid or missing image: {img_path}")
        
        if valid_images == 0:
            logger.error("No valid images found")
            return False
        
        # Check audio
        if not os.path.exists(audio_path) or not self._is_valid_audio(audio_path):
            logger.error(f"Invalid or missing audio file: {audio_path}")
            return False
        
        logger.info(f"Input validation passed: {valid_images}/{len(image_paths)} images, 1 audio file")
        return True
    
    def _assemble_with_moviepy_enhanced(
        self, 
        image_paths: List[str], 
        audio_path: str, 
        output_path: str,
        **kwargs
    ) -> Optional[str]:
        """Enhanced MoviePy assembly with effects and optimizations"""
        
        if not MOVIEPY_AVAILABLE:
            raise VideoProcessingError("MoviePy not available")
        
        try:
            # Load audio to get duration
            audio_clip = AudioFileClip(audio_path)
            total_duration = audio_clip.duration
            
            # Calculate timing
            duration_per_image = kwargs.get('duration_per_image') or (total_duration / len(image_paths))
            fps = kwargs.get('fps', self.default_fps)
            resolution = kwargs.get('resolution', self.default_resolution)
            
            # Process images in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_path = {
                    executor.submit(self._process_image_for_video, img_path, duration_per_image, resolution): img_path 
                    for img_path in image_paths if os.path.exists(img_path)
                }
                
                video_clips = []
                for future in concurrent.futures.as_completed(future_to_path):
                    img_path = future_to_path[future]
                    try:
                        clip = future.result()
                        if clip:
                            video_clips.append(clip)
                    except Exception as e:
                        logger.warning(f"Failed to process image {img_path}: {e}")
            
            if not video_clips:
                raise VideoProcessingError("No video clips generated from images")
            
            # Sort clips by original order
            video_clips.sort(key=lambda x: x.start if hasattr(x, 'start') else 0)
            
            # Add transitions if requested
            if kwargs.get('add_transitions', False):
                video_clips = self._add_transitions(video_clips)
            
            # Concatenate clips
            final_video = concatenate_videoclips(video_clips, method="compose")
            
            # Adjust duration to match audio
            if final_video.duration > total_duration:
                final_video = final_video.subclip(0, total_duration)
            elif final_video.duration < total_duration:
                # Loop video to match audio duration
                loops_needed = int(total_duration / final_video.duration) + 1
                looped_clips = [final_video] * loops_needed
                final_video = concatenate_videoclips(looped_clips).subclip(0, total_duration)
            
            # Set audio
            final_video = final_video.set_audio(audio_clip)
            
            # Add effects if requested
            if kwargs.get('add_effects', False):
                final_video = self._add_video_effects(final_video)
            
            # Write video with optimized settings
            final_video.write_videofile(
                output_path,
                fps=fps,
                codec='libx264',
                audio_codec='aac',
                preset='medium',
                ffmpeg_params=['-crf', '23'],  # Good quality/size balance
                logger=None,
                temp_audiofile=os.path.join(self.temp_dir, 'temp_audio.mp3')
            )
            
            # Cleanup
            audio_clip.close()
            final_video.close()
            for clip in video_clips:
                if hasattr(clip, 'close'):
                    clip.close()
            
            return output_path
            
        except Exception as e:
            logger.error(f"MoviePy enhanced assembly failed: {e}")
            raise VideoProcessingError(f"MoviePy assembly failed: {e}")
    
    def _process_image_for_video(self, image_path: str, duration: float, resolution: Tuple[int, int]) -> Optional[ImageClip]:
        """Process individual image for video with caching"""
        try:
            # Check cache first
            cache_key = self._get_cache_key(image_path, duration, resolution)
            cached_path = os.path.join(self.cache_dir, f"{cache_key}.mp4")
            
            if os.path.exists(cached_path):
                return VideoFileClip(cached_path)
            
            # Create image clip
            clip = ImageClip(image_path, duration=duration)
            
            # Resize to target resolution maintaining aspect ratio
            clip = clip.resize(height=resolution[1])
            if clip.w > resolution[0]:
                clip = clip.resize(width=resolution[0])
            
            # Center the clip if needed
            if clip.size != resolution:
                clip = clip.on_color(
                    size=resolution, 
                    color=(0, 0, 0), 
                    pos='center'
                )
            
            return clip
            
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            return None
    
    def _add_transitions(self, clips: List) -> List:
        """Add smooth transitions between video clips"""
        if len(clips) <= 1:
            return clips
        
        try:
            from moviepy.video.fx.all import crossfadein, crossfadeout
            
            transition_duration = 0.5  # 0.5 second transitions
            result_clips = []
            
            for i, clip in enumerate(clips):
                if i == 0:
                    # First clip: only fade in
                    clip = clip.fx(crossfadein, transition_duration)
                elif i == len(clips) - 1:
                    # Last clip: only fade out
                    clip = clip.fx(crossfadeout, transition_duration)
                else:
                    # Middle clips: fade in and out
                    clip = clip.fx(crossfadein, transition_duration).fx(crossfadeout, transition_duration)
                
                result_clips.append(clip)
            
            return result_clips
            
        except Exception as e:
            logger.warning(f"Failed to add transitions: {e}")
            return clips
    
    def _add_video_effects(self, video_clip):
        """Add subtle visual effects to enhance the video"""
        try:
            # Add a subtle zoom effect
            def zoom_effect(get_frame, t):
                frame = get_frame(t)
                zoom_factor = 1 + (t / video_clip.duration) * 0.05  # 5% zoom over duration
                
                import cv2
                h, w = frame.shape[:2]
                
                # Calculate crop dimensions
                crop_h = int(h / zoom_factor)
                crop_w = int(w / zoom_factor)
                
                # Center crop
                start_y = max(0, (h - crop_h) // 2)
                start_x = max(0, (w - crop_w) // 2)
                
                cropped = frame[start_y:start_y+crop_h, start_x:start_x+crop_w]
                
                # Resize back
                resized = cv2.resize(cropped, (w, h))
                return resized
            
            return video_clip.fl(zoom_effect, apply_to=[])
            
        except Exception as e:
            logger.warning(f"Failed to add effects: {e}")
            return video_clip
    
    def _assemble_with_ffmpeg_python(
        self, 
        image_paths: List[str], 
        audio_path: str, 
        output_path: str,
        **kwargs
    ) -> Optional[str]:
        """Assemble video using ffmpeg-python library"""
        
        if not FFMPEG_PYTHON_AVAILABLE:
            raise VideoProcessingError("ffmpeg-python not available")
        
        try:
            # Create input file list
            input_file = os.path.join(self.temp_dir, "input_list.txt")
            duration_per_image = kwargs.get('duration_per_image', 3)
            
            with open(input_file, 'w', encoding='utf-8') as f:
                for img_path in image_paths:
                    if os.path.exists(img_path):
                        f.write(f"file '{os.path.abspath(img_path).replace(chr(92), '/')}'\n")
                        f.write(f"duration {duration_per_image}\n")
            
            # Create video from images
            fps = kwargs.get('fps', self.default_fps)
            resolution = kwargs.get('resolution', self.default_resolution)
            
            video_stream = (
                ffmpeg
                .input(input_file, format='concat', safe=0)
                .filter('scale', resolution[0], resolution[1])
            )
            
            audio_stream = ffmpeg.input(audio_path)
            
            # Combine video and audio
            output = ffmpeg.output(
                video_stream, audio_stream, output_path,
                vcodec='libx264',
                acodec='aac',
                pix_fmt='yuv420p',
                r=fps,
                shortest=None
            )
            
            ffmpeg.run(output, overwrite_output=True, capture_stdout=True)
            
            return output_path
            
        except Exception as e:
            logger.error(f"ffmpeg-python assembly failed: {e}")
            raise VideoProcessingError(f"ffmpeg-python assembly failed: {e}")
    
    def _assemble_with_ffmpeg_direct(
        self, 
        image_paths: List[str], 
        audio_path: str, 
        output_path: str,
        **kwargs
    ) -> Optional[str]:
        """Assemble video using direct FFmpeg commands"""
        
        try:
            # Create input file list
            input_file = os.path.join(self.temp_dir, "ffmpeg_input.txt")
            duration_per_image = kwargs.get('duration_per_image', 3)
            
            with open(input_file, 'w', encoding='utf-8') as f:
                for img_path in image_paths:
                    if os.path.exists(img_path):
                        abs_path = os.path.abspath(img_path).replace('\\', '/')
                        f.write(f"file '{abs_path}'\n")
                        f.write(f"duration {duration_per_image}\n")
            
            # FFmpeg command
            fps = kwargs.get('fps', self.default_fps)
            resolution = kwargs.get('resolution', self.default_resolution)
            
            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', input_file,
                '-i', audio_path,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-pix_fmt', 'yuv420p',
                '-r', str(fps),
                '-vf', f'scale={resolution[0]}:{resolution[1]}',
                '-shortest',
                output_path
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                return output_path
            else:
                raise VideoProcessingError(f"FFmpeg error: {result.stderr}")
                
        except Exception as e:
            logger.error(f"FFmpeg direct assembly failed: {e}")
            raise VideoProcessingError(f"FFmpeg direct assembly failed: {e}")
    
    def _assemble_basic_fallback(
        self, 
        image_paths: List[str], 
        audio_path: str, 
        output_path: str,
        **kwargs
    ) -> Optional[str]:
        """Basic fallback assembly method"""
        
        try:
            # Use the simplest possible method - single image + audio
            if not image_paths:
                return None
            
            # Use first valid image
            first_image = None
            for img_path in image_paths:
                if os.path.exists(img_path) and self._is_valid_image(img_path):
                    first_image = img_path
                    break
            
            if not first_image:
                return None
            
            # Get audio duration
            audio_duration = self._get_audio_duration(audio_path)
            if not audio_duration:
                audio_duration = 30  # Default fallback
            
            # Simple FFmpeg command to create video from single image
            cmd = [
                'ffmpeg', '-y',
                '-loop', '1',
                '-i', first_image,
                '-i', audio_path,
                '-c:v', 'libx264',
                '-c:a', 'copy',
                '-shortest',
                '-pix_fmt', 'yuv420p',
                '-r', '24',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                return output_path
            else:
                raise VideoProcessingError(f"Basic fallback failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Basic fallback assembly failed: {e}")
            return None
    
    def _get_audio_duration(self, audio_path: str) -> Optional[float]:
        """Get audio file duration using FFmpeg"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet',
                '-show_entries', 'format=duration',
                '-of', 'csv=p=0',
                audio_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return float(result.stdout.strip())
            else:
                return None
                
        except Exception as e:
            logger.warning(f"Failed to get audio duration: {e}")
            return None
    
    def _get_cache_key(self, image_path: str, duration: float, resolution: Tuple[int, int]) -> str:
        """Generate cache key for processed content"""
        content = f"{image_path}_{duration}_{resolution[0]}x{resolution[1]}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _is_valid_image(self, image_path: str) -> bool:
        """Validate image file"""
        try:
            from PIL import Image
            with Image.open(image_path) as img:
                img.verify()
            return True
        except Exception:
            return False
    
    def _is_valid_audio(self, audio_path: str) -> bool:
        """Validate audio file"""
        if not os.path.exists(audio_path):
            return False
        if os.path.getsize(audio_path) < 1000:
            return False
        return audio_path.lower().endswith(('.mp3', '.wav', '.aac', '.ogg', '.m4a'))
    
    def _validate_output(self, output_path: str) -> bool:
        """Validate generated video file"""
        if not os.path.exists(output_path):
            return False
        
        if os.path.getsize(output_path) < 10000:  # Less than 10KB is likely invalid
            return False
        
        # Try to get video info with ffprobe
        try:
            cmd = [
                'ffprobe', '-v', 'quiet',
                '-show_entries', 'format=duration',
                '-of', 'csv=p=0',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                duration = float(result.stdout.strip())
                return duration > 0  # Video should have positive duration
            else:
                return False
                
        except Exception as e:
            logger.warning(f"Failed to validate video output: {e}")
            return False


class VideoProcessingManager:
    """Manager for video processing tasks with queue and monitoring"""
    
    def __init__(self, max_concurrent_jobs: int = 2):
        self.assembler = EnhancedVideoAssembler()
        self.max_concurrent_jobs = max_concurrent_jobs
        self.active_jobs = {}
        self.job_queue = Queue()
        self.job_counter = 0
        self._lock = threading.Lock()
        
    def submit_video_job(
        self, 
        image_paths: List[str], 
        audio_path: str, 
        output_path: str,
        priority: int = 5,
        **kwargs
    ) -> str:
        """Submit a video assembly job"""
        
        with self._lock:
            job_id = f"job_{self.job_counter}_{int(time.time())}"
            self.job_counter += 1
        
        job_data = {
            'id': job_id,
            'image_paths': image_paths,
            'audio_path': audio_path,
            'output_path': output_path,
            'priority': priority,
            'status': 'queued',
            'created_at': datetime.now(),
            'kwargs': kwargs
        }
        
        self.job_queue.put((priority, job_data))
        self.active_jobs[job_id] = job_data
        
        logger.info(f"Video job submitted: {job_id}")
        return job_id
    
    def process_video_queue(self):
        """Process video jobs from queue"""
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrent_jobs) as executor:
            while not self.job_queue.empty():
                try:
                    priority, job_data = self.job_queue.get(timeout=1)
                    
                    # Update job status
                    job_data['status'] = 'processing'
                    job_data['started_at'] = datetime.now()
                    
                    # Submit job to executor
                    future = executor.submit(self._process_single_job, job_data)
                    
                    # Monitor completion
                    try:
                        result = future.result(timeout=600)  # 10 minute timeout
                        job_data['status'] = 'completed' if result else 'failed'
                        job_data['result'] = result
                        job_data['completed_at'] = datetime.now()
                        
                    except concurrent.futures.TimeoutError:
                        job_data['status'] = 'timeout'
                        logger.error(f"Job {job_data['id']} timed out")
                    
                except Exception as e:
                    logger.error(f"Error processing job queue: {e}")
    
    def _process_single_job(self, job_data: Dict[str, Any]) -> Optional[str]:
        """Process a single video job"""
        try:
            logger.info(f"Processing job {job_data['id']}")
            
            result = self.assembler.assemble_video_enhanced(
                job_data['image_paths'],
                job_data['audio_path'],
                job_data['output_path'],
                **job_data['kwargs']
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Job {job_data['id']} failed: {e}")
            return None
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific job"""
        return self.active_jobs.get(job_id)
    
    def get_all_jobs_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all jobs"""
        return self.active_jobs.copy()


# Global instances
video_assembler = EnhancedVideoAssembler()
video_manager = VideoProcessingManager()

# Convenience functions
def assemble_video(
    image_paths: List[str], 
    audio_path: str, 
    output_path: str,
    **kwargs
) -> Optional[str]:
    """Assemble video using the enhanced pipeline"""
    return video_assembler.assemble_video_enhanced(image_paths, audio_path, output_path, **kwargs)

def submit_video_job(
    image_paths: List[str], 
    audio_path: str, 
    output_path: str,
    **kwargs
) -> str:
    """Submit video assembly job to queue"""
    return video_manager.submit_video_job(image_paths, audio_path, output_path, **kwargs)

def process_video_jobs():
    """Process all queued video jobs"""
    video_manager.process_video_queue()

def get_job_status(job_id: str) -> Optional[Dict[str, Any]]:
    """Get job status"""
    return video_manager.get_job_status(job_id)