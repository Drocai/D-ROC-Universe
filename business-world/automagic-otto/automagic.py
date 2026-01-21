#!/usr/bin/env python3
# automation_script.py - Main automation script for AutoMagic
import os
import sys
import random
import logging
import requests
import subprocess
import traceback
import json # Added: Missing import
import time # Added: Missing import
import schedule # Added: Missing import
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import ffmpeg  # Added for ffmpeg-python
import tempfile  # Added for temporary files
import openai # Added: Missing import
import elevenlabs  # Using the newer elevenlabs library instead of elevenlabslib

# Imports for YouTube API
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle

# Load environment variables
load_dotenv()

# Add debug mode flag
DEBUG_MODE = False

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configure logging - enhance with debug mode support
log_path = os.getenv("LOG_FILE_PATH", "logs/automagic.log")
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
os.makedirs(os.path.dirname(log_path), exist_ok=True)

logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("AutoMagic")

# Make sure directories exist
for dir_path in [
    os.getenv("IMAGE_SAVE_PATH", "generated_images/"),
    os.getenv("AUDIO_SAVE_PATH", "generated_audio/"),
    os.getenv("FINAL_VIDEO_SAVE_PATH", "final_videos/")
]:
    os.makedirs(dir_path, exist_ok=True)

class VideoProduction:
    def __init__(self, debug_mode=False):
        self.season = int(os.getenv("SEASON", 1))
        self.day_number = int(os.getenv("DAY_NUMBER", 1))
        self.logger = logger
        self.debug_mode = debug_mode
        
        if self.debug_mode:
            self.logger.setLevel(logging.DEBUG)
            self.logger.debug("Running in DEBUG mode - verbose logging enabled")
            
        # Check FFMPEG availability
        self._check_ffmpeg()
        
        # Check if required API keys are present
        self._check_api_keys()

        # Initialize OpenAI client
        try:
            self.openai_client = openai.OpenAI()
            self.logger.info("OpenAI client initialized.")
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI client: {e}. OpenAI-dependent features will not work.")
            self.openai_client = None # Ensure it's None if initialization fails

    def _check_ffmpeg(self):
        """Verify that FFMPEG is available and working"""
        self.logger.debug("Checking FFMPEG availability...")
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                self.logger.info(f"FFMPEG is available: {version}")
            else:
                self.logger.warning(f"FFMPEG may not be properly installed. Error: {result.stderr}")
        except Exception as e:
            self.logger.error(f"Failed to check FFMPEG: {e}")
            self.logger.error("Please ensure FFMPEG is installed and in your PATH")

    def _check_api_keys(self):
        """Verify that required API keys are present"""
        required_keys = [
            ("OPENAI_API_KEY", "OpenAI"),
            ("ELEVENLABS_API_KEY", "ElevenLabs"),
            ("GOOGLE_API_KEY", "Google Cloud")
        ]
        
        missing_keys = []
        for env_var, name in required_keys:
            value = os.getenv(env_var)
            if not value or value.startswith("YOUR_") or value == "":
                missing_keys.append(name)
        
        if missing_keys:
            self.logger.error(f"Missing required API keys: {', '.join(missing_keys)}")
            self.logger.error("Please check API_SETUP_GUIDE.txt for instructions")
            sys.exit(1)
        else:
            self.logger.info("All required API keys are configured")

    def generate_content_idea(self):
        """Generate a new content idea using AI"""
        self.logger.info("Generating content idea...")
        
        # Simulated content idea - would use OpenAI in production
        topics = [
            "The secret to perfect sourdough bread",
            "5 mind-blowing facts about space exploration",
            "How to train your brain to remember anything",
            "The psychology behind procrastination",
            "Unusual morning routines of successful people"
        ]
        
        return random.choice(topics)
    
    def generate_script(self, topic):
        """Generate a video script based on the topic"""
        self.logger.info(f"Generating script for topic: {topic}")
        if not self.openai_client:
            self.logger.error("OpenAI client is not initialized. Cannot generate script.")
            return "Error: Script generation failed due to missing OpenAI client."

        prompt = (
            f"Write a concise, engaging video script for YouTube on the topic '{topic}'. "
            "Include an introduction, three main points, and a conclusion in markdown format."
        )
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            script = response.choices[0].message.content
            self.logger.info("Script generated successfully.")
            return script
        except Exception as e:
            self.logger.error(f"OpenAI script generation failed: {e}")
            if self.debug_mode:
                self.logger.error(traceback.format_exc())
            return f"Error: Script generation failed. Topic: {topic}"

    def generate_images(self, script):
        """Generate images based on the script"""
        self.logger.info("Generating images...")

        if not self.openai_client:
            self.logger.error("OpenAI client is not initialized. Cannot generate images.")
            return []

        # For debugging, use mock images if in debug mode and no OPENAI key
        if self.debug_mode and (not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY").startswith("YOUR_")):
            self.logger.debug("DEBUG MODE: Using placeholder images")
            image_files = []
            # Create a simple test image using PIL
            from PIL import Image, ImageDraw, ImageFont
            
            for idx in range(1, 4):  # Create 3 test images
                img_path = os.path.join(os.getenv("IMAGE_SAVE_PATH", "generated_images/"), f"debug_image_{idx}.png")
                img = Image.new('RGB', (1280, 720), color=(73, 109, 137))
                d = ImageDraw.Draw(img)
                
                # Try to load a font, with fallbacks
                font_path = None
                for font_file in ['arial.ttf', 'DejaVuSans.ttf', 'LiberationSans-Regular.ttf']:
                    if os.name == 'nt':  # Windows
                        potential_path = os.path.join(r'C:\Windows\Fonts', font_file)
                    else:  # Linux/Mac
                        for directory in ['/usr/share/fonts/truetype', '/usr/share/fonts/TTF']:
                            potential_path = os.path.join(directory, font_file)
                            if os.path.exists(potential_path):
                                font_path = potential_path
                                break
                    if os.path.exists(potential_path):
                        font_path = potential_path
                        break
                
                try:
                    font = ImageFont.truetype(font_path, 40) if font_path else ImageFont.load_default()
                except Exception:
                    font = ImageFont.load_default()
                
                d.text((640, 360), f"Debug Test Image {idx}", fill=(255, 255, 255), anchor="mm", font=font)
                img.save(img_path)
                image_files.append(img_path)
                self.logger.debug(f"Created debug image: {img_path}")
            
            return image_files
            
        # Regular implementation for production
        # Extract image prompts from script headings
        image_topics = [f"Illustration for: {topic.strip()}" for topic in script.split('\n') if topic and topic[0].isdigit()]
        if not image_topics:
            self.logger.warning("No clear topics found in script for image generation. Using default topics.")
            image_topics = ["Abstract digital art", "Technology concept art", "Information visualization"]
        
        image_files = []
        for idx, prompt in enumerate(image_topics, start=1):
            self.logger.debug(f"Generating image for prompt: {prompt}")
            try:
                response = self.openai_client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    n=1,
                    size="1024x1024",
                    response_format="url"
                )
                image_url = response.data[0].url
                img_data = requests.get(image_url).content
                img_path = os.path.join(os.getenv("IMAGE_SAVE_PATH", "generated_images/"), f"image_{idx}.png")
                with open(img_path, 'wb') as f:
                    f.write(img_data)
                image_files.append(img_path)
                self.logger.debug(f"Saved generated image: {img_path}")
            except Exception as e:
                self.logger.error(f"Failed to generate image {idx}: {e}")
                if self.debug_mode:
                    self.logger.error(traceback.format_exc())
                
                # In case of failure, create a blank image with error message
                try:
                    from PIL import Image, ImageDraw, ImageFont
                    # Use a different variable name for the error image path
                    error_img_path = os.path.join(os.getenv("IMAGE_SAVE_PATH", "generated_images/"), f"error_image_{idx}.png") 
                    img = Image.new('RGB', (1280, 720), color=(40, 40, 40))
                    d = ImageDraw.Draw(img)
                    # Try to load a font, with fallbacks for error image
                    font_path = None
                    for font_file in ['arial.ttf', 'DejaVuSans.ttf', 'LiberationSans-Regular.ttf']:
                        if os.name == 'nt':  # Windows
                            potential_path = os.path.join(r'C:\\Windows\\Fonts', font_file)
                        else:  # Linux/Mac
                            for directory in ['/usr/share/fonts/truetype', '/usr/share/fonts/TTF']:
                                potential_path = os.path.join(directory, font_file)
                                if os.path.exists(potential_path):
                                    font_path = potential_path
                                    break
                        if font_path and os.path.exists(font_path): # check font_path before os.path.exists
                            break
                    
                    try:
                        font = ImageFont.truetype(font_path, 20) if font_path and os.path.exists(font_path) else ImageFont.load_default()
                    except Exception:
                        font = ImageFont.load_default()

                    d.text((640, 360), f"Image generation failed: {str(e)[:50]}", fill=(255, 0, 0), anchor="mm", font=font)
                    img.save(error_img_path) # Use the new variable name here
                    image_files.append(error_img_path) # and here
                    self.logger.debug(f"Created error placeholder image: {error_img_path}") # and here
                except Exception as e2:
                    self.logger.error(f"Also failed to create error image: {e2}")
        
        self.logger.info(f"Generated {len(image_files)} images")
        return image_files

    def _is_valid_image(self, image_path):
        """Check if the file is a valid image by attempting to open it with PIL"""
        try:
            from PIL import Image
            Image.open(image_path)
            return True
        except Exception as e:
            self.logger.error(f"Image validation error for {image_path}: {str(e)}")
            return False
            
    def _is_valid_audio(self, audio_path):
        """Check if the file is a valid audio file by attempting to analyze it with ffmpeg"""
        if not os.path.exists(audio_path):
            self.logger.error(f"Audio file does not exist: {audio_path}")
            return False
            
        # Basic size check - real audio files should be at least 1KB
        min_size = 1000  # bytes
        if os.path.getsize(audio_path) < min_size:
            self.logger.error(f"Audio file too small ({os.path.getsize(audio_path)} bytes): {audio_path}")
            return False
            
        # Extension check
        if not audio_path.lower().endswith(('.mp3', '.wav', '.aac', '.ogg')):
            self.logger.error(f"Audio file has invalid extension: {audio_path}")
            return False
        
        # Try to probe the file with ffmpeg to verify it's a valid audio file
        try:
            import ffmpeg
            probe = ffmpeg.probe(audio_path, v='error')
            # Check if there's at least one audio stream
            audio_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'audio']
            if not audio_streams:
                self.logger.error(f"No audio streams found in file: {audio_path}")
                return False
                
            self.logger.info(f"Validated audio file: {audio_path} - duration: {probe['format'].get('duration', 'unknown')}s")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate audio file {audio_path}: {str(e)}")
            
            # Try alternative validation with subprocess if ffmpeg.probe fails
            try:
                import subprocess
                result = subprocess.run(
                    ['ffmpeg', '-v', 'error', '-i', audio_path, '-f', 'null', '-'],
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    text=True
                )
                
                # If there's no error output, the file is likely valid
                if result.returncode == 0 and not result.stderr.strip():
                    self.logger.info(f"Audio file validated via subprocess: {audio_path}")
                    return True
                else:
                    self.logger.error(f"Audio validation failed (subprocess): {result.stderr}")
                    return False
                    
            except Exception as e2:
                self.logger.error(f"Failed to validate audio with subprocess: {str(e2)}")
                return False
                
    def generate_voice(self, script):
        """Generate voice narration based on the script"""
        self.logger.info("Generating voice narration via ElevenLabs...")
        
        # Debug mode with mock audio
        if self.debug_mode and (not os.getenv("ELEVENLABS_API_KEY") or os.getenv("ELEVENLABS_API_KEY").startswith("YOUR_")):
            self.logger.debug("DEBUG MODE: Using placeholder audio")
            audio_path = os.path.join(os.getenv("AUDIO_SAVE_PATH", "generated_audio/"), "debug_narration.mp3")
            
            # Create a silent audio file for testing
            try:
                # Create a 10 second silent audio
                silent_audio_cmd = [
                    'ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono', 
                    '-t', '10', '-q:a', '9', '-acodec', 'libmp3lame', audio_path
                ]
                
                subprocess.run(
                    silent_audio_cmd,
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    check=True
                )
                self.logger.debug(f"Created silent debug audio: {audio_path}")
                return audio_path
            except Exception as e:
                self.logger.error(f"Failed to create debug audio: {e}")
                # Try to create a dummy file
                with open(audio_path, 'wb') as f:
                    f.write(b'\x00' * 1024)  # Dummy audio data
            return audio_path
        
        # Regular production implementation
        narration_text = '\n'.join([p for p in script.split('\n') if p and not p.startswith('#')])
        audio_path = os.path.join(os.getenv("AUDIO_SAVE_PATH", "generated_audio/"), "narration.mp3")
        try:
            # The newer ElevenLabs library doesn't use set_api_key()
            # Instead, it uses environment variables or client initialization
            from elevenlabs.client import ElevenLabs
            
            api_key = os.getenv("ELEVENLABS_API_KEY")
            if not api_key:
                raise ValueError("ELEVENLABS_API_KEY environment variable is required")
                
            client = ElevenLabs(api_key=api_key)
            voice_id = os.getenv("ELEVENLABS_VOICE_ID")
            
            if not voice_id:
                # If no specific voice is configured, try to get the first available voice
                voices = client.voices.get_all()
                if voices.voices:
                    voice = voices.voices[0]
                    voice_id = voice.voice_id
                    self.logger.warning(f"No voice ID specified in .env, using first available voice: {voice.name}")
                else:
                    raise ValueError("No voices available on your ElevenLabs account")
            
            audio_data = client.generate(
                text=narration_text,
                voice=voice_id,
                model="eleven_multilingual_v2"
            )
            
            with open(audio_path, 'wb') as f:
                for chunk in audio_data:
                    f.write(chunk)
            self.logger.info(f"Generated voice narration at: {audio_path}")
        except Exception as e:
            self.logger.error(f"ElevenLabs voice generation failed: {e}")
            if self.debug_mode:
                self.logger.error(traceback.format_exc())
                
            # Create a fallback silent audio
            try:
                self.logger.info("Attempting to create fallback silent audio")
                silent_audio_cmd = [
                    'ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono', 
                    '-t', '20', '-q:a', '9', '-acodec', 'libmp3lame', audio_path
                ]
                
                subprocess.run(
                    silent_audio_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True
                )
                self.logger.warning(f"Created fallback silent audio: {audio_path}")
            except Exception as e2:
                self.logger.error(f"Failed to create fallback audio: {e2}")
                # Last resort - create a dummy file
                with open(audio_path, 'wb') as f:
                    f.write(b'\x00' * 1024)  # Dummy audio data
                
        return audio_path
    
    def create_video_from_images_and_audio(self, image_files, audio_file):
        """Create a final video from images and an audio file using ffmpeg."""
        self.logger.info("Creating final video from images and audio using ffmpeg...")
        
        today = datetime.now().strftime("%Y-%m-%d")
        final_video_dir = os.getenv("FINAL_VIDEO_SAVE_PATH", "final_videos/")
        # Directory creation is handled at the script start
        final_video_path = os.path.join(
            final_video_dir,
            f"S{self.season}_D{self.day_number}_{today}.mp4"
        )

        if not image_files:
            self.logger.error("No images provided to create video.")
            # Create a dummy file with error to allow script to proceed for testing other parts if needed
            try:
                with open(final_video_path, 'w') as f: f.write("Error: No images provided for video creation.")
            except Exception as e:
                self.logger.error(f"Failed to write dummy error file: {e}")
            return final_video_path
        
        # Verify that all image files exist and are valid
        valid_image_files = []
        for img_path in image_files:
            if not os.path.exists(img_path):
                self.logger.error(f"Image file not found: {img_path}")
                continue
                
            if not self._is_valid_image(img_path):
                self.logger.error(f"Invalid image file: {img_path}")
                continue
                
            valid_image_files.append(img_path)
            
        if not valid_image_files:
            self.logger.error("No valid image files found.")
            try:
                with open(final_video_path, 'w') as f: f.write("Error: No valid image files found.")
            except Exception as e:
                self.logger.error(f"Failed to write dummy error file: {e}")
            return final_video_path
            
        # Use only valid images
        image_files = valid_image_files
            
        if not os.path.exists(audio_file):
            self.logger.error(f"Audio file not found: {audio_file}")
            try:
                with open(final_video_path, 'w') as f: f.write(f"Error: Audio file {audio_file} not found.")
            except Exception as e:
                self.logger.error(f"Failed to write dummy error file: {e}")
            return final_video_path
            
        # Verify that audio file is valid
        if not self._is_valid_audio(audio_file):
            self.logger.error(f"Invalid audio file: {audio_file}")
            try:
                with open(final_video_path, 'w') as f: f.write(f"Error: Invalid audio file: {audio_file}")
            except Exception as e:
                self.logger.error(f"Failed to write dummy error file: {e}")
            return final_video_path

        image_duration_per_image = 5  # seconds per image
        output_framerate = 25  # fps

        temp_concat_file_path = None
        silent_video_path = None

        try:
            # Create a temporary file list for ffmpeg's concat demuxer
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as tmpf:
                for img_path in image_files:
                    abs_img_path = os.path.abspath(img_path)
                    # FFmpeg on Windows prefers forward slashes or escaped backslashes.
                    # ffmpeg-python might handle this, but being explicit can help.
                    # For concat file, simple forward slashes are usually safer.
                    # However, direct path from abspath should work if ffmpeg-python handles it.
                    # Let's ensure paths are clean for the concat file.
                    # Replacing backslashes with forward slashes for ffmpeg file list.
                    clean_img_path = abs_img_path.replace('\\\\', '/').replace('\\', '/')
                    tmpf.write(f"file '{clean_img_path}'\n")
                    tmpf.write(f"duration {image_duration_per_image}\n")
                temp_concat_file_path = tmpf.name
            
            self.logger.debug(f"Using concat file: {temp_concat_file_path}")

            # Stage 1: Create silent video from images
            # Need a temporary path for the silent video
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_silent_video:
                silent_video_path = tmp_silent_video.name
                self.logger.info(f"Creating silent video at: {silent_video_path}")
            
            # Stage 1: Create silent video from images
            try:
                (
                    ffmpeg
                    .input(temp_concat_file_path, format='concat', safe=0)
                    .output(silent_video_path, vcodec='libx264', pix_fmt='yuv420p', r=str(output_framerate), loglevel="error")
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True)
                )
                self.logger.info(f"Silent video created: {silent_video_path}")
                
                # Verify that silent video was created
                if not os.path.exists(silent_video_path) or os.path.getsize(silent_video_path) < 1000:
                    self.logger.error(f"Silent video was not created properly: {silent_video_path}")
                    raise Exception("Failed to create valid silent video")
                
                # Stage 2: Combine silent video with audio
                self.logger.info(f"Adding audio {audio_file} to {silent_video_path}")
                
                # Create input streams
                video_stream = ffmpeg.input(silent_video_path)
                audio_stream = ffmpeg.input(audio_file)
                
                # First attempt with standard approach
                try:
                    (
                        ffmpeg
                        .output(video_stream, audio_stream, final_video_path, 
                                vcodec='copy', 
                                acodec='aac', 
                                shortest=None, # Ensures audio is not cut short if video is shorter
                                loglevel="error" 
                               )
                        .overwrite_output()
                        .run(capture_stdout=True, capture_stderr=True)
                    )
                except Exception as e:
                    self.logger.warning(f"First attempt at adding audio failed: {str(e)}. Trying alternative FFmpeg approach.")
                    # Fallback to alternative approach if first one fails
                    (
                        ffmpeg.concat(video_stream, audio_stream, v=1, a=1)
                        .output(final_video_path, vcodec='copy', acodec='aac', loglevel="error")
                        .overwrite_output()
                        .run(capture_stdout=True, capture_stderr=True)
                    )
                
                self.logger.info(f"Final video with audio created: {final_video_path}")
                return final_video_path
                
            except Exception as e_inner:
                self.logger.error(f"Error in video processing: {str(e_inner)}")
                raise  # Re-raise for outer exception handler
                
        except ffmpeg.Error as e:
            self.logger.error("ffmpeg error during video creation:")
            # Decode stdout/stderr if they are bytes, handling potential decoding errors
            stdout_msg = e.stdout.decode('utf-8', errors='replace') if e.stdout else "N/A"
            stderr_msg = e.stderr.decode('utf-8', errors='replace') if e.stderr else "N/A"
            self.logger.error(f"FFmpeg command: {' '.join(e.cmd) if hasattr(e, 'cmd') and e.cmd else 'N/A'}")
            self.logger.error(f"FFmpeg stdout: {stdout_msg}")
            self.logger.error(f"FFmpeg stderr: {stderr_msg}")
            if not os.path.exists(final_video_path) or os.path.getsize(final_video_path) == 0:
                try:
                    with open(final_video_path, 'w', encoding='utf-8') as f:
                        f.write(f"Error: ffmpeg failed. Stderr: {stderr_msg[:500]}")
                except Exception as ex_write:
                     self.logger.error(f"Failed to write dummy error file after ffmpeg error: {ex_write}")
            return final_video_path 
        except Exception as e_gen:
            self.logger.error(f"General error in create_video_from_images_and_audio: {str(e_gen)}", exc_info=True)
            if not os.path.exists(final_video_path) or os.path.getsize(final_video_path) == 0:
                try:
                    with open(final_video_path, 'w', encoding='utf-8') as f:
                        f.write(f"Error: General error during video creation. Error: {str(e_gen)[:500]}")
                except Exception as ex_write:
                    self.logger.error(f"Failed to write dummy error file after general error: {ex_write}")
            return final_video_path
        finally:
            if temp_concat_file_path and os.path.exists(temp_concat_file_path):
                try:
                    os.remove(temp_concat_file_path)
                    self.logger.debug(f"Removed temporary concat file: {temp_concat_file_path}")
                except Exception as e_remove:
                    self.logger.warning(f"Could not remove temp concat file {temp_concat_file_path}: {e_remove}")
            if silent_video_path and os.path.exists(silent_video_path):
                try:
                    os.remove(silent_video_path)
                    self.logger.debug(f"Removed temporary silent video: {silent_video_path}")
                except Exception as e_remove:
                    self.logger.warning(f"Could not remove temp silent video {silent_video_path}: {e_remove}")

    def upload_to_youtube(self, video_path, title, description):
        """Upload the video to YouTube"""
        self.logger.info(f"Attempting to upload to YouTube: {title}")
        # Prevent duplicate uploads within the same workspace
        script_dir = os.path.dirname(os.path.abspath(__file__))
        upload_log = os.path.join(script_dir, 'uploaded_videos.log')
        if os.path.exists(upload_log):
            with open(upload_log, 'r') as logf:
                if f"{title}" in logf.read():
                    self.logger.warning(f"Video already uploaded previously, skipping: {title}")
                    return False  # Skip duplicate, treat as no upload

        # Check if required YouTube credentials are present
        client_id = os.getenv("YOUTUBE_CLIENT_ID")
        client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
        channel_id = os.getenv("YOUTUBE_CHANNEL_ID") # Not directly used in upload but good for config check
        
        credentials_file = os.getenv("GOOGLE_API_CREDENTIALS_FILE", "youtube_credentials.json")
        
        # Clean and validate credentials_file
        if isinstance(credentials_file, str):
            # It's a string, good to proceed with further checks.
            # No specific action needed here if it's already a string,
            # as subsequent checks will handle it.
            pass 
        else:
            self.logger.error(f"GOOGLE_API_CREDENTIALS_FILE path is not a string: {credentials_file}. Using default 'youtube_credentials.json'.")
            credentials_file = "youtube_credentials.json" # Fallback to default

        if not credentials_file: # Check if it's an empty string
            self.logger.error("GOOGLE_API_CREDENTIALS_FILE path is empty. Cannot proceed with YouTube upload.")
            # Consider how to handle this: return False, raise error, or skip upload
            return # Or return an indicator of failure like False or None
            
        # Ensure the credentials file name includes the .json extension
        if not credentials_file.lower().endswith('.json'):
            self.logger.warning(f"GOOGLE_API_CREDENTIALS_FILE '{credentials_file}' does not end with .json. Appending .json.")
            credentials_file += ".json"
        
        # script_dir was already defined above, re-using it.
        credentials_path = credentials_file if os.path.isabs(credentials_file) else os.path.join(script_dir, credentials_file)
        
        self.logger.debug(f"Attempting to use YouTube credentials file: '{credentials_file}', resolved to absolute path: '{credentials_path}'")

        # Check for placeholder values in .env for YouTube API keys
        if any(not var or (isinstance(var, str) and var.startswith("YOUR_")) for var in [client_id, client_secret, channel_id]):
            self.logger.warning("YouTube client_id, client_secret, or channel_id not properly configured in .env. Skipping actual upload.")
            self.logger.info(f"SIMULATED UPLOAD: Would upload {video_path} to YouTube with title: {title}")
            return False # Indicate simulated upload or misconfiguration

        # Check that credentials JSON exists
        if not os.path.exists(credentials_path):
            self.logger.error(f"YouTube credentials file ('{credentials_path}') not found. Please ensure it's present and correctly named.")
            self.logger.info(f"SIMULATED UPLOAD: Would upload {video_path} to YouTube with title: {title}")
            return False

        if not os.path.exists(video_path) or os.path.getsize(video_path) == 0:
            self.logger.error(f"Video file for upload not found or is empty: {video_path}")
            return False

        creds = None
        # Store token.pickle in the same directory as credentials for better organization
        token_pickle_path = os.path.join(os.path.dirname(credentials_path), 'token.pickle')

        # Load credentials from token.pickle if it exists
        if os.path.exists(token_pickle_path):
            with open(token_pickle_path, 'rb') as token:
                try:
                    creds = pickle.load(token)
                    self.logger.debug(f"Loaded credentials from {token_pickle_path}")
                except Exception as e:
                    self.logger.error(f"Error loading token.pickle: {e}. Will re-authenticate.")
                    creds = None

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and hasattr(creds, 'expired') and creds.expired and hasattr(creds, 'refresh_token') and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    self.logger.info("YouTube credentials refreshed successfully.")
                except Exception as e:
                    self.logger.error(f"Failed to refresh YouTube credentials: {e}. Re-authentication required.")
                    creds = None  # Force re-authentication

            if not creds:  # creds is None either initially or after a refresh failure
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_path,
                        scopes=['https://www.googleapis.com/auth/youtube.upload']
                    )
                    auth_url, _ = flow.authorization_url(access_type='offline', prompt='consent')
                    self.logger.info("Starting YouTube OAuth flow. If your browser does not open, please visit this URL to authorize:")
                    self.logger.info(auth_url)
                    creds = flow.run_local_server(port=0)
                    self.logger.info("YouTube authentication successful.")
                except Exception as e:
                    self.logger.error(f"Error during YouTube authentication flow: {e}")
                    self.logger.error("Please ensure your youtube_credentials.json is correctly configured and accessible.")
                    self.logger.error("You might need to re-authorize the application by deleting token.pickle and running again.")
                    return False  # Authentication failed

            # Save the credentials for the next run, restrict permissions for security
            try:
                with open(token_pickle_path, 'wb') as token:
                    pickle.dump(creds, token)
                if os.name == 'nt':
                    import ctypes
                    FILE_ATTRIBUTE_HIDDEN = 0x02
                    ctypes.windll.kernel32.SetFileAttributesW(token_pickle_path, FILE_ATTRIBUTE_HIDDEN)
                else:
                    os.chmod(token_pickle_path, 0o600)
                self.logger.info(f"YouTube credentials saved to {token_pickle_path} (permissions restricted)")
            except Exception as e:
                self.logger.warning(f"Could not restrict permissions on {token_pickle_path}: {e}")

        try:
            youtube = build('youtube', 'v3', credentials=creds)
            
            request_body = {
                'snippet': {
                    'categoryId': '22',  # Defaulting to 'People & Blogs'. Change as needed.
                                         # See https://developers.google.com/youtube/v3/docs/videoCategories/list
                    'title': title,
                    'description': description,
                    'tags': ['AutoMagic', 'AutomatedContent', 'Python'] # Example tags
                },
                'status': {
                    'privacyStatus': 'public',  # 'public', 'private', or 'unlisted'
                    'selfDeclaredMadeForKids': False # Adjust if content is made for kids
                }
            }

            self.logger.info(f"Uploading video: {video_path} with title: {title}")
            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
            
            insert_request = youtube.videos().insert(
                part=','.join(request_body.keys()),
                body=request_body,
                media_body=media
            )

            response = None
            retry_count = 0
            max_retries = 3
            while response is None and retry_count < max_retries:
                try:
                    status, response = insert_request.next_chunk()
                    if response is not None:
                        if 'id' in response:
                            self.logger.info(f"Video uploaded successfully! Video ID: {response['id']}")
                            # Log the uploaded title to prevent duplicates
                            with open(upload_log, 'a') as logf:
                                logf.write(f"{title}\n")
                            return True
                        else:
                            self.logger.error(f"Video upload failed. No ID in response: {response}")
                            return False
                except Exception as e:
                    retry_count += 1
                    self.logger.error(f"An error occurred during upload (attempt {retry_count}/{max_retries}): {e}")
                    if retry_count >= max_retries:
                        self.logger.error("Max retries reached. Upload failed.")
                        return False
                    time.sleep(5) # Wait before retrying

            if response is None: # Should be caught by retry logic, but as a safeguard
                 self.logger.error("Upload failed after retries, response is None.")
                 return False

        except Exception as e:
            self.logger.error(f"An error occurred with the YouTube API: {e}", exc_info=True)
            # If there's an auth error, token.pickle might be invalid.
            if "invalid_grant" in str(e).lower() or "token has been expired" in str(e).lower() or "token has been revoked" in str(e).lower():
                self.logger.warning("YouTube token might be invalid. Deleting token.pickle for re-authentication on next run.")
                if os.path.exists(token_pickle_path):
                    try:
                        os.remove(token_pickle_path)
                    except Exception as ex_remove:
                        self.logger.error(f"Failed to remove token.pickle: {ex_remove}")
            return False
        
        return False # Default to false if something unexpected happens

    def run_daily_production(self):
        """Run the full daily production pipeline"""
        self.logger.info(f"Starting daily production for Season {self.season}, Day {self.day_number}")
        
        final_video_path_for_check = None  # Initialize to ensure it's always defined for logging
        try:
            # Step 1: Generate content idea
            topic = self.generate_content_idea()
            self.logger.info(f"Content idea: {topic}")
            
            # Step 2: Generate script
            script = self.generate_script(topic)
            
            # Step 3: Generate images
            image_files = self.generate_images(script)
            
            # Step 4: Generate voice
            audio_file = self.generate_voice(script)
            
            # Step 5: Create final video from images and audio
            final_video = self.create_video_from_images_and_audio(image_files, audio_file)
            final_video_path_for_check = final_video  # Store for logging outside exception block if needed

            # Check if video creation actually succeeded and produced a valid file
            if not final_video or not os.path.exists(final_video) or os.path.getsize(final_video) == 0:
                self.logger.error("Video creation failed or produced an empty/invalid file. Aborting this production cycle.")
                # Check if it's a dummy error file and log its content
                if final_video and os.path.exists(final_video):
                    try:
                        with open(final_video, 'r', encoding='utf-8', errors='replace') as f_check:
                            content = f_check.read(500)  # Read more content for better error diagnosis
                            if "Error:" in content:
                                 self.logger.error(f"Video file content indicates error: {content}")
                            else:
                                 self.logger.info(f"Video file {final_video} exists but might be empty or invalid. Size: {os.path.getsize(final_video)} bytes.")
                    except Exception as e_read:
                        self.logger.error(f"Could not read content of video file {final_video}: {e_read}")
                return  # Stop this run

            # Step 6: Upload to YouTube
            # datetime already imported at the top of the file - no need to reimport
            today_str = datetime.now().strftime("%Y-%m-%d")
            video_file_size = os.path.getsize(final_video) / (1024 * 1024)  # Size in MB
            self.logger.info(f"Preparing to upload video: {final_video} (Size: {video_file_size:.2f} MB)")
            
            # Create a more SEO-friendly title with proper formatting
            title = f"Season {self.season:02d}, Day {self.day_number:02d} - {topic} ({today_str})"
            
            # Create a richer description with hashtags for better discoverability
            keywords = [word for word in topic.split() if len(word) > 3]
            hashtags = " ".join([f"#{word.strip(',.?!').lower()}" for word in keywords[:5]])
            
            description = (
                f"{script}\n\n"
                f"AutoMagic generated this video on {today_str}\n"
                f"Season {self.season}, Day {self.day_number}\n\n"
                f"{hashtags}"
            )
            
            # Track upload attempts for metrics
            metrics_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'upload_metrics.json')
            metrics = {'total_attempts': 0, 'successes': 0, 'failures': 0}
            
            if os.path.exists(metrics_file):
                try:
                    with open(metrics_file, 'r') as f:
                        metrics = json.load(f)
                except Exception as e:
                    self.logger.warning(f"Could not load metrics file: {e}")
            
            metrics['total_attempts'] += 1
            
            # Attempt upload with retry logic
            max_upload_attempts = 3
            for attempt in range(1, max_upload_attempts + 1):
                if attempt > 1:
                    self.logger.info(f"Retry attempt {attempt}/{max_upload_attempts} for uploading to YouTube")
                
                success = self.upload_to_youtube(final_video, title, description)
                
                if success:
                    self.logger.info(f"YouTube upload successful for: {title}")
                    metrics['successes'] += 1
                    
                    # Increment day number for next run
                    self.day_number += 1
                    
                    # Update .env file with new day number
                    try:
                        self._update_env_variable("DAY_NUMBER", str(self.day_number))
                    except Exception as e_env:
                        self.logger.error(f"Failed to update DAY_NUMBER in .env: {e_env}")
                        # Fallback: Create a separate tracking file for day number
                        try:
                            with open('current_day.txt', 'w') as f:
                                f.write(str(self.day_number))
                            self.logger.info(f"Saved current day ({self.day_number}) to fallback file")
                        except Exception as e_fallback:
                            self.logger.error(f"Also failed to write fallback day tracking file: {e_fallback}")
                    
                    self.logger.info(f"Daily production completed successfully! Next run will be Day {self.day_number}")
                    break
                else:
                    if attempt < max_upload_attempts:
                        self.logger.warning(f"Upload attempt {attempt} failed, will retry in 30 seconds...")
                        time.sleep(30)  # Wait before retrying
                    else:
                        self.logger.error("All upload attempts failed")
                        metrics['failures'] += 1
                        self.logger.warning(f"Daily production completed but YouTube upload failed after {max_upload_attempts} attempts")
            
            # Save updated metrics
            try:
                with open(metrics_file, 'w') as f:
                    json.dump(metrics, f)
                self.logger.debug(f"Updated upload metrics: {metrics}")
            except Exception as e_metrics:
                self.logger.warning(f"Could not save metrics: {e_metrics}")
                
        except Exception as e:
            self.logger.error(f"Error in daily production: {str(e)}", exc_info=True)
            if final_video_path_for_check:
                 self.logger.error(f"The video file involved was: {final_video_path_for_check}")
    
    def _update_env_variable(self, variable, value):
        """Update a variable in the .env file"""
        env_path = ".env"
        
        if os.path.exists(env_path):
            with open(env_path, 'r') as file:
                lines = file.readlines()
            
            with open(env_path, 'w') as file:
                for line in lines:
                    if line.startswith(f"{variable}="):
                        file.write(f"{variable}={value}\n")
                    else:
                        file.write(line)
            
            self.logger.info(f"Updated {variable} to {value} in .env file")

