#!/usr/bin/env python3
# automation_script_optimized.py - Optimized automation script for AutoMagic
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
import tempfile
import openai
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import shutil
import elevenlabs
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from PIL import Image, ImageDraw, ImageFont

# Add trend integration
try:
    from trend_integration import get_trending_topic, get_content_adaptation
    TREND_MODULE_AVAILABLE = True
except ImportError:
    TREND_MODULE_AVAILABLE = False

# Add mask_api_key function at the top
def mask_api_key(key):
    """Mask an API key for secure display."""
    if not key or len(key) < 8:
        return "Not configured"
    return f"{key[:4]}...{key[-4:]}"

# Load environment variables
load_dotenv()

# Configure logging
log_path = os.getenv("LOG_FILE_PATH", "logs/automagic.log")
log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO"))
os.makedirs(os.path.dirname(log_path), exist_ok=True)

logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class OptimizedVideoProduction:
    def __init__(self):
        self.logger = logging.getLogger("AutoMagic")
        self.season = int(os.getenv("SEASON", 1))
        self.day_number = int(os.getenv("DAY_NUMBER", 1))
        self.openai_client = None
        self.elevenlabs_client = None
        
        # Initialize API clients
        self._init_api_clients()
        
    def _init_api_clients(self):
        """Initialize API clients with proper error handling"""
        try:
            # OpenAI client
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                self.openai_client = openai.OpenAI(api_key=openai_key)
                self.logger.info("OpenAI client initialized successfully")
            else:
                self.logger.warning("OpenAI API key not found")
                
            # ElevenLabs client  
            elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
            if elevenlabs_key:
                elevenlabs.set_api_key(elevenlabs_key)
                self.elevenlabs_client = elevenlabs
                self.logger.info("ElevenLabs client initialized successfully")
            else:
                self.logger.warning("ElevenLabs API key not found")
                
        except Exception as e:
            self.logger.error(f"Error initializing API clients: {e}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_content_idea(self):
        """Generate content idea with trending integration and fallbacks"""
        self.logger.info("Generating content idea...")
        
        # Try trending topics first if available
        if TREND_MODULE_AVAILABLE:
            try:
                topic = get_trending_topic()
                if topic:
                    self.logger.info(f"Using trending topic: {topic}")
                    return topic
            except Exception as e:
                self.logger.warning(f"Error getting trending topic: {e}")
        
        # Fallback to OpenAI generation
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{
                        "role": "user", 
                        "content": f"Generate a compelling YouTube video topic for Season {self.season}, Day {self.day_number}. Focus on educational, entertaining, or trending subjects. Return only the topic title."
                    }],
                    max_tokens=50,
                    temperature=0.7
                )
                topic = response.choices[0].message.content.strip()
                self.logger.info(f"Generated topic via OpenAI: {topic}")
                return topic
            except Exception as e:
                self.logger.error(f"Error with OpenAI topic generation: {e}")
        
        # Final fallback - predefined topics
        fallback_topics = [
            "How to train your brain to remember anything",
            "The secret to perfect sourdough bread", 
            "Unusual morning routines of successful people",
            "5 mind-blowing facts about space exploration",
            "Simple tricks to boost your productivity",
            "The science behind procrastination"
        ]
        
        topic = random.choice(fallback_topics)
        self.logger.info(f"Using fallback topic: {topic}")
        return topic

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_script(self, topic):
        """Generate script with improved structure and error handling"""
        self.logger.info(f"Generating script for topic: {topic}")
        
        if not self.openai_client:
            self.logger.error("OpenAI client not available for script generation")
            return f"Introduction: Today we explore {topic}.\n\nMain content about {topic}.\n\nConclusion: Thanks for watching!"
        
        try:
            prompt = f"""Create a concise, engaging YouTube video script about: {topic}

Structure:
- Hook (attention-grabbing opening)
- Introduction (15-30 seconds)
- 3 Main Points (45-60 seconds each)
- Conclusion with call-to-action (15 seconds)

Make it conversational, informative, and suitable for a 3-4 minute video.
Focus on practical value and engagement."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.7
            )
            
            script = response.choices[0].message.content.strip()
            self.logger.info("Script generated successfully")
            return script
            
        except Exception as e:
            self.logger.error(f"Error generating script: {e}")
            return f"Introduction: Today we explore {topic}.\n\nMain content about {topic}.\n\nConclusion: Thanks for watching!"

    def create_video_from_images_and_audio_optimized(self, image_files, audio_file):
        """Optimized video creation with better FFmpeg handling"""
        self.logger.info("Creating optimized video from images and audio...")
        
        # Setup paths
        today = datetime.now().strftime("%Y-%m-%d")
        final_video_dir = os.getenv("FINAL_VIDEO_SAVE_PATH", "final_videos/")
        os.makedirs(final_video_dir, exist_ok=True)
        
        final_video_path = os.path.join(
            final_video_dir,
            f"S{self.season}_D{self.day_number}_{today}.mp4"
        )
        
        # Validate inputs
        if not image_files:
            self.logger.error("No images provided")
            return None
            
        valid_images = [img for img in image_files if os.path.exists(img) and self._is_valid_image(img)]
        if not valid_images:
            self.logger.error("No valid images found")
            return None
            
        if not os.path.exists(audio_file) or not self._is_valid_audio(audio_file):
            self.logger.error(f"Invalid audio file: {audio_file}")
            return None
        
        try:
            # Use MoviePy for more reliable video creation
            from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip
            
            # Get audio duration to calculate timing
            audio_clip = AudioFileClip(audio_file)
            total_duration = audio_clip.duration
            
            # Calculate duration per image
            duration_per_image = max(2.0, total_duration / len(valid_images))
            
            # Create video clips from images
            video_clips = []
            for img_path in valid_images:
                try:
                    clip = ImageClip(img_path, duration=duration_per_image)
                    # Resize to consistent dimensions
                    clip = clip.resize(height=720).resize(width=1280)
                    video_clips.append(clip)
                except Exception as e:
                    self.logger.warning(f"Failed to process image {img_path}: {e}")
                    continue
            
            if not video_clips:
                self.logger.error("No valid video clips created")
                return None
            
            # Concatenate video clips
            final_video = concatenate_videoclips(video_clips, method="compose")
            
            # Adjust video duration to match audio
            if final_video.duration > total_duration:
                final_video = final_video.subclip(0, total_duration)
            elif final_video.duration < total_duration:
                # Loop the video to match audio duration
                loops_needed = int(total_duration / final_video.duration) + 1
                final_video = concatenate_videoclips([final_video] * loops_needed)
                final_video = final_video.subclip(0, total_duration)
            
            # Set audio
            final_video = final_video.set_audio(audio_clip)
            
            # Write video file
            final_video.write_videofile(
                final_video_path,
                codec='libx264',
                audio_codec='aac',
                fps=24,
                preset='medium',
                logger=None  # Suppress MoviePy verbose output
            )
            
            # Cleanup
            audio_clip.close()
            final_video.close()
            for clip in video_clips:
                clip.close()
            
            # Verify output
            if os.path.exists(final_video_path) and os.path.getsize(final_video_path) > 1000:
                self.logger.info(f"Video created successfully: {final_video_path}")
                return final_video_path
            else:
                self.logger.error("Video creation failed - invalid output file")
                return None
                
        except Exception as e:
            self.logger.error(f"Error in optimized video creation: {e}")
            
            # Fallback to FFmpeg direct command
            return self._create_video_ffmpeg_fallback(valid_images, audio_file, final_video_path)
    
    def _create_video_ffmpeg_fallback(self, image_files, audio_file, output_path):
        """Fallback video creation using direct FFmpeg commands"""
        self.logger.info("Using FFmpeg fallback for video creation...")
        
        try:
            # Create input file list for FFmpeg
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
                for img in image_files:
                    f.write(f"file '{os.path.abspath(img).replace(chr(92), '/')}'\n")
                    f.write("duration 3\n")
                input_file = f.name
            
            # FFmpeg command for creating video
            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0', 
                '-i', input_file,
                '-i', audio_file,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-pix_fmt', 'yuv420p',
                '-shortest',
                '-r', '24',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Cleanup temp file
            os.unlink(input_file)
            
            if result.returncode == 0 and os.path.exists(output_path):
                self.logger.info(f"FFmpeg fallback successful: {output_path}")
                return output_path
            else:
                self.logger.error(f"FFmpeg fallback failed: {result.stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"FFmpeg fallback error: {e}")
            return None

    def _is_valid_image(self, image_path):
        """Validate image file"""
        try:
            with Image.open(image_path) as img:
                img.verify()
            return True
        except Exception:
            return False
    
    def _is_valid_audio(self, audio_path):
        """Validate audio file"""
        if not os.path.exists(audio_path):
            return False
        if os.path.getsize(audio_path) < 1000:  # Minimum size check
            return False
        return audio_path.lower().endswith(('.mp3', '.wav', '.aac', '.ogg'))

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_images_optimized(self, script, num_images=3):
        """Optimized image generation with better error handling"""
        self.logger.info("Generating optimized images...")
        
        image_save_path = os.getenv("IMAGE_SAVE_PATH", "generated_images/")
        os.makedirs(image_save_path, exist_ok=True)
        
        image_files = []
        
        if self.openai_client:
            for i in range(num_images):
                try:
                    # Create contextual prompt
                    prompt = f"High-quality, professional image representing: {script[:200]}... Style: modern, clean, engaging for YouTube thumbnail. Image {i+1} of {num_images}."
                    
                    response = self.openai_client.images.generate(
                        model="dall-e-3",
                        prompt=prompt,
                        size="1024x1024",
                        quality="standard",
                        n=1
                    )
                    
                    # Download image
                    image_url = response.data[0].url
                    img_response = requests.get(image_url, timeout=30)
                    img_response.raise_for_status()
                    
                    # Save image
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    image_path = os.path.join(image_save_path, f"image_{i+1}_{timestamp}.jpg")
                    
                    with open(image_path, 'wb') as f:
                        f.write(img_response.content)
                    
                    if self._is_valid_image(image_path):
                        image_files.append(image_path)
                        self.logger.info(f"Generated image {i+1}: {image_path}")
                    else:
                        self.logger.warning(f"Generated invalid image: {image_path}")
                        
                except Exception as e:
                    self.logger.warning(f"Failed to generate image {i+1}: {e}")
                    continue
        
        # Create fallback images if needed
        while len(image_files) < num_images:
            try:
                fallback_path = self._create_fallback_image(image_save_path, len(image_files) + 1)
                if fallback_path:
                    image_files.append(fallback_path)
            except Exception as e:
                self.logger.error(f"Failed to create fallback image: {e}")
                break
        
        self.logger.info(f"Generated {len(image_files)} images total")
        return image_files
    
    def _create_fallback_image(self, save_path, index):
        """Create a fallback image when AI generation fails"""
        try:
            # Create a simple gradient image
            img = Image.new('RGB', (1024, 1024), color='#4A90E2')
            draw = ImageDraw.Draw(img)
            
            # Add text
            try:
                font = ImageFont.truetype("arial.ttf", 60)
            except:
                font = ImageFont.load_default()
            
            text = f"AutoMagic\nS{self.season}D{self.day_number}\nImage {index}"
            
            # Calculate text position
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (1024 - text_width) // 2
            y = (1024 - text_height) // 2
            
            draw.text((x, y), text, fill='white', font=font, align='center')
            
            # Save fallback image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fallback_path = os.path.join(save_path, f"fallback_{index}_{timestamp}.jpg")
            img.save(fallback_path, 'JPEG', quality=85)
            
            return fallback_path
            
        except Exception as e:
            self.logger.error(f"Error creating fallback image: {e}")
            return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_voice_optimized(self, script):
        """Optimized voice generation with robust fallbacks"""
        self.logger.info("Generating optimized voice narration...")
        
        audio_save_path = os.getenv("AUDIO_SAVE_PATH", "generated_audio/")
        os.makedirs(audio_save_path, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_path = os.path.join(audio_save_path, f"narration_{timestamp}.mp3")
        
        # Try ElevenLabs first
        if self.elevenlabs_client:
            try:
                voice_id = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")
                
                # Clean script for TTS
                clean_script = self._clean_script_for_tts(script)
                
                audio = elevenlabs.generate(
                    text=clean_script,
                    voice=voice_id,
                    model="eleven_multilingual_v2"
                )
                
                elevenlabs.save(audio, audio_path)
                
                if os.path.exists(audio_path) and self._is_valid_audio(audio_path):
                    self.logger.info(f"ElevenLabs audio generated: {audio_path}")
                    return audio_path
                else:
                    self.logger.warning("ElevenLabs audio validation failed")
                    
            except Exception as e:
                self.logger.warning(f"ElevenLabs generation failed: {e}")
        
        # Fallback to silent audio generation
        return self._generate_silent_audio(audio_path)
    
    def _clean_script_for_tts(self, script):
        """Clean script text for better TTS pronunciation"""
        # Remove stage directions and formatting
        lines = script.split('\n')
        clean_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('[') and not line.startswith('('):
                # Remove common formatting markers
                line = line.replace('**', '').replace('*', '').replace('_', '')
                clean_lines.append(line)
        
        return ' '.join(clean_lines)
    
    def _generate_silent_audio(self, output_path):
        """Generate silent audio as fallback"""
        try:
            # Use FFmpeg to generate silent audio
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', 'anullsrc=r=44100:cl=stereo',
                '-t', '60',  # 60 seconds
                '-c:a', 'libmp3lame',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and os.path.exists(output_path):
                self.logger.info(f"Silent audio fallback created: {output_path}")
                return output_path
            else:
                self.logger.error(f"Silent audio generation failed: {result.stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error generating silent audio: {e}")
            return None

    def run_optimized_production(self):
        """Run the complete optimized production pipeline"""
        self.logger.info(f"Starting optimized production for Season {self.season}, Day {self.day_number}")
        
        try:
            # Step 1: Generate content idea
            topic = self.generate_content_idea()
            
            # Step 2: Generate script
            script = self.generate_script(topic)
            
            # Step 3: Generate images (parallel would be ideal but keeping sequential for stability)
            images = self.generate_images_optimized(script)
            if not images:
                self.logger.error("No images generated, aborting production")
                return False
            
            # Step 4: Generate voice
            audio = self.generate_voice_optimized(script)
            if not audio:
                self.logger.error("No audio generated, aborting production")
                return False
            
            # Step 5: Create video
            video_path = self.create_video_from_images_and_audio_optimized(images, audio)
            if not video_path:
                self.logger.error("Video creation failed, aborting production")
                return False
            
            self.logger.info(f"Production completed successfully: {video_path}")
            
            # Update day counter
            self._update_day_counter()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Production failed: {e}", exc_info=True)
            return False
    
    def _update_day_counter(self):
        """Update day and season counters"""
        try:
            new_day = self.day_number + 1
            new_season = self.season
            
            # Reset to new season after 30 days (configurable)
            max_days_per_season = int(os.getenv("MAX_DAYS_PER_SEASON", 30))
            if new_day > max_days_per_season:
                new_day = 1
                new_season += 1
            
            # Update environment file
            env_path = ".env"
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    content = f.read()
                
                # Update or add SEASON and DAY_NUMBER
                import re
                content = re.sub(r'^SEASON=.*$', f'SEASON={new_season}', content, flags=re.MULTILINE)
                content = re.sub(r'^DAY_NUMBER=.*$', f'DAY_NUMBER={new_day}', content, flags=re.MULTILINE)
                
                # If not found, append
                if 'SEASON=' not in content:
                    content += f'\nSEASON={new_season}'
                if 'DAY_NUMBER=' not in content:
                    content += f'\nDAY_NUMBER={new_day}'
                
                with open(env_path, 'w') as f:
                    f.write(content)
                
                self.logger.info(f"Updated counters: Season {new_season}, Day {new_day}")
                
        except Exception as e:
            self.logger.error(f"Error updating day counter: {e}")

def main():
    """Main execution function"""
    logger = logging.getLogger("AutoMagic")
    
    # Create production instance
    production = OptimizedVideoProduction()
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="AutoMagic Optimized Video Production")
    parser.add_argument("--now", action="store_true", help="Run immediately instead of scheduling")
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    
    args = parser.parse_args()
    
    if args.test:
        logger.info("Running in test mode...")
        success = production.run_optimized_production()
        if success:
            logger.info("Test completed successfully")
        else:
            logger.error("Test failed")
        return
    
    if args.now:
        logger.info("Running production immediately...")
        success = production.run_optimized_production()
        if success:
            logger.info("Immediate production completed successfully")
        else:
            logger.error("Immediate production failed")
        return
    
    # Schedule regular production
    run_time = os.getenv("DAILY_RUN_TIME", "09:00")
    logger.info(f"Scheduling daily production at {run_time}")
    
    schedule.every().day.at(run_time).do(production.run_optimized_production)
    
    logger.info("AutoMagic optimized scheduler started. Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")

if __name__ == "__main__":
    main()