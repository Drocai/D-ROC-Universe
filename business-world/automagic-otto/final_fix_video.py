#!/usr/bin/env python3
"""
Final Fix Video Creator - Guaranteed to work
"""

import os
import sys
import logging
import json
from datetime import datetime
from pathlib import Path
import random
import time
import subprocess

from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinalFixVideoCreator:
    def __init__(self):
        self.output_dir = Path("final_videos")
        self.output_dir.mkdir(exist_ok=True)
        
        self.images_dir = Path("generated_images")
        self.images_dir.mkdir(exist_ok=True)
    
    def create_final_images(self) -> list:
        """Create 4 quality images"""
        logger.info("Creating quality images...")
        
        topics = [
            "Amazing Discovery",
            "Scientific Breakthrough", 
            "Mind-Blowing Facts",
            "Incredible Results"
        ]
        
        # Professional color schemes
        color_schemes = [
            [(25, 42, 86), (58, 96, 115), (107, 147, 173)],   # Blue professional
            [(86, 25, 42), (115, 58, 96), (173, 107, 147)],   # Red professional  
            [(42, 86, 25), (96, 115, 58), (147, 173, 107)],   # Green professional
            [(86, 42, 25), (115, 96, 58), (173, 147, 107)]    # Orange professional
        ]
        
        image_paths = []
        
        for i, (topic, colors) in enumerate(zip(topics, color_schemes)):
            # Create image
            width, height = 1920, 1080
            img = Image.new('RGB', (width, height), colors[0])
            
            # Create gradient
            for y in range(height):
                ratio = y / height
                if ratio < 0.5:
                    t = ratio * 2
                    r = int(colors[0][0] * (1-t) + colors[1][0] * t)
                    g = int(colors[0][1] * (1-t) + colors[1][1] * t)
                    b = int(colors[0][2] * (1-t) + colors[1][2] * t)
                else:
                    t = (ratio - 0.5) * 2
                    r = int(colors[1][0] * (1-t) + colors[2][0] * t)
                    g = int(colors[1][1] * (1-t) + colors[2][1] * t)
                    b = int(colors[1][2] * (1-t) + colors[2][2] * t)
                
                for x in range(width):
                    img.putpixel((x, y), (r, g, b))
            
            # Add text
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("arial.ttf", 100)
            except:
                font = ImageFont.load_default()
            
            # Calculate text position
            bbox = draw.textbbox((0, 0), topic, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            # Draw shadow
            draw.text((x+5, y+5), topic, font=font, fill=(0, 0, 0))
            # Draw main text
            draw.text((x, y), topic, font=font, fill=(255, 255, 255))
            
            # Add part number
            part_text = f"Part {i+1}"
            try:
                small_font = ImageFont.truetype("arial.ttf", 50)
            except:
                small_font = ImageFont.load_default()
            
            part_bbox = draw.textbbox((0, 0), part_text, font=small_font)
            part_width = part_bbox[2] - part_bbox[0]
            part_x = (width - part_width) // 2
            part_y = y + text_height + 30
            
            draw.text((part_x+3, part_y+3), part_text, font=small_font, fill=(0, 0, 0))
            draw.text((part_x, part_y), part_text, font=small_font, fill=(200, 200, 200))
            
            # Save image
            filename = f"final_image_{i+1}.jpg"
            filepath = self.images_dir / filename
            img.save(filepath, quality=95)
            image_paths.append(str(filepath))
        
        logger.info(f"Created {len(image_paths)} images")
        return image_paths
    
    def create_final_video(self, images: list) -> str:
        """Create video using simple FFmpeg command"""
        logger.info("Creating final video...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"final_quality_{timestamp}.mp4"
        
        # Create a simple slideshow with 20 seconds per image
        duration_per_image = 20
        total_duration = len(images) * duration_per_image
        
        # Simple FFmpeg command that works
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1', '-t', str(duration_per_image), '-i', images[0],
            '-loop', '1', '-t', str(duration_per_image), '-i', images[1], 
            '-loop', '1', '-t', str(duration_per_image), '-i', images[2],
            '-loop', '1', '-t', str(duration_per_image), '-i', images[3],
            '-filter_complex', 
            f'[0:v][1:v][2:v][3:v]concat=n=4:v=1:a=0,scale=1920:1080,fps=25[v]',
            '-map', '[v]',
            '-f', 'lavfi', '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100:duration={total_duration}',
            '-c:v', 'libx264', '-c:a', 'aac', '-pix_fmt', 'yuv420p',
            '-t', str(total_duration),
            str(output_path)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Video created successfully: {output_path}")
                return str(output_path)
            else:
                logger.error(f"FFmpeg error: {result.stderr}")
                return None
        except Exception as e:
            logger.error(f"Video creation failed: {e}")
            return None
    
    def upload_to_youtube(self, video_path: str) -> str:
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
            
            title = "AutoMagic: Amazing Scientific Discoveries That Will Blow Your Mind"
            
            body = {
                'snippet': {
                    'title': title,
                    'description': 'Incredible discoveries and breakthrough findings that are changing everything we know about science and technology.',
                    'tags': ['science', 'discovery', 'amazing', 'facts', 'automagic'],
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
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Log the upload
            with open('uploaded_videos.log', 'a', encoding='utf-8') as f:
                f.write(f"{title}\n")
            
            logger.info(f"YouTube upload successful: {youtube_url}")
            return youtube_url
            
        except Exception as e:
            logger.error(f"YouTube upload failed: {e}")
            return None
    
    def create_complete_video(self):
        """Create complete high-quality video"""
        try:
            print("=" * 60)
            print("CREATING FINAL QUALITY VIDEO")
            print("=" * 60)
            
            # Create images
            images = self.create_final_images()
            
            # Create video
            video_path = self.create_final_video(images)
            if not video_path:
                print("Video creation failed")
                return False
            
            # Check video file
            if os.path.exists(video_path):
                file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
                print(f"Video created: {video_path} ({file_size:.1f} MB)")
            
            # Upload to YouTube
            youtube_url = self.upload_to_youtube(video_path)
            
            if youtube_url:
                print(f"SUCCESS! Video uploaded to YouTube: {youtube_url}")
            else:
                print(f"Video ready for manual upload: {video_path}")
            
            print("=" * 60)
            print("VIDEO CREATION COMPLETE!")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"Video creation failed: {e}")
            return False

if __name__ == "__main__":
    creator = FinalFixVideoCreator()
    creator.create_complete_video()