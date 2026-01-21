#!/usr/bin/env python3
"""
Simple Working AutoMagic - Creates actual quality videos
"""

import os
import sys
import logging
import json
from datetime import datetime
from pathlib import Path
import random
import time

from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleWorkingAutoMagic:
    def __init__(self):
        # Setup directories
        for dir_name in ['final_videos', 'generated_images', 'generated_audio', 'logs']:
            Path(dir_name).mkdir(exist_ok=True)
    
    def get_trending_topic(self):
        """Get engaging topic"""
        topics = [
            "Mind-Blowing Space Discoveries That Changed Everything",
            "Secret Psychology Tricks That Actually Work",
            "Amazing Scientific Breakthroughs Happening Right Now", 
            "Incredible Animal Behaviors Scientists Just Discovered",
            "Revolutionary Technology Changing The World"
        ]
        return random.choice(topics)
    
    def generate_script(self, topic):
        """Generate engaging script"""
        
        scripts = {
            "space": """
# Video Title: Mind-Blowing Space Discoveries That Changed Everything

## Introduction
The universe just revealed some of its biggest secrets, and what scientists discovered will absolutely blow your mind.

## Main Point 1: Impossible Galaxies
The James Webb Space Telescope found galaxies that shouldn't exist. These cosmic giants formed just 400 million years after the Big Bang - that's like finding a fully grown forest where only seedlings should be.

## Main Point 2: Water on Alien Worlds  
We discovered water vapor on an exoplanet called K2-18b, located 120 light-years away. This world might have clouds, rain, and possibly even alien oceans teeming with life.

## Main Point 3: Dark Matter Mystery
New research suggests dark matter interacts with regular matter in ways we never imagined. This could explain why galaxies spin the way they do and why the universe is expanding faster than it should.

## Conclusion
Every new discovery is rewriting the textbooks. The universe is far stranger and more incredible than we ever thought possible. What we'll find next could change everything we know about reality itself.
""",
            
            "psychology": """
# Video Title: Secret Psychology Tricks That Actually Work

## Introduction
What if I told you that understanding these psychology tricks could completely change how people respond to you? These aren't theory - they're proven techniques that work.

## Main Point 1: The Two-Minute Rule
If something takes less than two minutes, do it immediately. This simple rule prevents small tasks from becoming overwhelming mountains and makes you appear incredibly organized.

## Main Point 2: Mirror Body Language
Subtly copying someone's posture and gestures makes them feel more comfortable around you. It's called mirroring, and it works because our brains are wired to trust people who are similar to us.

## Main Point 3: The Power of Pausing
When someone asks you a question, pause for two seconds before answering. This makes you appear more thoughtful and confident, and your answers carry more weight.

## Conclusion
These tricks work because they tap into fundamental aspects of human psychology. Start using just one of these today, and watch how differently people respond to you.
""",
            
            "default": f"""
# Video Title: {topic}

## Introduction
There's something incredible about {topic} that most people completely miss, and once you understand it, everything changes.

## Main Point 1: Hidden Discoveries
Scientists have been researching this for years, and what they found challenges everything we thought we knew. The results are absolutely mind-blowing.

## Main Point 2: Surprising Impacts
Here's what's incredible - small changes in this area can have massive effects. We're talking about simple adjustments that transform your entire perspective.

## Main Point 3: Breakthrough Findings
The experts discovered patterns that nobody expected. These findings are opening up possibilities we never imagined were even remotely possible.

## Conclusion
The best part? You can start applying this knowledge right now. The tools are available today, and the results will absolutely surprise you.
"""
        }
        
        if "space" in topic.lower():
            return scripts["space"]
        elif "psychology" in topic.lower() or "trick" in topic.lower():
            return scripts["psychology"]
        else:
            return scripts["default"]
    
    def create_quality_images(self, script):
        """Create high-quality images based on script"""
        logger.info("Creating quality images...")
        
        # Extract main points from script
        lines = script.split('\\n')
        main_points = []
        for line in lines:
            if line.startswith("## Main Point"):
                point = line.replace("## Main Point", "").strip()
                if ":" in point:
                    point = point.split(":", 1)[1].strip()
                main_points.append(point)
        
        if not main_points:
            main_points = ["Introduction", "Key Discovery", "Amazing Results", "Conclusion"]
        
        # Professional color schemes
        color_schemes = [
            [(20, 30, 60), (40, 70, 120), (80, 120, 180)],    # Deep blue
            [(60, 20, 80), (120, 40, 140), (180, 80, 200)],   # Purple
            [(80, 40, 20), (140, 80, 40), (200, 140, 80)],    # Orange
            [(20, 80, 40), (40, 140, 80), (80, 200, 140)]     # Green
        ]
        
        images = []
        
        for i, point in enumerate(main_points[:4]):
            # Create high-quality image
            width, height = 1920, 1080
            colors = color_schemes[i % len(color_schemes)]
            
            # Create base image with gradient
            img = Image.new('RGB', (width, height), colors[0])
            
            # Create sophisticated gradient
            for y in range(height):
                for x in range(width):
                    # Calculate position ratios
                    x_ratio = x / width
                    y_ratio = y / height
                    
                    # Multi-layer gradient calculation
                    if y_ratio < 0.4:
                        ratio = y_ratio / 0.4
                        r = int(colors[0][0] * (1-ratio) + colors[1][0] * ratio)
                        g = int(colors[0][1] * (1-ratio) + colors[1][1] * ratio)
                        b = int(colors[0][2] * (1-ratio) + colors[1][2] * ratio)
                    else:
                        ratio = (y_ratio - 0.4) / 0.6
                        r = int(colors[1][0] * (1-ratio) + colors[2][0] * ratio)
                        g = int(colors[1][1] * (1-ratio) + colors[2][1] * ratio)
                        b = int(colors[1][2] * (1-ratio) + colors[2][2] * ratio)
                    
                    # Add subtle noise for texture
                    r = max(0, min(255, r + random.randint(-5, 5)))
                    g = max(0, min(255, g + random.randint(-5, 5)))
                    b = max(0, min(255, b + random.randint(-5, 5)))
                    
                    img.putpixel((x, y), (r, g, b))
            
            # Add visual elements
            draw = ImageDraw.Draw(img)
            
            # Add geometric shapes for visual interest
            for _ in range(6):
                x1 = random.randint(0, width//2)
                y1 = random.randint(0, height//2)
                x2 = x1 + random.randint(200, 500)
                y2 = y1 + random.randint(150, 350)
                
                # Create semi-transparent overlay
                overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                
                shape_color = (
                    random.randint(150, 255),
                    random.randint(150, 255), 
                    random.randint(150, 255),
                    30  # Alpha
                )
                
                if random.choice([True, False]):
                    overlay_draw.rectangle([x1, y1, x2, y2], fill=shape_color)
                else:
                    overlay_draw.ellipse([x1, y1, x2, y2], fill=shape_color)
                
                img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
            
            # Add professional text
            try:
                font_large = ImageFont.truetype("arial.ttf", 80)
                font_medium = ImageFont.truetype("arial.ttf", 50)
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
            
            # Process text for better display
            text_lines = []
            words = point.split()
            if len(words) > 6:
                # Split into multiple lines
                mid = len(words) // 2
                text_lines = [" ".join(words[:mid]), " ".join(words[mid:])]
            else:
                text_lines = [point]
            
            # Calculate total text height
            total_height = 0
            line_heights = []
            for line in text_lines:
                bbox = draw.textbbox((0, 0), line, font=font_large)
                line_height = bbox[3] - bbox[1]
                line_heights.append(line_height)
                total_height += line_height + 10
            
            # Start position for centered text
            start_y = (height - total_height) // 2
            
            # Draw each line with shadow
            for j, line in enumerate(text_lines):
                bbox = draw.textbbox((0, 0), line, font=font_large)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                y = start_y + sum(line_heights[:j]) + j * 10
                
                # Text shadow (multiple layers for depth)
                for shadow_offset in range(1, 6):
                    shadow_alpha = 255 - (shadow_offset * 40)
                    draw.text((x + shadow_offset, y + shadow_offset), line, 
                             font=font_large, fill=(0, 0, 0, shadow_alpha))
                
                # Main text
                draw.text((x, y), line, font=font_large, fill=(255, 255, 255))
            
            # Add part number
            part_text = f"Part {i+1}"
            part_bbox = draw.textbbox((0, 0), part_text, font=font_medium)
            part_width = part_bbox[2] - part_bbox[0]
            part_x = (width - part_width) // 2
            part_y = start_y + total_height + 30
            
            # Part number with shadow
            draw.text((part_x + 3, part_y + 3), part_text, font=font_medium, fill=(0, 0, 0))
            draw.text((part_x, part_y), part_text, font=font_medium, fill=(220, 220, 220))
            
            # Save image
            filename = f"quality_img_{i+1}_{int(time.time())}.jpg"
            filepath = Path("generated_images") / filename
            img.save(filepath, quality=95)
            images.append(str(filepath))
            
            logger.info(f"  Created image {i+1}: {filename}")
        
        return images
    
    def create_video_simple(self, images, title):
        """Create video using simple FFmpeg command"""
        logger.info("Creating video...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path("final_videos") / f"automagic_quality_{timestamp}.mp4"
        
        # Simple slideshow: 25 seconds per image = 100 second video
        duration_per_image = 25
        
        try:
            import subprocess
            
            # Build simple FFmpeg command
            cmd = ['ffmpeg', '-y']
            
            # Add each image with duration
            for img_path in images:
                cmd.extend(['-loop', '1', '-t', str(duration_per_image), '-i', img_path])
            
            # Filter to concatenate and add silent audio
            total_duration = len(images) * duration_per_image
            filter_complex = f"[0:v][1:v][2:v][3:v]concat=n={len(images)}:v=1:a=0,scale=1920:1080,fps=25[v]"
            
            cmd.extend([
                '-filter_complex', filter_complex,
                '-map', '[v]',
                '-f', 'lavfi', '-t', str(total_duration), '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
                '-c:v', 'libx264', '-c:a', 'aac', '-pix_fmt', 'yuv420p',
                '-shortest',
                str(output_path)
            ])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Video created: {output_path}")
                return str(output_path)
            else:
                logger.error(f"FFmpeg failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Video creation failed: {e}")
            return None
    
    def upload_to_youtube(self, video_path, title):
        """Upload to YouTube"""
        try:
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            import pickle
            
            if not os.path.exists('token.pickle'):
                logger.error("No YouTube authentication")
                return None
            
            with open('token.pickle', 'rb') as f:
                creds = pickle.load(f)
            
            youtube = build('youtube', 'v3', credentials=creds)
            
            body = {
                'snippet': {
                    'title': f'AutoMagic: {title}',
                    'description': f'An engaging video about {title}. Created by AutoMagic AI.',
                    'tags': ['automagic', 'educational', 'amazing', 'discovery'],
                    'categoryId': '27'  # Education
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
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Log upload
            with open('uploaded_videos.log', 'a', encoding='utf-8') as f:
                f.write(f"{title}\\n")
            
            logger.info(f"Uploaded successfully: {url}")
            return url
            
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return None
    
    def create_complete_video(self):
        """Main function to create complete quality video"""
        try:
            print("=" * 60)
            print("AUTOMAGIC: CREATING QUALITY VIDEO")
            print("=" * 60)
            
            # Get topic
            topic = self.get_trending_topic()
            print(f"Topic: {topic}")
            
            # Generate script
            script = self.generate_script(topic)
            print(f"Script: {len(script)} characters")
            
            # Create images
            images = self.create_quality_images(script)
            print(f"Images: {len(images)} created")
            
            # Create video
            video_path = self.create_video_simple(images, topic)
            if not video_path:
                print("Video creation failed")
                return False
            
            # Check video size
            if os.path.exists(video_path):
                size_mb = os.path.getsize(video_path) / (1024 * 1024)
                print(f"Video file: {video_path} ({size_mb:.1f} MB)")
            
            # Upload to YouTube
            youtube_url = self.upload_to_youtube(video_path, topic)
            
            if youtube_url:
                print(f"SUCCESS! Uploaded to YouTube: {youtube_url}")
            else:
                print(f"Video ready for manual upload: {video_path}")
            
            print("=" * 60)
            print("AUTOMAGIC COMPLETE!")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"AutoMagic failed: {e}")
            return False

if __name__ == "__main__":
    automagic = SimpleWorkingAutoMagic()
    automagic.create_complete_video()