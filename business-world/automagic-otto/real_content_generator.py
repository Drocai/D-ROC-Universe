#!/usr/bin/env python3
"""
Real Content Generator - Creates actual quality videos with images, sound, and proper length
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path
import random
import requests

# Image generation
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

# Audio generation
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    print("gTTS not available, will use fallback audio")

from dotenv import load_dotenv
load_dotenv()

class RealContentGenerator:
    def __init__(self):
        self.images_dir = Path("generated_images")
        self.audio_dir = Path("generated_audio")
        self.videos_dir = Path("final_videos")
        
        # Create directories
        for d in [self.images_dir, self.audio_dir, self.videos_dir]:
            d.mkdir(exist_ok=True)
    
    def get_trending_topic(self):
        """Get a real trending topic"""
        try:
            # Try to get from Reddit
            response = requests.get('https://www.reddit.com/r/popular.json', 
                                   headers={'User-Agent': 'AutoMagic'}, 
                                   timeout=5)
            if response.status_code == 200:
                posts = response.json()['data']['children']
                # Get a clean topic
                for post in posts[:10]:
                    title = post['data']['title']
                    if len(title) < 100 and not any(bad in title.lower() for bad in ['nsfw', 'porn', 'sex']):
                        return title[:80]
        except:
            pass
        
        # Fallback topics
        topics = [
            "Amazing Space Discoveries That Changed Everything",
            "Mind-Blowing Technology That's Coming in 2025",
            "Incredible Animal Behaviors Scientists Just Discovered",
            "Secret Life Hacks That Actually Work",
            "Unbelievable Facts About The Human Brain"
        ]
        return random.choice(topics)
    
    def generate_script(self, topic):
        """Generate a real 2-3 minute script"""
        
        # Try OpenAI first if available
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and not openai_key.startswith("YOUR_"):
            try:
                import openai
                client = openai.OpenAI(api_key=openai_key)
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{
                        "role": "system", 
                        "content": "You are a YouTube script writer. Create engaging 2-minute scripts."
                    }, {
                        "role": "user",
                        "content": f"Write a 2-minute YouTube video script about: {topic}. Include an introduction, 3 main points, and conclusion. Make it engaging and informative."
                    }],
                    max_tokens=500
                )
                
                script = response.choices[0].message.content
                print("[OK] Generated script with OpenAI")
                return script
                
            except Exception as e:
                print(f"[INFO] OpenAI unavailable: {e}")
        
        # Fallback: Generate structured script
        script = f"""
Welcome to today's video about {topic}!

{topic} is one of the most fascinating subjects we've discovered recently. Scientists and researchers have been amazed by what they've found.

First, let's talk about why this matters. This discovery changes everything we thought we knew. The implications are absolutely mind-blowing when you really think about it.

The most interesting part is how this affects our daily lives. You might not realize it, but this impacts you more than you think. Every single day, millions of people are affected by this without even knowing it.

Here's what the experts are saying. Leading researchers have confirmed that this is a game-changer. The data shows incredible results that nobody expected.

But here's the real secret that most people don't know. This information could completely transform how we understand the world. Once you know this, you'll never look at things the same way again.

What does this mean for the future? The possibilities are endless. We're just scratching the surface of what's possible.

In conclusion, {topic} represents a major breakthrough in our understanding. The next few years are going to be absolutely incredible as we learn more.