def main():
    """Main entrypoint for automation script"""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='AutoMagic Content Production')
    parser.add_argument('--now', action='store_true', help='Run production immediately')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--test', choices=['image', 'voice', 'video', 'upload'], 
                      help='Test a specific component without running the full pipeline')
    parser.add_argument('--list-voices', action='store_true', help='List available ElevenLabs voices')
    args = parser.parse_args()
    
    # Set debug mode
    global DEBUG_MODE
    DEBUG_MODE = args.debug
    if DEBUG_MODE:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    logger.info("Starting AutoMagic automation script")
    
    # Create video production instance
    production = VideoProduction(debug_mode=DEBUG_MODE)
    
    # Handle test modes
    if args.test:
        logger.info(f"Running in test mode: {args.test}")
        
        if args.test == 'image':
            # Test image generation
            test_script = "# Test script\n1. Testing image generation\n2. With multiple topics\n3. For debugging"
            images = production.generate_images(test_script)
            logger.info(f"Test completed: Generated {len(images)} images")
            for img in images:
                logger.info(f"  - {img}")
            return
            
        elif args.test == 'voice':
            # Test voice generation
            test_script = "This is a test of the voice generation system. Testing one two three."
            audio = production.generate_voice(test_script)
            logger.info(f"Test completed: Generated voice at {audio}")
            return
            
        elif args.test == 'video':
            # Test video creation with debug images and audio
            test_script = "# Test script\n1. Testing video generation\n2. With test assets"
            images = production.generate_images(test_script)
            audio = production.generate_voice("This is a test of the automatic video generation system.")
            video = production.create_video_from_images_and_audio(images, audio)
            logger.info(f"Test completed: Generated video at {video}")
            return
            
        elif args.test == 'upload':
            # Test upload functionality with minimal video
            logger.info("Testing upload functionality with a minimal video...")
            # Create a simple test video
            test_video_path = os.path.join(os.getenv("FINAL_VIDEO_SAVE_PATH", "final_videos/"), "test_upload.mp4")
            try:
                # Try to create a 5-second test video
                subprocess.run(
                    ['ffmpeg', '-f', 'lavfi', '-i', 'color=c=blue:s=1280x720:d=5', 
                     '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo:d=5',
                     '-shortest', '-c:v', 'libx264', '-c:a', 'aac', test_video_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True
                )
                logger.info(f"Created test video: {test_video_path}")
                
                # Test upload
                result = production.upload_to_youtube(
                    test_video_path, 
                    "AutoMagic Test Upload", 
                    "This is a test upload from AutoMagic debugging mode."
                )
                logger.info(f"Upload test result: {'Success' if result else 'Failed'}")
                
            except Exception as e:
                logger.error(f"Failed to create test video: {e}")
                if DEBUG_MODE:
                    logger.error(traceback.format_exc())
            return    # List ElevenLabs voices
    if args.list_voices:
        try:
            api_key = os.getenv("ELEVENLABS_API_KEY")
            if not api_key or api_key.startswith("YOUR_"):
                logger.error("Missing or invalid ELEVENLABS_API_KEY in .env file")
                return
                
            from elevenlabs.client import ElevenLabs
            client = ElevenLabs(api_key=api_key)
            voices_response = client.voices.get_all()
            voices = voices_response.voices
            logger.info(f"Available ElevenLabs voices ({len(voices)}):")
            for voice in voices:
                logger.info(f"  - {voice.name}: {voice.voice_id}")
            return
        except Exception as e:
            logger.error(f"Failed to list voices: {e}")
            if DEBUG_MODE:
                logger.error(traceback.format_exc())
            return
    
    # Get scheduled run time from .env
    run_time = os.getenv("DAILY_RUN_TIME", "09:00")
    logger.info(f"Scheduled to run daily at {run_time}")
    
    # Schedule daily run
    schedule.every().day.at(run_time).do(production.run_daily_production)
    
    # Also provide a way to run it immediately for testing
    if args.now:
        logger.info("Running production now as requested")
        production.run_daily_production()
    else:
        logger.info(f"Waiting for scheduled time ({run_time})...")
        logger.info("(Run with --now flag to execute immediately)")
        
        # Run continuously to check schedule
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
