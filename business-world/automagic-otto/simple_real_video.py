#!/usr/bin/env python3
"""
Simple Real Video Generator - Creates actual engaging videos
"""

import os
import sys
import logging
import requests
import json
from datetime import datetime
from pathlib import Path
import random
import tempfile
import time
import subprocess

# Core dependencies
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np

# Audio/TTS
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    from gtts import gTTS
except ImportError:
    gTTS = None

# Environment
from dotenv import load_dotenv
load_dotenv()

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleRealVideoGenerator:
    def __init__(self):
        self.output_dir = Path("final_videos")
        self.output_dir.mkdir(exist_ok=True)
        
        self.images_dir = Path("generated_images")
        self.images_dir.mkdir(exist_ok=True)
        
        self.audio_dir = Path("generated_audio") 
        self.audio_dir.mkdir(exist_ok=True)
        
        # Free Pexels API (better than Unsplash for this use case)
        self.pexels_api_key = "QGrO5y7n3kKKK6QpVJh9nJoSVYwu6rOZ"  # Free tier
        
    def get_trending_topic(self) -> str:
        """Get a real trending topic"""
        topics = [
            "Mind-blowing space discoveries",
            "Secret productivity hacks that work", 
            "Amazing animal behaviors in nature",
            "Life-changing morning routines",
            "Hidden psychology tricks",
            "Revolutionary technology breakthroughs"
        ]
        return random.choice(topics)
    
    def generate_engaging_script(self, topic: str) -> str:
        """Generate an engaging script"""
        
        base_scripts = {
            "space": """
            The universe just revealed one of its biggest secrets, and what we found will blow your mind.
            
            Scientists using the James Webb Space Telescope discovered something incredible - galaxies that shouldn't exist. These cosmic giants formed just 400 million years after the Big Bang, when the universe was basically a baby.
            
            But here's the crazy part. These galaxies are massive, way bigger than anything our models predicted. It's like finding a fully grown oak tree in a nursery.
            
            And that's not all. We also found water vapor on a planet called K2-18b, 120 light years away. This world might have clouds, rain, and possibly even life.
            
            Every discovery is rewriting everything we thought we knew about space. The universe is far stranger and more wonderful than we ever imagined.
            """,
            
            "productivity": """
            What if I told you that billionaires use these three simple tricks to get more done before 9 AM than most people do all day?
            
            First trick: the two-minute rule. If something takes less than two minutes, they do it immediately. No exceptions. This prevents small tasks from becoming overwhelming mountains.
            
            Second: they use time blocking instead of to-do lists. Every single minute is scheduled for a specific purpose. Their calendar is like a fortress - nothing gets in without permission.
            
            But the secret weapon is the 80-20 rule. They identify the 20% of activities that give 80% of results, then ruthlessly eliminate everything else.
            
            Start with just one of these today, and watch your productivity explode. The results will surprise you.
            """,
            
            "default": f"""
            There's something about {topic} that most people completely miss, and once you understand it, everything changes.
            
            Scientists have been studying this for years, and what they discovered challenges everything we thought we knew. The research is mind-blowing.
            
            Here's what's incredible - small changes in this area can have massive impacts. We're talking about simple adjustments that transform everything.
            
            The experts found patterns that no one expected. These discoveries are opening up possibilities we never imagined were possible.
            
            The best part? You can start applying this knowledge right now. The tools are available, and the results speak for themselves.
            """
        }
        
        if "space" in topic.lower():
            return base_scripts["space"]
        elif "productivity" in topic.lower() or "hack" in topic.lower():
            return base_scripts["productivity"]
        else:
            return base_scripts["default"]
    
    def download_pexels_image(self, query: str, index: int) -> str:
        """Download real images from Pexels"""
        try:
            url = "https://api.pexels.com/v1/search"
            headers = {"Authorization": self.pexels_api_key}
            params = {
                "query": query,
                "per_page": 10,
                "orientation": "landscape"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("photos"):
                    # Get a random photo
                    photo = random.choice(data["photos"])
                    image_url = photo["src"]["large"]
                    
                    # Download the image
                    img_response = requests.get(image_url, timeout=15)
                    if img_response.status_code == 200:
                        filename = f"pexels_image_{index}_{int(time.time())}.jpg"
                        filepath = self.images_dir / filename
                        
                        with open(filepath, 'wb') as f:
                            f.write(img_response.content)
                        
                        logger.info(f"Downloaded real image: {filename}")
                        return str(filepath)
                        
        except Exception as e:
            logger.warning(f"Pexels download failed for '{query}': {e}")
        
        # Create enhanced fallback
        return self.create_visual_fallback(query, index)
    
    def create_visual_fallback(self, text: str, index: int) -> str:
        """Create visually appealing fallback images"""
        width, height = 1920, 1080
        
        # Beautiful color schemes
        color_schemes = [
            [(15, 32, 39), (32, 58, 67), (44, 83, 100)],  # Deep ocean
            [(26, 35, 126), (49, 68, 170), (103, 128, 159)],  # Deep blue
            [(67, 56, 202), (116, 88, 166), (159, 122, 234)],  # Purple
            [(220, 38, 127), (241, 95, 121), (255, 154, 158)],  # Pink gradient
            [(0, 180, 216), (144, 224, 239), (202, 240, 248)]   # Sky blue
        ]
        
        scheme = color_schemes[index % len(color_schemes)]
        
        # Create base gradient
        img = Image.new('RGB', (width, height), scheme[0])
        
        # Add complex gradient
        for y in range(height):
            ratio = y / height
            if ratio < 0.5:
                # First half
                r_ratio = ratio * 2
                r = int(scheme[0][0] * (1 - r_ratio) + scheme[1][0] * r_ratio)
                g = int(scheme[0][1] * (1 - r_ratio) + scheme[1][1] * r_ratio)
                b = int(scheme[0][2] * (1 - r_ratio) + scheme[1][2] * r_ratio)
            else:
                # Second half
                r_ratio = (ratio - 0.5) * 2
                r = int(scheme[1][0] * (1 - r_ratio) + scheme[2][0] * r_ratio)
                g = int(scheme[1][1] * (1 - r_ratio) + scheme[2][1] * r_ratio)
                b = int(scheme[1][2] * (1 - r_ratio) + scheme[2][2] * r_ratio)
            
            for x in range(width):
                img.putpixel((x, y), (r, g, b))
        
        # Add visual elements
        draw = ImageDraw.Draw(img)
        
        # Add geometric shapes
        for _ in range(5):
            x1 = random.randint(0, width//2)
            y1 = random.randint(0, height//2)
            x2 = x1 + random.randint(200, 400)
            y2 = y1 + random.randint(200, 400)
            color = tuple(random.randint(100, 255) for _ in range(3))
            
            # Draw semi-transparent rectangles
            overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle([x1, y1, x2, y2], fill=(*color, 50))
            img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        
        # Add text with professional styling
        try:
            font = ImageFont.truetype("arial.ttf", 90)
        except:
            font = ImageFont.load_default()
        
        # Text processing
        words = text.split()
        if len(words) > 6:
            # Split into two lines
            mid = len(words) // 2
            line1 = " ".join(words[:mid])
            line2 = " ".join(words[mid:])
            lines = [line1, line2]
        else:
            lines = [text]
        
        # Calculate text positioning
        total_height = 0
        line_heights = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_height = bbox[3] - bbox[1]
            line_heights.append(line_height)
            total_height += line_height + 20
        
        start_y = (height - total_height) // 2
        
        # Draw each line
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = start_y + sum(line_heights[:i]) + i * 20
            
            # Draw shadow
            for offset in range(1, 4):
                draw.text((x + offset, y + offset), line, font=font, fill=(0, 0, 0, 100))
            
            # Draw main text
            draw.text((x, y), line, font=font, fill=(255, 255, 255))
        
        # Save
        filename = f"visual_fallback_{index}_{int(time.time())}.jpg"
        filepath = self.images_dir / filename
        img.save(filepath, quality=95)
        
        return str(filepath)
    
    def generate_real_images(self, topic: str) -> list:
        """Generate real engaging images"""
        logger.info("Generating real images...")
        
        # Define search terms based on topic
        if "space" in topic.lower():
            searches = ["space galaxy", "nebula stars", "telescope astronomy", "cosmic universe"]
        elif "productivity" in topic.lower():
            searches = ["business workspace", "success planning", "office productivity", "goals achievement"]
        elif "animal" in topic.lower():
            searches = ["wildlife nature", "animals forest", "ocean marine life", "birds flying"]
        else:
            searches = ["technology modern", "science laboratory", "innovation digital", "future progress"]
        
        image_paths = []
        for i, search in enumerate(searches):
            img_path = self.download_pexels_image(search, i)
            image_paths.append(img_path)
        
        logger.info(f"Generated {len(image_paths)} real images")
        return image_paths
    
    def generate_real_audio(self, script: str) -> str:
        """Generate real voice narration"""
        logger.info("Generating voice...")
        
        audio_path = self.audio_dir / f"voice_{int(time.time())}.mp3"
        
        # Try Google TTS (best quality)
        if gTTS:
            try:
                # Clean script for TTS
                clean_script = script.replace('\n', ' ').strip()
                tts = gTTS(text=clean_script, lang='en', slow=False)
                tts.save(str(audio_path))
                logger.info("Generated Google TTS voice")
                return str(audio_path)
            except Exception as e:
                logger.warning(f"Google TTS failed: {e}")
        
        # Try Windows TTS
        if pyttsx3:
            try:
                engine = pyttsx3.init()
                voices = engine.getProperty('voices')
                if voices and len(voices) > 1:
                    engine.setProperty('voice', voices[1].id)  # Often female voice
                engine.setProperty('rate', 150)
                engine.setProperty('volume', 0.9)
                
                wav_path = str(audio_path).replace('.mp3', '.wav')
                engine.save_to_file(script, wav_path)
                engine.runAndWait()
                
                if os.path.exists(wav_path):
                    logger.info("Generated Windows TTS voice")
                    return wav_path
                    
            except Exception as e:
                logger.warning(f"Windows TTS failed: {e}")
        
        # Create silence as fallback
        return None
    
    def create_video_with_ffmpeg(self, images: list, audio_path: str, title: str) -> str:
        """Create video using FFmpeg directly"""
        logger.info("Creating video with FFmpeg...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"real_video_{timestamp}.mp4"
        
        # Calculate timing
        if audio_path and os.path.exists(audio_path):
            # Get audio duration using ffprobe
            try:
                result = subprocess.run([
                    'ffprobe', '-v', 'quiet', '-print_format', 'json', 
                    '-show_format', audio_path
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    info = json.loads(result.stdout)
                    audio_duration = float(info['format']['duration'])
                else:
                    audio_duration = 120  # Default 2 minutes
            except:
                audio_duration = 120
        else:
            audio_duration = 120
        
        # Time per image
        time_per_image = audio_duration / len(images)
        
        # Create input file list for FFmpeg
        input_file = self.output_dir / "input_list.txt"
        with open(input_file, 'w') as f:
            for img_path in images:
                f.write(f"file '{os.path.abspath(img_path)}'\n")
                f.write(f"duration {time_per_image}\n")
            # Add last image again to fix FFmpeg requirement
            f.write(f"file '{os.path.abspath(images[-1])}'\n")
        
        # Build FFmpeg command
        cmd = [
            'ffmpeg', '-y',  # Overwrite output
            '-f', 'concat',
            '-safe', '0',
            '-i', str(input_file),
            '-vf', f'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=25',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p'
        ]
        
        # Add audio if available
        if audio_path and os.path.exists(audio_path):
            cmd.extend(['-i', audio_path, '-c:a', 'aac', '-shortest'])
        else:
            # Add silent audio
            cmd.extend(['-f', 'lavfi', '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100:duration={audio_duration}', '-c:a', 'aac'])
        
        cmd.append(str(output_path))
        
        # Run FFmpeg
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Video created successfully: {output_path}")
                return str(output_path)
            else:
                logger.error(f"FFmpeg error: {result.stderr}")
                return None
        except Exception as e:
            logger.error(f"FFmpeg execution failed: {e}")
            return None
        finally:
            # Clean up
            if input_file.exists():
                input_file.unlink()
    
    def upload_to_youtube(self, video_path: str, title: str) -> str:
        """Upload to YouTube"""
        try:
            from googleapiclient.discovery import build
            from google.oauth2.credentials import Credentials
            from googleapiclient.http import MediaFileUpload
            import pickle
            
            if not os.path.exists('token.pickle'):
                logger.error("No YouTube authentication found")
                return None
            
            with open('token.pickle', 'rb') as f:
                creds = pickle.load(f)
            
            youtube = build('youtube', 'v3', credentials=creds)
            
            body = {
                'snippet': {
                    'title': f'AutoMagic: {title}',
                    'description': f'An engaging video about {title}, created by AutoMagic AI.',
                    'tags': ['automagic', 'ai', 'educational', 'trending'],
                    'categoryId': '22'  # People & Blogs
                },
                'status': {
                    'privacyStatus': 'public'
                }
            }
            
            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
            request = youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )
            
            response = request.execute()
            video_id = response['id']
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Log the upload
            with open('uploaded_videos.log', 'a', encoding='utf-8') as f:
                f.write(f"{title[:50]}\\n")
            
            logger.info(f"YouTube upload successful: {youtube_url}")
            return youtube_url
            
        except Exception as e:
            logger.error(f"YouTube upload failed: {e}")
            return None
    
    def create_complete_real_video(self):
        """Main function to create a complete, engaging video"""
        try:
            logger.info("=" * 60)
            logger.info("🎬 CREATING REAL ENGAGING VIDEO")
            logger.info("=" * 60)
            
            # Get topic
            topic = self.get_trending_topic()
            logger.info(f"📺 Topic: {topic}")
            
            # Generate script
            script = self.generate_engaging_script(topic)
            logger.info(f"📝 Script: {len(script)} characters")
            
            # Generate real images
            images = self.generate_real_images(topic)
            logger.info(f"🖼️  Images: {len(images)} generated")
            
            # Generate voice
            audio_path = self.generate_real_audio(script)
            if audio_path:
                logger.info(f"🎤 Voice: Generated")
            else:
                logger.info(f"🎤 Voice: Using silent audio")
            
            # Create video
            video_path = self.create_video_with_ffmpeg(images, audio_path, topic)
            if not video_path:
                logger.error("Video creation failed")
                return False
            
            # Upload to YouTube
            youtube_url = self.upload_to_youtube(video_path, topic)
            
            if youtube_url:
                logger.info(f"🎉 SUCCESS! Video uploaded: {youtube_url}")
            else:
                logger.info(f"✅ Video ready: {video_path}")
            
            logger.info("=" * 60)
            logger.info("✅ REAL VIDEO CREATION COMPLETE!")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"Video creation failed: {e}")
            return False

if __name__ == "__main__":
    generator = SimpleRealVideoGenerator()
    success = generator.create_complete_real_video()
    
    if success:
        print("\\n🎉 Real video created successfully!")
    else:
        print("\\n❌ Video creation failed.")