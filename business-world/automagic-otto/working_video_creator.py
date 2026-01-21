#!/usr/bin/env python3
"""
Working Video Creator - Actually creates proper videos
"""

import os
import sys
import logging
import requests
import json
from datetime import datetime
from pathlib import Path
import random
import time
import subprocess

# Core dependencies
from PIL import Image, ImageDraw, ImageFont
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

class WorkingVideoCreator:
    def __init__(self):
        self.output_dir = Path("final_videos")
        self.output_dir.mkdir(exist_ok=True)
        
        self.images_dir = Path("generated_images")
        self.images_dir.mkdir(exist_ok=True)
        
        self.audio_dir = Path("generated_audio") 
        self.audio_dir.mkdir(exist_ok=True)
        
    def get_topic(self) -> str:
        """Get engaging topic"""
        topics = [
            "Mind-blowing space discoveries that changed everything",
            "Secret productivity hacks billionaires use daily", 
            "Amazing animal behaviors scientists just discovered",
            "Life-changing psychology tricks that actually work",
            "Revolutionary technology changing the world right now"
        ]
        return random.choice(topics)
    
    def create_script(self, topic: str) -> str:
        """Create engaging script content"""
        
        if "space" in topic.lower():
            return """
The universe just revealed something incredible that's changing everything we know about space.

Scientists using the James Webb Space Telescope discovered galaxies that shouldn't exist. These cosmic giants formed just 400 million years after the Big Bang, when the universe was practically a baby.

But here's the mind-blowing part - these galaxies are massive, way bigger than our models predicted. It's like finding a fully grown forest in what should be empty space.

We also found water vapor on an exoplanet 120 light-years away. This world might have clouds, rain, and possibly even life swimming in alien oceans.

Every new discovery is rewriting the textbooks. The universe is far stranger and more incredible than we ever imagined possible.
"""
        
        elif "productivity" in topic.lower():
            return """
Billionaires use these three simple tricks to accomplish more before 9 AM than most people do all week.

First - the two-minute rule. If something takes less than two minutes, they do it immediately. No exceptions. This prevents small tasks from becoming overwhelming mountains.

Second - time blocking instead of to-do lists. Every minute is scheduled for a specific purpose. Their calendar is like a fortress where nothing gets in without permission.

The secret weapon is the 80-20 rule. They identify the 20 percent of activities that produce 80 percent of results, then ruthlessly eliminate everything else.

Start with just one of these habits today and watch your productivity explode beyond what you thought was possible.
"""
        
        else:
            return f"""
There's something about {topic} that most people completely miss, and once you understand it, everything changes forever.

Scientists have been studying this for years, and what they discovered challenges everything we thought we knew. The research results are absolutely mind-blowing.

Here's what's incredible - tiny changes in this area can have massive impacts. We're talking about simple adjustments that transform your entire perspective.

The experts found patterns that nobody expected. These discoveries are opening up possibilities we never imagined were even remotely possible.

The best part? You can start applying this knowledge right now. The tools are available today, and the results will absolutely surprise you.
"""
    
    def create_real_images(self, topic: str) -> list:
        """Create high-quality visual images"""
        logger.info("Creating high-quality images...")
        
        # Define visual themes
        if "space" in topic.lower():
            themes = [
                ("Deep Space Discovery", [(10, 20, 40), (30, 60, 120), (60, 100, 180)]),
                ("Cosmic Telescope", [(40, 20, 60), (80, 40, 120), (120, 80, 200)]),
                ("Galaxy Formation", [(20, 10, 50), (50, 30, 100), (100, 60, 180)]),
                ("Alien Worlds", [(0, 40, 80), (20, 80, 140), (40, 120, 200)])
            ]
        elif "productivity" in topic.lower():
            themes = [
                ("Success Mindset", [(40, 60, 100), (80, 120, 160), (120, 180, 220)]),
                ("Peak Performance", [(60, 80, 40), (120, 160, 80), (180, 220, 120)]),
                ("Time Mastery", [(80, 40, 60), (140, 80, 120), (200, 120, 180)]),
                ("Goal Achievement", [(100, 60, 20), (180, 120, 60), (220, 180, 120)])
            ]
        else:
            themes = [
                ("Innovation", [(20, 60, 100), (60, 120, 180), (100, 180, 240)]),
                ("Discovery", [(60, 20, 80), (120, 60, 140), (180, 100, 200)]),
                ("Technology", [(40, 80, 60), (80, 140, 120), (120, 200, 180)]),
                ("Future", [(80, 60, 40), (140, 120, 80), (200, 180, 120)])
            ]
        
        image_paths = []
        
        for i, (title, colors) in enumerate(themes):
            img_path = self.create_visual_image(title, colors, i + 1)
            image_paths.append(img_path)
        
        logger.info(f"Created {len(image_paths)} high-quality images")
        return image_paths
    
    def create_visual_image(self, title: str, colors: list, part_num: int) -> str:
        """Create a visually stunning image"""
        width, height = 1920, 1080
        
        # Create base with complex gradient
        img = Image.new('RGB', (width, height), colors[0])
        
        # Create multi-layer gradient
        for y in range(height):
            for x in range(width):
                # Calculate position ratios
                x_ratio = x / width
                y_ratio = y / height
                
                # Complex color mixing
                if y_ratio < 0.3:
                    ratio = y_ratio / 0.3
                    r = int(colors[0][0] * (1-ratio) + colors[1][0] * ratio)
                    g = int(colors[0][1] * (1-ratio) + colors[1][1] * ratio)
                    b = int(colors[0][2] * (1-ratio) + colors[1][2] * ratio)
                elif y_ratio < 0.7:
                    ratio = (y_ratio - 0.3) / 0.4
                    r = int(colors[1][0] * (1-ratio) + colors[2][0] * ratio)
                    g = int(colors[1][1] * (1-ratio) + colors[2][1] * ratio)
                    b = int(colors[1][2] * (1-ratio) + colors[2][2] * ratio)
                else:
                    ratio = (y_ratio - 0.7) / 0.3
                    r = int(colors[2][0] * (1-ratio) + colors[0][0] * ratio)
                    g = int(colors[2][1] * (1-ratio) + colors[0][1] * ratio)
                    b = int(colors[2][2] * (1-ratio) + colors[0][2] * ratio)
                
                # Add subtle variation
                r = max(0, min(255, r + random.randint(-10, 10)))
                g = max(0, min(255, g + random.randint(-10, 10)))
                b = max(0, min(255, b + random.randint(-10, 10)))
                
                img.putpixel((x, y), (r, g, b))
        
        # Add visual elements
        draw = ImageDraw.Draw(img)
        
        # Add abstract shapes
        for _ in range(8):
            x1 = random.randint(0, width//2)
            y1 = random.randint(0, height//2)
            x2 = x1 + random.randint(300, 600)
            y2 = y1 + random.randint(200, 400)
            
            # Create overlay for transparency
            overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            
            # Random shape
            if random.choice([True, False]):
                # Rectangle
                overlay_draw.rectangle([x1, y1, x2, y2], 
                                     fill=(random.randint(100, 255), 
                                          random.randint(100, 255), 
                                          random.randint(100, 255), 40))
            else:
                # Circle
                overlay_draw.ellipse([x1, y1, x2, y2], 
                                   fill=(random.randint(100, 255), 
                                        random.randint(100, 255), 
                                        random.randint(100, 255), 40))
            
            img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        
        # Add professional text
        try:
            font_large = ImageFont.truetype("arial.ttf", 120)
            font_small = ImageFont.truetype("arial.ttf", 60)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Main title
        main_text = title
        text_bbox = draw.textbbox((0, 0), main_text, font=font_large)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (width - text_width) // 2
        y = height // 3
        
        # Text shadow
        for offset in range(1, 6):
            draw.text((x + offset, y + offset), main_text, font=font_large, 
                     fill=(0, 0, 0, 150))
        
        # Main text
        draw.text((x, y), main_text, font=font_large, fill=(255, 255, 255))
        
        # Part number
        part_text = f"Part {part_num}"
        part_bbox = draw.textbbox((0, 0), part_text, font=font_small)
        part_width = part_bbox[2] - part_bbox[0]
        
        part_x = (width - part_width) // 2
        part_y = y + text_height + 40
        
        # Part text shadow
        for offset in range(1, 4):
            draw.text((part_x + offset, part_y + offset), part_text, font=font_small, 
                     fill=(0, 0, 0, 120))
        
        # Part text
        draw.text((part_x, part_y), part_text, font=font_small, fill=(200, 200, 200))
        
        # Save image
        timestamp = int(time.time())
        filename = f"quality_image_{part_num}_{timestamp}.jpg"
        filepath = self.images_dir / filename
        img.save(filepath, quality=95)
        
        return str(filepath)
    
    def create_voice_audio(self, script: str) -> str:
        """Create voice narration"""
        logger.info("Creating voice narration...")
        
        timestamp = int(time.time())
        audio_path = self.audio_dir / f"narration_{timestamp}.mp3"
        
        # Try Google TTS first
        if gTTS:
            try:
                clean_script = script.replace('\\n', ' ').strip()
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
                
                # Find best voice
                if voices:
                    for voice in voices:
                        if any(word in voice.name.lower() for word in ['zira', 'hazel', 'female']):
                            engine.setProperty('voice', voice.id)
                            break
                
                engine.setProperty('rate', 160)  # Natural pace
                engine.setProperty('volume', 0.9)
                
                wav_path = str(audio_path).replace('.mp3', '.wav')
                engine.save_to_file(script, wav_path)
                engine.runAndWait()
                
                if os.path.exists(wav_path):
                    logger.info("Generated Windows TTS voice")
                    return wav_path
                    
            except Exception as e:
                logger.warning(f"Windows TTS failed: {e}")
        
        return None
    
    def create_video_ffmpeg(self, images: list, audio_path: str, title: str) -> str:
        """Create video using FFmpeg with correct syntax"""
        logger.info("Creating video with FFmpeg...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"quality_video_{timestamp}.mp4"
        
        # Calculate timing
        if audio_path and os.path.exists(audio_path):
            try:
                # Get audio duration
                result = subprocess.run([
                    'ffprobe', '-v', 'quiet', '-print_format', 'json', 
                    '-show_format', audio_path
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    info = json.loads(result.stdout)
                    audio_duration = float(info['format']['duration'])
                else:
                    audio_duration = 90  # Default
            except:
                audio_duration = 90
        else:
            audio_duration = 90
        
        # Time per image
        time_per_image = audio_duration / len(images)
        
        # Create input list
        input_list = self.output_dir / f"input_{timestamp}.txt"
        with open(input_list, 'w') as f:
            for i, img_path in enumerate(images):
                f.write(f"file '{os.path.abspath(img_path)}'\\n")
                f.write(f"duration {time_per_image}\\n")
            # FFmpeg requires last image without duration
            f.write(f"file '{os.path.abspath(images[-1])}'\\n")
        
        # Build FFmpeg command correctly
        if audio_path and os.path.exists(audio_path):
            # With audio
            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat', '-safe', '0', '-i', str(input_list),
                '-i', audio_path,
                '-vf', 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=25',
                '-c:v', 'libx264', '-c:a', 'aac',
                '-pix_fmt', 'yuv420p',
                '-shortest',
                str(output_path)
            ]
        else:
            # Without audio (add silent track)
            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat', '-safe', '0', '-i', str(input_list),
                '-f', 'lavfi', '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100',
                '-vf', 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=25',
                '-c:v', 'libx264', '-c:a', 'aac',
                '-pix_fmt', 'yuv420p',
                '-t', str(audio_duration),
                str(output_path)
            ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Video created: {output_path}")
                return str(output_path)
            else:
                logger.error(f"FFmpeg failed: {result.stderr}")
                return None
        except Exception as e:
            logger.error(f"FFmpeg error: {e}")
            return None
        finally:
            # Cleanup
            if input_list.exists():
                input_list.unlink()
    
    def upload_youtube(self, video_path: str, title: str) -> str:
        """Upload to YouTube"""
        try:
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            import pickle
            
            if not os.path.exists('token.pickle'):
                logger.error("No YouTube auth")
                return None
            
            with open('token.pickle', 'rb') as f:
                creds = pickle.load(f)
            
            youtube = build('youtube', 'v3', credentials=creds)
            
            body = {
                'snippet': {
                    'title': f'AutoMagic: {title[:50]}',
                    'description': f'An engaging video about {title}',
                    'tags': ['automagic', 'educational', 'trending'],
                    'categoryId': '22'
                },
                'status': {'privacyStatus': 'public'}
            }
            
            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
            request = youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )
            
            response = request.execute()
            video_id = response['id']
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Log upload
            with open('uploaded_videos.log', 'a', encoding='utf-8') as f:
                f.write(f"{title[:50]}\\n")
            
            logger.info(f"Uploaded: {url}")
            return url
            
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return None
    
    def create_quality_video(self):
        """Main function - create high quality video"""
        try:
            logger.info("=" * 50)
            logger.info("Creating Quality Video")
            logger.info("=" * 50)
            
            # Get topic
            topic = self.get_topic()
            logger.info(f"Topic: {topic}")
            
            # Create script
            script = self.create_script(topic)
            logger.info(f"Script: {len(script)} chars")
            
            # Create images
            images = self.create_real_images(topic)
            logger.info(f"Images: {len(images)} created")
            
            # Create voice
            audio_path = self.create_voice_audio(script)
            if audio_path:
                logger.info("Voice: Generated")
            else:
                logger.info("Voice: Silent mode")
            
            # Create video
            video_path = self.create_video_ffmpeg(images, audio_path, topic)
            if not video_path:
                return False
            
            # Upload
            youtube_url = self.upload_youtube(video_path, topic)
            
            if youtube_url:
                print(f"SUCCESS! Video uploaded: {youtube_url}")
            else:
                print(f"Video ready: {video_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed: {e}")
            return False

if __name__ == "__main__":
    creator = WorkingVideoCreator()
    success = creator.create_quality_video()
    
    if not success:
        print("Video creation failed")