Thanks for watching! Don't forget to subscribe for more amazing content like this. See you in the next video!
"""
        
        print("[OK] Generated fallback script")
        return script
    
    def create_quality_images(self, topic, script):
        """Create actual quality images"""
        print("Creating quality images...")
        
        images = []
        
        # Split script into sections for different images
        script_parts = script.split('\n\n')[:4]  # Get 4 sections
        
        for i in range(4):
            # Create a high-quality image
            width, height = 1920, 1080
            
            # Professional color schemes
            schemes = [
                [(25, 42, 86), (89, 139, 176), (142, 202, 230)],    # Blue gradient
                [(86, 25, 70), (150, 88, 138), (203, 153, 190)],    # Purple gradient
                [(31, 64, 55), (77, 128, 106), (153, 217, 140)],    # Green gradient
                [(64, 29, 33), (142, 68, 75), (217, 153, 120)]      # Warm gradient
            ]
            
            colors = schemes[i % len(schemes)]
            
            # Create base image
            img = Image.new('RGB', (width, height), colors[0])
            
            # Create gradient background
            for y in range(height):
                # Calculate gradient
                ratio = y / height
                
                if ratio < 0.5:
                    # Top half gradient
                    t = ratio * 2
                    r = int(colors[0][0] * (1-t) + colors[1][0] * t)
                    g = int(colors[0][1] * (1-t) + colors[1][1] * t)
                    b = int(colors[0][2] * (1-t) + colors[1][2] * t)
                else:
                    # Bottom half gradient
                    t = (ratio - 0.5) * 2
                    r = int(colors[1][0] * (1-t) + colors[2][0] * t)
                    g = int(colors[1][1] * (1-t) + colors[2][1] * t)
                    b = int(colors[1][2] * (1-t) + colors[2][2] * t)
                
                # Add some noise for texture
                r = max(0, min(255, r + random.randint(-10, 10)))
                g = max(0, min(255, g + random.randint(-10, 10)))
                b = max(0, min(255, b + random.randint(-10, 10)))
                
                for x in range(width):
                    img.putpixel((x, y), (r, g, b))
            
            # Add visual elements
            draw = ImageDraw.Draw(img)
            
            # Add geometric shapes
            for _ in range(8):
                x1 = random.randint(0, width)
                y1 = random.randint(0, height)
                size = random.randint(100, 400)
                
                # Semi-transparent overlay
                overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                
                # Random shapes with transparency
                color = (random.randint(100, 255), random.randint(100, 255), 
                        random.randint(100, 255), 40)
                
                if random.choice([True, False]):
                    overlay_draw.ellipse([x1, y1, x1+size, y1+size], fill=color)
                else:
                    overlay_draw.rectangle([x1, y1, x1+size, y1+size//2], fill=color)
                
                img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
            
            # Add text overlay
            draw = ImageDraw.Draw(img)
            
            # Main title
            try:
                font_large = ImageFont.truetype("arial.ttf", 120)
                font_small = ImageFont.truetype("arial.ttf", 60)
            except:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Extract key phrase from topic
            if len(topic) > 40:
                main_text = topic[:40] + "..."
            else:
                main_text = topic
            
            # Calculate text position
            bbox = draw.textbbox((0, 0), main_text, font=font_large)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (width - text_width) // 2
            y = height // 3
            
            # Draw text with shadow
            for offset in range(1, 8):
                draw.text((x + offset, y + offset), main_text, 
                         font=font_large, fill=(0, 0, 0, 180))
            
            draw.text((x, y), main_text, font=font_large, fill=(255, 255, 255))
            
            # Add part number
            part_text = f"Part {i+1} of 4"
            part_bbox = draw.textbbox((0, 0), part_text, font=font_small)
            part_width = part_bbox[2] - part_bbox[0]
            
            part_x = (width - part_width) // 2
            part_y = y + text_height + 50
            
            draw.text((part_x + 3, part_y + 3), part_text, 
                     font=font_small, fill=(0, 0, 0))
            draw.text((part_x, part_y), part_text, 
                     font=font_small, fill=(220, 220, 220))
            
            # Save image
            timestamp = int(time.time() * 1000)
            filename = f"quality_image_{i+1}_{timestamp}.jpg"
            filepath = self.images_dir / filename
            img.save(filepath, quality=95)
            images.append(str(filepath))
            
            print(f"  Created image {i+1}: {filename}")
        
        return images
    
    def generate_voice_audio(self, script):
        """Generate real voice narration"""
        print("Generating voice narration...")
        
        timestamp = int(time.time())
        audio_path = self.audio_dir / f"narration_{timestamp}.mp3"
        
        # Try Google TTS (reliable and free)
        if GTTS_AVAILABLE:
            try:
                # Clean the script
                clean_script = script.replace('\n', ' ').strip()
                
                # Generate audio
                tts = gTTS(text=clean_script, lang='en', slow=False)
                tts.save(str(audio_path))
                
                print(f"  [OK] Generated voice with Google TTS")
                return str(audio_path)
                
            except Exception as e:
                print(f"  [ERROR] TTS failed: {e}")
        
        # Fallback: Create silent audio
        print("  Creating fallback audio...")
        
        # Calculate duration based on script (roughly 150 words per minute)
        word_count = len(script.split())
        duration = max(60, (word_count / 150) * 60)  # At least 1 minute
        
        # Create silent audio with FFmpeg
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100',
            '-t', str(duration),
            '-c:a', 'mp3',
            str(audio_path)
        ]
        
        subprocess.run(cmd, capture_output=True)
        print(f"  [OK] Created {duration:.0f}s audio track")
        return str(audio_path)
    
    def create_video(self, images, audio_path, topic):
        """Create the final video with proper length"""
        print("Creating video...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.videos_dir / f"automagic_real_{timestamp}.mp4"
        
        # Get audio duration
        probe_cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', 
                    '-show_format', audio_path]
        result = subprocess.run(probe_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            info = json.loads(result.stdout)
            audio_duration = float(info['format']['duration'])
        else:
            audio_duration = 120  # Default 2 minutes
        
        print(f"  Audio duration: {audio_duration:.1f}s")
        
        # Calculate time per image
        time_per_image = audio_duration / len(images)
        print(f"  Time per image: {time_per_image:.1f}s")
        
        # Create input file for concat
        input_list = self.videos_dir / f"input_{timestamp}.txt"
        with open(input_list, 'w') as f:
            for img in images:
                f.write(f"file '{os.path.abspath(img)}'\n")
                f.write(f"duration {time_per_image}\n")
            # Last image without duration
            f.write(f"file '{os.path.abspath(images[-1])}'\n")
        
        # Create video with FFmpeg
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat', '-safe', '0', '-i', str(input_list),
            '-i', audio_path,
            '-vf', 'scale=1920:1080,fps=30',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
            '-c:a', 'aac', '-b:a', '192k',
            '-pix_fmt', 'yuv420p',
            '-shortest',
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Check final video
            file_size = os.path.getsize(output_path) / (1024 * 1024)
            print(f"  [OK] Video created: {output_path.name}")
            print(f"  Size: {file_size:.1f} MB")
            
            # Clean up
            input_list.unlink()
            
            return str(output_path)
        else:
            print(f"  [ERROR] Video creation failed: {result.stderr}")
            return None
    
    def upload_to_youtube(self, video_path, topic):
        """Upload to YouTube"""
        print("Uploading to YouTube...")
        
        try:
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            import pickle
            
            with open('token.pickle', 'rb') as f:
                creds = pickle.load(f)
            
            youtube = build('youtube', 'v3', credentials=creds)
            
            body = {
                'snippet': {
                    'title': f'AutoMagic: {topic[:80]}',
                    'description': f'''🤖 Automatically generated video about {topic}

This video was created by AutoMagic AI system, bringing you the latest trending topics and amazing discoveries.

🔔 Subscribe for daily AI-generated content
👍 Like if you found this interesting
💬 Comment your thoughts below

#AutoMagic #AI #Trending #Technology #Education''',
                    'tags': ['automagic', 'ai', 'trending', 'education', 'technology'],
                    'categoryId': '28'  # Science & Technology
                },
                'status': {
                    'privacyStatus': 'public',
                    'embeddable': True,
                    'madeForKids': False
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
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            print(f"  [OK] Upload successful!")
            print(f"  Video ID: {video_id}")
            print(f"  URL: {video_url}")
            
            # Log the upload
            with open('uploaded_videos.log', 'a', encoding='utf-8') as f:
                f.write(f"AutoMagic: {topic[:80]} - {datetime.now()}\\n")
            
            return video_url
            
        except Exception as e:
            print(f"  [ERROR] Upload failed: {e}")
            return None
    
    def create_complete_video(self):
        """Main function to create a complete video"""
        print("=" * 60)
        print("AUTOMAGIC REAL CONTENT GENERATOR")
        print("=" * 60)
        
        # Get trending topic
        topic = self.get_trending_topic()
        print(f"Topic: {topic}")
        
        # Generate script
        script = self.generate_script(topic)
        print(f"Script: {len(script)} characters")
        
        # Create images
        images = self.create_quality_images(topic, script)
        print(f"Images: {len(images)} created")
        
        # Generate audio
        audio_path = self.generate_voice_audio(script)
        print(f"Audio: Generated")
        
        # Create video
        video_path = self.create_video(images, audio_path, topic)
        
        if not video_path:
            print("[ERROR] Video creation failed")
            return False
        
        # Upload to YouTube
        youtube_url = self.upload_to_youtube(video_path, topic)
        
        print()
        print("=" * 60)
        if youtube_url:
            print("[SUCCESS] Video created and uploaded!")
            print(f"Watch at: {youtube_url}")
        else:
            print("[SUCCESS] Video created!")
            print(f"Local file: {video_path}")
        print("=" * 60)
        
        return True

if __name__ == "__main__":
    generator = RealContentGenerator()
    generator.create_complete_video()