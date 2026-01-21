#!/usr/bin/env python3
# automation_script.py - Main automation script for 
import os
import sys
import logging
import schedule
import time
import json
import random
import subprocess
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import ffmpeg  # Added for ffmpeg-python
import tempfile  # Added for temporary files

# Load environment variables
load_dotenv()

# Configure logging
log_path = os.getenv("LOG_FILE_PATH", "logs/.log")
log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO"))
os.makedirs(os.path.dirname(log_path), exist_ok=True)

logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("")

# Make sure directories exist
for dir_path in [
    os.getenv("IMAGE_SAVE_PATH", "generated_images/"),
    os.getenv("AUDIO_SAVE_PATH", "generated_audio/"),
    os.getenv("FINAL_VIDEO_SAVE_PATH", "final_videos/")
]:
    os.makedirs(dir_path, exist_ok=True)

class VideoProduction:
    def __init__(self):
        self.season = int(os.getenv("SEASON", 1))
        self.day_number = int(os.getenv("DAY_NUMBER", 1))
        self.logger = logger
        
        # Check if required API keys are present
        self._check_api_keys()

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
        
        # Simulated script - would use OpenAI in production
        return f"""
# {topic}

## Introduction
Welcome to another exciting episode! Today we're diving into {topic}.

## Main Points
1. First, let's understand the basics
2. Next, we'll explore some interesting examples
3. Finally, I'll share some practical tips you can use today

## Conclusion
Thanks for watching! If you enjoyed this video, don't forget to like and subscribe.
"""

    def generate_images(self, script):
        """Generate images based on the script"""
        self.logger.info("Generating images...")
        
        # Import Pillow for image generation
        from PIL import Image, ImageDraw, ImageFont
        import random
        
        # Extract potential image topics from script
        lines = script.strip().split('\n')
        image_topics = [line for line in lines if line.startswith('1. ') or 
                                               line.startswith('2. ') or 
                                               line.startswith('3. ')]
        
        # Simulated image generation - would use DALL-E in production
        image_files = []
        for i, topic in enumerate(image_topics):
            img_path = os.path.join(os.getenv("IMAGE_SAVE_PATH", "generated_images/"), f"image_{i+1}.jpg")
            
            # Create a simple colored image with text
            width, height = 1280, 720  # 720p
            # Generate a random background color
            bg_color = (
                random.randint(50, 200),
                random.randint(50, 200),
                random.randint(50, 200)
            )
            text_color = (255, 255, 255)  # White text
            
            # Create image and draw object
            img = Image.new('RGB', (width, height), color=bg_color)
            draw = ImageDraw.Draw(img)
            
            # Try to use a system font
            try:
                # For Windows, try a common font
                if os.name == 'nt':
                    font_path = "C:\\Windows\\Fonts\\Arial.ttf"
                else:
                    # For Unix/Linux/Mac, try a common font
                    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
                    if not os.path.exists(font_path):
                        # Fallback for Mac
                        font_path = "/System/Library/Fonts/Helvetica.ttc"
                
                if os.path.exists(font_path):
                    title_font = ImageFont.truetype(font_path, 40)
                    subtitle_font = ImageFont.truetype(font_path, 30)
                else:
                    # Use default font if system font not found
                    title_font = ImageFont.load_default()
                    subtitle_font = ImageFont.load_default()
            except Exception as e:
                self.logger.warning(f"Could not load font: {e}. Using default.")
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
            
            # Draw title
            title = f"Topic {i+1}"
            draw.text((width//2, height//4), title, fill=text_color, font=title_font, anchor="mm")
            
            # Draw topic text, wrap if needed
            words = topic.split()
            lines_of_text = []
            current_line = []
            
            for word in words:
                current_line.append(word)
                text_width = draw.textlength(" ".join(current_line), font=subtitle_font)
                if text_width > width - 200:  # Keep a margin
                    current_line.pop()  # Remove the last word
                    lines_of_text.append(" ".join(current_line))
                    current_line = [word]
            
            if current_line:
                lines_of_text.append(" ".join(current_line))
            
            # Draw each line
            for idx, line in enumerate(lines_of_text):
                y_position = height//2 + idx * 50
                draw.text((width//2, y_position), line, fill=text_color, font=subtitle_font, anchor="mm")
            
            # Add a decorative circle or box
            draw.ellipse((width//2 - 300, height//2 - 200, width//2 + 300, height//2 + 200), 
                       outline=(255, 255, 255), width=5)
            # Save the image
            try:
                img.save(img_path, format="JPEG")
                
                # Verify the image was saved correctly
                if os.path.exists(img_path) and os.path.getsize(img_path) > 0:
                    # Try to open the image to verify it's valid
                    test_img = Image.open(img_path)
                    test_img.verify()  # Verify image integrity
                    image_files.append(img_path)
                    self.logger.debug(f"Successfully generated and verified image: {img_path}")
                else:
                    self.logger.error(f"Failed to save image: {img_path} (file doesn't exist or is empty)")
            except Exception as e:
                self.logger.error(f"Error saving/verifying image {img_path}: {str(e)}")
                # If there was an error, try one more time with a simpler image
                try:
                    simple_img = Image.new('RGB', (640, 480), color=(100, 100, 100))
                    simple_draw = ImageDraw.Draw(simple_img)
                    simple_draw.text((320, 240), f"Backup Image {i+1}", fill=(255, 255, 255))
                    simple_img.save(img_path, format="JPEG")
                    if os.path.exists(img_path) and os.path.getsize(img_path) > 0:
                        image_files.append(img_path)
                        self.logger.debug(f"Successfully generated backup image: {img_path}")
                except Exception as e2:
                    self.logger.error(f"Failed to create even a simple backup image: {str(e2)}")
        
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
        self.logger.info("Generating voice narration...")
        
        # Extract narration text
        lines = script.strip().split('\n')
        narration_lines = [line for line in lines if not line.startswith('#') and line.strip()]
        narration_text = ' '.join(narration_lines)
        
        # Simulated voice generation - would use ElevenLabs in production
        audio_path = os.path.join(os.getenv("AUDIO_SAVE_PATH", "generated_audio/"), "narration.mp3")
        
        # Check if a valid audio file already exists - don't overwrite if it's good
        if os.path.exists(audio_path) and self._is_valid_audio(audio_path):
            self.logger.info(f"Using existing valid audio file: {audio_path}")
            return audio_path
        
        # Create a silent MP3 file for testing purposes
        success = False
        
        # Method 1: Try using ffmpeg-python
        try:
            # Using ffmpeg-python to create a silent audio file
            import ffmpeg
            
            # Create silent audio - 10 seconds duration
            duration = 10  # seconds
            
            self.logger.info(f"Generating silent audio using ffmpeg-python...")
            (
                ffmpeg
                .input('anullsrc', format='lavfi', t=str(duration))
                .output(audio_path, acodec='libmp3lame', ar='44100')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )
            
            # Verify the file was created successfully
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 1000:
                # Do additional validation
                if self._is_valid_audio(audio_path):
                    self.logger.info(f"Successfully generated silent audio file: {audio_path}")
                    success = True
                else:
                    self.logger.warning(f"Audio file exists but may not be valid: {audio_path}")
            else:
                self.logger.warning(f"Audio file missing or too small: {audio_path}")
                
        except Exception as e:
            self.logger.error(f"Error generating audio with ffmpeg-python: {str(e)}")
            
        # Method 2: If Method 1 failed, try using subprocess with ffmpeg directly
        if not success:
            try:
                import subprocess
                self.logger.warning("Trying direct ffmpeg command as fallback...")
                
                # Ensure audio directory exists
                audio_dir = os.path.dirname(audio_path)
                os.makedirs(audio_dir, exist_ok=True)
                
                # Clean up any partial file that might exist
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                
                # Run ffmpeg command directly - more explicit for better reliability
                duration = 10  # seconds
                
                if os.name == 'nt':  # Windows
                    # On Windows, use subprocess with shell=True to avoid path issues
                    result = subprocess.run(
                        f'ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t {duration} -q:a 2 -acodec libmp3lame "{audio_path}"',
                        shell=True, 
                        capture_output=True,
                        text=True
                    )
                else:  # Linux, macOS
                    # On Unix systems, use array form
                    result = subprocess.run([
                        'ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono', 
                        '-t', str(duration), '-q:a', '2', '-acodec', 'libmp3lame', 
                        audio_path
                    ], capture_output=True, text=True)
                
                if result.returncode == 0 and os.path.exists(audio_path) and os.path.getsize(audio_path) > 1000:
                    if self._is_valid_audio(audio_path):
                        self.logger.info(f"Successfully generated silent audio via subprocess: {audio_path}")
                        success = True
                    else:
                        self.logger.warning(f"Audio file created via subprocess but may not be valid")
                else:
                    self.logger.error(f"Subprocess ffmpeg command failed: {result.stderr}")
            except Exception as e2:
                self.logger.error(f"Error with fallback audio generation: {str(e2)}")
        
        # Method 3: Last resort - copy a pre-packaged test audio file if it exists
        if not success:
            try:
                test_audio = os.path.join(os.getenv("AUDIO_SAVE_PATH", "generated_audio/"), "test_audio.mp3")
                if os.path.exists(test_audio) and os.path.getsize(test_audio) > 1000:
                    import shutil
                    shutil.copy(test_audio, audio_path)
                    self.logger.warning(f"Using backup test audio file: {test_audio}")
                    if self._is_valid_audio(audio_path):
                        success = True
                    else:
                        self.logger.error(f"Backup audio file exists but is not valid")
            except Exception as e3:
                self.logger.error(f"Error copying backup audio file: {str(e3)}")
        
        # Final check and error handling
        if not success:
            self.logger.critical("CRITICAL: All audio generation methods failed!")
            # Create a more descriptive error message for debugging
            try:
                with open(audio_path + ".error.txt", 'w') as f:
                    f.write(f"ERROR: Could not generate valid audio file. Check logs for details.")
                # Try to create a clearly labeled invalid MP3 that won't cause FFmpeg to crash
                with open(audio_path, 'wb') as f:
                    # Write MP3 file header to make it minimally recognizable as MP3
                    f.write(b'\xFF\xFB\x90\x44\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
                    f.write(b'\x54\x41\x47\x00' + b'ERROR AUDIO' + b'\x00' * 128)
            except Exception as ex_write:
                self.logger.error(f"Failed to write error placeholder: {ex_write}")
                
        self.logger.info(f"Voice narration process completed: {audio_path} (success={success})")
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
                                shortest=None,
                                loglevel="error" 
                               )
                        .overwrite_output()
                        .run(capture_stdout=True, capture_stderr=True)
                    )
                except Exception as e:
                    self.logger.warning(f"First attempt at adding audio failed: {str(e)}")
                    # Fallback to alternative approach if first one fails
                    self.logger.info("Trying alternative FFmpeg approach")
                    (
                        ffmpeg.concat(video_stream, audio_stream, v=1, a=1)
                        .output(final_video_path, vcodec='copy', acodec='aac')
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
                    with open(final_video_path, 'w') as f: f.write(f"Error: ffmpeg failed. Stderr: {stderr_msg[:500]}")
                except Exception as ex_write:
                     self.logger.error(f"Failed to write dummy error file after ffmpeg error: {ex_write}")
            return final_video_path 
        except Exception as e_gen:
            self.logger.error(f"General error in create_video_from_images_and_audio: {str(e_gen)}", exc_info=True)
            if not os.path.exists(final_video_path) or os.path.getsize(final_video_path) == 0:
                try:
                    with open(final_video_path, 'w') as f: f.write(f"Error: General error during video creation. Error: {str(e_gen)[:500]}")
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
        self.logger.info(f"Simulating upload to YouTube: {title}")
        
        # Check if required YouTube credentials are present
        yt_creds = [
            os.getenv("YOUTUBE_CLIENT_ID"),
            os.getenv("YOUTUBE_CLIENT_SECRET"),
            os.getenv("YOUTUBE_CHANNEL_ID")
        ]
        
        if any(not cred or cred.startswith("YOUR_") for cred in yt_creds):
            self.logger.warning("YouTube credentials not properly configured. Skipping upload.")
            return False
            
        # Simulated YouTube upload - would use YouTube API in production
        self.logger.info(f"Would upload {video_path} to YouTube with title: {title}")
        return True
    
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
            title = f"S{self.season} D{self.day_number}: {topic}"
            description = f" generated video on {topic}\n\nSeason {self.season}, Day {self.day_number}"
            
            success = self.upload_to_youtube(final_video, title, description)
            if success:
                self.logger.info("Daily production completed successfully!")
                # Increment day number for next run
                self.day_number += 1
                # Update .env file with new day number
                self._update_env_variable("DAY_NUMBER", str(self.day_number))
            else:
                self.logger.warning("Daily production completed but upload failed")
                
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
    logger.info("Starting  automation script")
    
    # Create video production instance
    production = VideoProduction()
    
    # Get scheduled run time from .env
    run_time = os.getenv("DAILY_RUN_TIME", "09:00")
    logger.info(f"Scheduled to run daily at {run_time}")
    
    # Schedule daily run
    schedule.every().day.at(run_time).do(production.run_daily_production)
    
    # Also provide a way to run it immediately for testing
    if len(sys.argv) > 1 and sys.argv[1] == "--now":
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
