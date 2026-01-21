#!/usr/bin/env python3
"""
Engaging Video Creator - Creates ACTUAL watchable content with animations,
stock footage, dynamic visuals, and storytelling
"""

import os
import sys
import json
import time
import subprocess
import random
import requests
from datetime import datetime
from pathlib import Path
import tempfile
import shutil

# For animations and visuals
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import numpy as np

# Load environment
from dotenv import load_dotenv
load_dotenv()

class EngagingVideoCreator:
    def __init__(self):
        self.output_dir = Path("final_videos")
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir = Path("temp_assets")
        self.temp_dir.mkdir(exist_ok=True)
        
        # Free API keys for stock content
        self.pexels_key = "563492ad6f91700001000001d33e48e9e3474ef9b81a2fbbf67234fa"  # Free tier
        
    def get_trending_story(self):
        """Get an engaging story-based topic"""
        
        # Try Reddit for real trending stories
        try:
            headers = {'User-Agent': 'AutoMagic/1.0'}
            response = requests.get('https://www.reddit.com/r/todayilearned/top.json?limit=10', 
                                   headers=headers, timeout=5)
            if response.status_code == 200:
                posts = response.json()['data']['children']
                for post in posts:
                    title = post['data']['title']
                    if 'TIL' in title:
                        # Clean up the title
                        story = title.replace('TIL ', '').replace('TIL:', '')
                        return story[:200]
        except:
            pass
        
        # Fallback engaging stories
        stories = [
            "How a Pizza Delivery Driver Saved 3 Lives in One Night",
            "The Unbelievable Story of the World's Luckiest Man",
            "This Simple Trick Helped Students Improve Grades by 40%",
            "Scientists Discovered Something Incredible in the Amazon",
            "The Hidden Message in Every Dollar Bill",
            "What Happens to Your Body When You Stop Eating Sugar",
            "The Secret Room Found After 500 Years in Famous Castle"
        ]
        return random.choice(stories)
    
    def create_story_script(self, topic):
        """Create an engaging story script with scenes"""
        
        # Structure: Hook -> Setup -> Development -> Climax -> Resolution
        script = {
            "title": topic,
            "scenes": [
                {
                    "type": "hook",
                    "duration": 5,
                    "text": f"What if I told you {topic.lower()}? Stay tuned, because this story will blow your mind.",
                    "visual": "dramatic_intro",
                    "animation": "zoom_in"
                },
                {
                    "type": "setup", 
                    "duration": 10,
                    "text": f"It all started when researchers made an unexpected discovery. {topic} wasn't just a coincidence - it was part of something much bigger.",
                    "visual": "mystery",
                    "animation": "pan_left"
                },
                {
                    "type": "development",
                    "duration": 15,
                    "text": "The evidence was overwhelming. Scientists couldn't believe what they were seeing. Every test confirmed the impossible was actually happening.",
                    "visual": "evidence",
                    "animation": "ken_burns"
                },
                {
                    "type": "story",
                    "duration": 20,
                    "text": f"Here's what actually happened: {topic}. But that's not even the most incredible part. What came next changed everything we thought we knew.",
                    "visual": "revelation",
                    "animation": "parallax"
                },
                {
                    "type": "climax",
                    "duration": 15,
                    "text": "The implications are staggering. This discovery means that everything we've been taught might need to be reconsidered. The truth is far stranger than fiction.",
                    "visual": "mind_blown",
                    "animation": "rotate_zoom"
                },
                {
                    "type": "resolution",
                    "duration": 10,
                    "text": "So what does this mean for you? The answer might surprise you. This knowledge could literally change your life starting today.",
                    "visual": "conclusion",
                    "animation": "fade_out"
                },
                {
                    "type": "cta",
                    "duration": 5,
                    "text": "Want more mind-blowing stories? Subscribe now and never miss an incredible discovery!",
                    "visual": "subscribe",
                    "animation": "pulse"
                }
            ]
        }
        
        return script
    
    def download_stock_footage(self, keyword, count=3):
        """Download stock video footage from Pexels"""
        
        videos = []
        
        try:
            headers = {"Authorization": self.pexels_key}
            url = "https://api.pexels.com/videos/search"
            params = {
                "query": keyword,
                "per_page": count,
                "size": "medium"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for video in data.get("videos", [])[:count]:
                    video_files = video.get("video_files", [])
                    
                    # Get HD version
                    for file in video_files:
                        if file.get("quality") == "hd" and file.get("width") >= 1280:
                            video_url = file.get("link")
                            
                            # Download video
                            video_response = requests.get(video_url, stream=True, timeout=30)
                            if video_response.status_code == 200:
                                filename = self.temp_dir / f"stock_{len(videos)}.mp4"
                                
                                with open(filename, 'wb') as f:
                                    for chunk in video_response.iter_content(chunk_size=8192):
                                        f.write(chunk)
                                
                                videos.append(str(filename))
                                print(f"  Downloaded stock footage: {keyword}")
                                break
        except Exception as e:
            print(f"  Stock footage download failed: {e}")
        
        return videos
    
    def create_animated_scene(self, scene_data, index):
        """Create an animated scene with effects"""
        
        width, height = 1920, 1080
        fps = 30
        duration = scene_data["duration"]
        total_frames = fps * duration
        
        scene_dir = self.temp_dir / f"scene_{index}"
        scene_dir.mkdir(exist_ok=True)
        
        # Color schemes based on scene type
        color_schemes = {
            "hook": [(20, 20, 40), (100, 20, 60)],
            "setup": [(30, 40, 80), (80, 100, 150)],
            "development": [(40, 60, 90), (100, 140, 180)],
            "story": [(60, 40, 100), (140, 100, 180)],
            "climax": [(100, 30, 30), (200, 100, 100)],
            "resolution": [(30, 80, 120), (100, 180, 220)],
            "subscribe": [(200, 50, 50), (250, 150, 150)]
        }
        
        colors = color_schemes.get(scene_data["type"], [(50, 50, 50), (150, 150, 150)])
        
        # Generate frames
        for frame_num in range(total_frames):
            # Create base image with gradient
            img = Image.new('RGB', (width, height))
            draw = ImageDraw.Draw(img)
            
            # Animated gradient
            t = frame_num / total_frames
            
            for y in range(height):
                ratio = y / height
                # Animate color shift
                color_shift = np.sin(t * np.pi * 2) * 0.2
                
                r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
                g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
                b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
                
                r = max(0, min(255, int(r * (1 + color_shift))))
                g = max(0, min(255, int(g * (1 + color_shift))))
                b = max(0, min(255, int(b * (1 + color_shift))))
                
                draw.rectangle([(0, y), (width, y+1)], fill=(r, g, b))
            
            # Add animated elements based on animation type
            animation = scene_data.get("animation", "none")
            
            if animation == "zoom_in":
                # Zoom effect
                scale = 1 + (t * 0.3)
                img = img.resize((int(width * scale), int(height * scale)), Image.Resampling.LANCZOS)
                # Crop to center
                left = (img.width - width) // 2
                top = (img.height - height) // 2
                img = img.crop((left, top, left + width, top + height))
                
            elif animation == "pan_left":
                # Panning effect
                offset = int(t * 200)
                new_img = Image.new('RGB', (width, height))
                new_img.paste(img, (-offset, 0))
                img = new_img
                
            elif animation == "ken_burns":
                # Ken Burns effect (slow zoom and pan)
                scale = 1 + (t * 0.1)
                img = img.resize((int(width * scale), int(height * scale)), Image.Resampling.LANCZOS)
                offset_x = int(t * 50)
                offset_y = int(np.sin(t * np.pi) * 30)
                new_img = Image.new('RGB', (width, height))
                new_img.paste(img, (-offset_x, -offset_y))
                img = new_img
                
            elif animation == "rotate_zoom":
                # Rotation with zoom
                angle = t * 10
                scale = 1 + (np.sin(t * np.pi * 2) * 0.1)
                img = img.rotate(angle, expand=False, fillcolor=(0, 0, 0))
                img = img.resize((int(width * scale), int(height * scale)), Image.Resampling.LANCZOS)
                # Center crop
                left = (img.width - width) // 2
                top = (img.height - height) // 2
                img = img.crop((left, top, left + width, top + height))
                
            elif animation == "pulse":
                # Pulsing effect
                brightness = 1 + (np.sin(t * np.pi * 4) * 0.2)
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(brightness)
            
            # Add animated shapes
            draw = ImageDraw.Draw(img)
            
            # Floating particles
            for i in range(10):
                particle_y = (frame_num * 3 + i * 100) % height
                particle_x = width // 2 + np.sin(frame_num * 0.1 + i) * 300
                particle_size = 5 + np.sin(frame_num * 0.2 + i) * 3
                
                draw.ellipse([particle_x - particle_size, particle_y - particle_size,
                            particle_x + particle_size, particle_y + particle_size],
                           fill=(255, 255, 255, 100))
            
            # Add text overlay with animation
            try:
                font_large = ImageFont.truetype("arial.ttf", 80)
                font_small = ImageFont.truetype("arial.ttf", 40)
            except:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Animated text
            text = scene_data["text"]
            
            # Text reveal animation (typewriter effect)
            chars_to_show = int(len(text) * min(1, t * 2))
            display_text = text[:chars_to_show]
            
            if display_text:
                # Calculate text position
                lines = []
                words = display_text.split()
                current_line = []
                
                for word in words:
                    current_line.append(word)
                    test_line = " ".join(current_line)
                    bbox = draw.textbbox((0, 0), test_line, font=font_large)
                    
                    if bbox[2] - bbox[0] > width - 200:
                        lines.append(" ".join(current_line[:-1]))
                        current_line = [word]
                
                if current_line:
                    lines.append(" ".join(current_line))
                
                # Draw each line
                total_height = len(lines) * 100
                start_y = (height - total_height) // 2
                
                for i, line in enumerate(lines):
                    bbox = draw.textbbox((0, 0), line, font=font_large)
                    text_width = bbox[2] - bbox[0]
                    x = (width - text_width) // 2
                    y = start_y + i * 100
                    
                    # Text glow effect
                    for offset in range(10, 0, -2):
                        alpha = 20 - offset * 2
                        draw.text((x, y), line, font=font_large, 
                                fill=(255, 255, 255, alpha))
                    
                    # Main text
                    draw.text((x, y), line, font=font_large, fill=(255, 255, 255))
            
            # Save frame
            frame_path = scene_dir / f"frame_{frame_num:04d}.png"
            img.save(frame_path)
        
        # Create video from frames
        scene_video = self.temp_dir / f"scene_{index}.mp4"
        
        cmd = [
            'ffmpeg', '-y',
            '-framerate', str(fps),
            '-i', str(scene_dir / 'frame_%04d.png'),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-crf', '23',
            str(scene_video)
        ]
        
        subprocess.run(cmd, capture_output=True)
        
        # Clean up frames
        shutil.rmtree(scene_dir)
        
        return str(scene_video)
    
    def create_voice_narration(self, script):
        """Create engaging voice narration"""
        
        full_text = " ".join([scene["text"] for scene in script["scenes"]])
        audio_path = self.temp_dir / "narration.wav"
        
        # Use Windows SAPI (proven to work)
        try:
            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            
            # Select best voice
            voices = speaker.GetVoices()
            for voice in voices:
                if 'Microsoft Zira' in voice.GetDescription():
                    speaker.Voice = voice
                    break
            
            # Adjust speech parameters
            speaker.Rate = 1  # Slightly faster
            speaker.Volume = 100
            
            # Save to file
            stream = win32com.client.Dispatch("SAPI.SpFileStream")
            stream.Open(str(audio_path), 3)
            speaker.AudioOutputStream = stream
            speaker.Speak(full_text)
            stream.Close()
            
            print(f"  Voice narration created: {audio_path}")
            return str(audio_path)
            
        except Exception as e:
            print(f"  Voice creation failed: {e}")
            
            # Fallback: silent audio
            duration = len(full_text) // 3  # Rough estimate
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100',
                '-t', str(duration),
                str(audio_path)
            ]
            subprocess.run(cmd, capture_output=True)
            
            return str(audio_path)
    
    def add_background_music(self, video_path):
        """Add royalty-free background music"""
        
        # Download royalty-free music (simplified for now)
        # In production, you'd have a library of music files
        
        output_path = video_path.replace('.mp4', '_with_music.mp4')
        
        # For now, just return the original
        # In production, mix audio tracks properly
        return video_path
    
    def create_engaging_video(self):
        """Main function to create an engaging video"""
        
        print("=" * 60)
        print("CREATING ENGAGING VIDEO CONTENT")
        print("=" * 60)
        
        # Get trending story
        story = self.get_trending_story()
        print(f"Story: {story}")
        
        # Create script with scenes
        script = self.create_story_script(story)
        print(f"Script: {len(script['scenes'])} scenes")
        
        # Download stock footage
        keywords = ["technology", "science", "discovery", "amazing"]
        stock_videos = []
        for keyword in keywords[:2]:  # Limit for speed
            videos = self.download_stock_footage(keyword, count=1)
            stock_videos.extend(videos)
        
        print(f"Stock footage: {len(stock_videos)} clips")
        
        # Create animated scenes
        scene_videos = []
        for i, scene in enumerate(script["scenes"]):
            print(f"  Creating scene {i+1}/{len(script['scenes'])}...")
            scene_video = self.create_animated_scene(scene, i)
            scene_videos.append(scene_video)
        
        # Create voice narration
        print("Creating voice narration...")
        audio_path = self.create_voice_narration(script)
        
        # Combine everything
        print("Assembling final video...")
        
        # Create concat list
        concat_list = self.temp_dir / "concat.txt"
        with open(concat_list, 'w') as f:
            # Mix animated scenes with stock footage
            for i, scene_video in enumerate(scene_videos):
                f.write(f"file '{os.path.abspath(scene_video)}'\n")
                
                # Insert stock footage between scenes if available
                if stock_videos and i < len(stock_videos):
                    f.write(f"file '{os.path.abspath(stock_videos[i])}'\n")
                    f.write("duration 3\n")  # Show for 3 seconds
        
        # Final output
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"engaging_video_{timestamp}.mp4"
        
        # Combine with audio
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat', '-safe', '0', '-i', str(concat_list),
            '-i', audio_path,
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
            '-c:a', 'aac', '-b:a', '192k',
            '-shortest',
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Video created: {output_path}")
            
            # Clean up temp files
            shutil.rmtree(self.temp_dir)
            self.temp_dir.mkdir(exist_ok=True)
            
            # Upload to YouTube
            self.upload_to_youtube(str(output_path), story)
            
            return str(output_path)
        else:
            print(f"Video assembly failed: {result.stderr}")
            return None
    
    def upload_to_youtube(self, video_path, title):
        """Upload the engaging video to YouTube"""
        
        try:
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            import pickle
            
            with open('token.pickle', 'rb') as f:
                creds = pickle.load(f)
            
            youtube = build('youtube', 'v3', credentials=creds)
            
            body = {
                'snippet': {
                    'title': f"{title[:90]} | AutoMagic",
                    'description': f'''🔥 {title}

This incredible story will blow your mind! Watch till the end for the shocking conclusion.

In this video:
✓ The unbelievable discovery
✓ Evidence that changes everything  
✓ What this means for you
✓ The shocking truth revealed

🔔 Subscribe for daily mind-blowing content
👍 Like if this amazed you
💬 Share your thoughts in the comments
🔗 Share with someone who needs to see this

#Trending #MindBlowing #Discovery #Amazing #MustWatch #Viral''',
                    'tags': ['trending', 'viral', 'amazing', 'discovery', 'mindblowing', 
                            'mustwatch', 'story', 'incredible', 'facts'],
                    'categoryId': '24'  # Entertainment
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
            
            print(f"Uploaded to YouTube: https://www.youtube.com/watch?v={video_id}")
            
        except Exception as e:
            print(f"Upload failed: {e}")

if __name__ == "__main__":
    creator = EngagingVideoCreator()
    creator.create_engaging_video()