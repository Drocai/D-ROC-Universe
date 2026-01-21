#!/usr/bin/env python3
"""
Watchable Video Maker - Creates actually engaging content people will watch
Uses simpler methods to avoid Windows permission issues
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
import math

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np

from dotenv import load_dotenv
load_dotenv()

class WatchableVideoMaker:
    def __init__(self):
        self.output_dir = Path("final_videos")
        self.output_dir.mkdir(exist_ok=True)
        self.assets_dir = Path("video_assets")
        self.assets_dir.mkdir(exist_ok=True)
        
    def get_viral_story(self):
        """Get a story that people actually want to watch"""
        
        # Try Reddit for actual interesting stories
        try:
            headers = {'User-Agent': 'AutoMagic/1.0'}
            subreddits = ['todayilearned', 'interestingasfuck', 'Damnthatsinteresting']
            
            for subreddit in subreddits:
                response = requests.get(f'https://www.reddit.com/r/{subreddit}/hot.json?limit=5', 
                                       headers=headers, timeout=5)
                if response.status_code == 200:
                    posts = response.json()['data']['children']
                    for post in posts:
                        title = post['data']['title']
                        if len(title) > 20 and len(title) < 150:
                            return title.replace('TIL ', '').replace('TIL: ', '')
        except:
            pass
        
        # Fallback viral-style stories
        stories = [
            "This Man Predicted His Own Death Date 20 Years in Advance",
            "Scientists Found Something Terrifying Inside This Ancient Pyramid", 
            "What This Homeless Man Did With $100 Will Restore Your Faith in Humanity",
            "The Real Reason Why Airplane Windows Are Round Will Shock You",
            "This Simple Math Trick Can Read Your Mind - Try It",
            "The Dark Secret Hidden in Every Smart Phone",
            "What Happens to Your Body if You Eat Eggs Every Day",
            "The One Exercise That Fixes Everything Wrong With Your Body"
        ]
        return random.choice(stories)
    
    def create_story_segments(self, title):
        """Create engaging story segments with hooks"""
        
        segments = [
            {
                "hook": f"What I'm about to tell you about {title.lower()} will completely change your perspective.",
                "duration": 8,
                "style": "dramatic"
            },
            {
                "content": f"You've probably never heard this story before, but {title.lower()} reveals something incredible about human nature.",
                "duration": 12,
                "style": "mystery"
            },
            {
                "reveal": "Here's what actually happened, and why it matters more than you think.",
                "duration": 15,
                "style": "revelation"
            },
            {
                "details": f"The evidence is overwhelming. Scientists, researchers, and experts all agree - {title.lower()} proves what we've suspected all along.",
                "duration": 18,
                "style": "evidence"
            },
            {
                "impact": "But here's the part that will blow your mind. The implications of this discovery are far-reaching and could affect your daily life.",
                "duration": 15,
                "style": "shocking"
            },
            {
                "conclusion": "So what does this mean for you? The answer might surprise you, and the solution is simpler than you think.",
                "duration": 12,
                "style": "resolution"
            },
            {
                "cta": "If this amazed you, wait until you see what we reveal next. Subscribe now and never miss these incredible discoveries!",
                "duration": 8,
                "style": "subscribe"
            }
        ]
        
        return segments
    
    def create_dynamic_visual(self, text, style, segment_index, total_duration):
        """Create a single dynamic visual with movement and effects"""
        
        width, height = 1920, 1080
        
        # Style-based color schemes
        color_schemes = {
            "dramatic": [(5, 5, 20), (40, 20, 60), (80, 40, 100)],
            "mystery": [(20, 30, 50), (60, 80, 120), (100, 140, 180)],
            "revelation": [(60, 30, 10), (120, 80, 40), (200, 140, 80)],
            "evidence": [(10, 50, 30), (40, 100, 60), (80, 160, 120)],
            "shocking": [(80, 10, 10), (160, 40, 40), (220, 100, 100)],
            "resolution": [(30, 60, 100), (80, 120, 160), (140, 180, 220)],
            "subscribe": [(180, 50, 50), (220, 100, 100), (255, 150, 150)]
        }
        
        colors = color_schemes.get(style, [(50, 50, 50), (100, 100, 100), (150, 150, 150)])
        
        # Create base image with animated gradient
        img = Image.new('RGB', (width, height))
        
        # Create animated gradient background
        for y in range(height):
            ratio = y / height
            
            # Animate the gradient over time
            time_factor = math.sin(segment_index * 0.5) * 0.3
            
            if ratio < 0.4:
                # Top section
                t = ratio / 0.4
                r = int(colors[0][0] * (1-t) + colors[1][0] * t + time_factor * 30)
                g = int(colors[0][1] * (1-t) + colors[1][1] * t + time_factor * 20)
                b = int(colors[0][2] * (1-t) + colors[1][2] * t + time_factor * 40)
            else:
                # Bottom section
                t = (ratio - 0.4) / 0.6
                r = int(colors[1][0] * (1-t) + colors[2][0] * t + time_factor * 30)
                g = int(colors[1][1] * (1-t) + colors[2][1] * t + time_factor * 20)
                b = int(colors[1][2] * (1-t) + colors[2][2] * t + time_factor * 40)
            
            # Clamp values
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            for x in range(width):
                img.putpixel((x, y), (r, g, b))
        
        # Add dynamic elements
        draw = ImageDraw.Draw(img)
        
        # Add floating particles based on style
        particle_count = {"dramatic": 15, "mystery": 20, "shocking": 25}.get(style, 10)
        
        for i in range(particle_count):
            # Animated particle positions
            base_x = (i * 150) % width
            base_y = (i * 80) % height
            
            # Add movement based on segment
            offset_x = math.sin(segment_index * 0.3 + i * 0.5) * 100
            offset_y = math.cos(segment_index * 0.2 + i * 0.3) * 50
            
            particle_x = base_x + offset_x
            particle_y = base_y + offset_y
            
            # Keep particles on screen
            particle_x = max(0, min(width, particle_x))
            particle_y = max(0, min(height, particle_y))
            
            # Animated size
            size = 3 + math.sin(segment_index * 0.4 + i) * 2
            
            # Draw particle
            draw.ellipse([particle_x - size, particle_y - size,
                         particle_x + size, particle_y + size],
                        fill=(255, 255, 255, 80))
        
        # Add geometric shapes for visual interest
        for i in range(5):
            shape_x = (width // 6) * (i + 1)
            shape_y = height // 2 + math.sin(segment_index * 0.3 + i) * 200
            shape_size = 50 + math.cos(segment_index * 0.2 + i) * 30
            
            # Semi-transparent overlay
            overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            
            # Different shapes based on style
            if style in ["dramatic", "shocking"]:
                # Diamonds
                points = [
                    (shape_x, shape_y - shape_size),
                    (shape_x + shape_size, shape_y),
                    (shape_x, shape_y + shape_size),
                    (shape_x - shape_size, shape_y)
                ]
                overlay_draw.polygon(points, fill=(colors[2][0], colors[2][1], colors[2][2], 30))
            else:
                # Circles
                overlay_draw.ellipse([shape_x - shape_size, shape_y - shape_size,
                                    shape_x + shape_size, shape_y + shape_size],
                                   fill=(colors[2][0], colors[2][1], colors[2][2], 25))
            
            img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        
        # Add text with dynamic styling
        draw = ImageDraw.Draw(img)
        
        try:
            font_large = ImageFont.truetype("arial.ttf", 90)
            font_medium = ImageFont.truetype("arial.ttf", 60)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
        
        # Break text into lines
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            test_line = " ".join(current_line)
            bbox = draw.textbbox((0, 0), test_line, font=font_large)
            
            if bbox[2] - bbox[0] > width - 200:  # Leave margin
                if len(current_line) > 1:
                    lines.append(" ".join(current_line[:-1]))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []
        
        if current_line:
            lines.append(" ".join(current_line))
        
        # Center text vertically
        line_height = 110
        total_height = len(lines) * line_height
        start_y = (height - total_height) // 2
        
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font_large)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = start_y + i * line_height
            
            # Text shadow with glow effect
            for shadow_offset in range(8, 0, -1):
                shadow_alpha = 255 - (shadow_offset * 25)
                shadow_color = (0, 0, 0, shadow_alpha)
                
                draw.text((x + shadow_offset, y + shadow_offset), line, 
                         font=font_large, fill=shadow_color)
            
            # Colored outline based on style
            outline_color = colors[2] if style != "subscribe" else (255, 255, 255)
            
            for dx in [-2, -1, 0, 1, 2]:
                for dy in [-2, -1, 0, 1, 2]:
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), line, font=font_large, 
                                 fill=outline_color)
            
            # Main text
            text_color = (255, 255, 255) if style != "subscribe" else (255, 255, 100)
            draw.text((x, y), line, font=font_large, fill=text_color)
        
        # Add style-specific elements
        if style == "dramatic":
            # Add lightning effect
            for i in range(3):
                x = random.randint(50, width - 50)
                draw.line([(x, 0), (x + random.randint(-50, 50), height)], 
                         fill=(255, 255, 255), width=2)
        
        elif style == "shocking":
            # Add exclamation effects
            for i in range(4):
                x = 100 + i * 400
                y = 100
                draw.text((x, y), "!", font=font_large, fill=(255, 255, 0))
        
        return img
    
    def create_voice_narration(self, segments):
        """Create voice narration for all segments"""
        
        full_script = " ".join([
            segment.get("hook", "") + " " + 
            segment.get("content", "") + " " + 
            segment.get("reveal", "") + " " +
            segment.get("details", "") + " " +
            segment.get("impact", "") + " " +
            segment.get("conclusion", "") + " " +
            segment.get("cta", "")
            for segment in segments
        ])
        
        audio_path = self.assets_dir / f"narration_{int(time.time())}.wav"
        
        # Use Windows SAPI (proven to work)
        try:
            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            
            # Configure voice
            voices = speaker.GetVoices()
            for voice in voices:
                if any(name in voice.GetDescription() for name in ['Zira', 'David', 'Mark']):
                    speaker.Voice = voice
                    break
            
            speaker.Rate = 2  # Slightly faster for engagement
            speaker.Volume = 100
            
            # Create file stream
            stream = win32com.client.Dispatch("SAPI.SpFileStream")
            stream.Open(str(audio_path), 3)
            speaker.AudioOutputStream = stream
            speaker.Speak(full_script)
            stream.Close()
            
            print(f"  Voice created: {audio_path}")
            return str(audio_path)
            
        except Exception as e:
            print(f"  Voice creation failed: {e}")
            return None
    
    def create_engaging_video(self):
        """Create the complete engaging video"""
        
        print("=" * 60)
        print("CREATING WATCHABLE VIDEO CONTENT")
        print("=" * 60)
        
        # Get viral story
        story = self.get_viral_story()
        print(f"Story: {story}")
        
        # Create segments
        segments = self.create_story_segments(story)
        print(f"Segments: {len(segments)} parts")
        
        # Create visuals for each segment
        visual_files = []
        total_duration = 0
        
        for i, segment in enumerate(segments):
            print(f"  Creating visual {i+1}/{len(segments)}...")
            
            # Get text for this segment
            text = (segment.get("hook", "") or 
                   segment.get("content", "") or 
                   segment.get("reveal", "") or
                   segment.get("details", "") or
                   segment.get("impact", "") or
                   segment.get("conclusion", "") or
                   segment.get("cta", ""))
            
            style = segment["style"]
            duration = segment["duration"]
            total_duration += duration
            
            # Create dynamic visual
            img = self.create_dynamic_visual(text, style, i, duration)
            
            # Save image
            img_path = self.assets_dir / f"segment_{i:02d}.jpg"
            img.save(img_path, quality=95)
            visual_files.append((str(img_path), duration))
        
        # Create voice narration
        print("Creating voice narration...")
        audio_path = self.create_voice_narration(segments)
        
        # Assemble video
        print("Assembling video...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"watchable_{timestamp}.mp4"
        
        # Create input list for FFmpeg
        input_list = self.assets_dir / f"input_{timestamp}.txt"
        
        with open(input_list, 'w') as f:
            for img_path, duration in visual_files:
                f.write(f"file '{os.path.abspath(img_path)}'\\n")
                f.write(f"duration {duration}\\n")
            # Last image
            f.write(f"file '{os.path.abspath(visual_files[-1][0])}'\\n")
        
        # Build FFmpeg command
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat', '-safe', '0', '-i', str(input_list),
            '-vf', 'scale=1920:1080,fps=30',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
            '-pix_fmt', 'yuv420p'
        ]
        
        # Add audio if available
        if audio_path:
            cmd.extend(['-i', audio_path, '-c:a', 'aac', '-b:a', '192k', '-shortest'])
        else:
            # Add silent audio
            cmd.extend(['-f', 'lavfi', '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100:duration={total_duration}', '-c:a', 'aac'])
        
        cmd.append(str(output_path))
        
        # Run FFmpeg
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            file_size = os.path.getsize(output_path) / (1024 * 1024)
            print(f"Video created: {output_path} ({file_size:.1f} MB)")
            
            # Upload to YouTube
            self.upload_to_youtube(str(output_path), story)
            
            return str(output_path)
        else:
            print(f"Video creation failed: {result.stderr}")
            return None
    
    def upload_to_youtube(self, video_path, title):
        """Upload with viral-optimized metadata"""
        
        try:
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            import pickle
            
            with open('token.pickle', 'rb') as f:
                creds = pickle.load(f)
            
            youtube = build('youtube', 'v3', credentials=creds)
            
            # Viral-optimized title
            if len(title) > 80:
                title = title[:77] + "..."
            
            body = {
                'snippet': {
                    'title': f"{title} 🤯",
                    'description': f'''🔥 {title}

This will absolutely blow your mind! The story behind this is incredible and the ending will shock you.

📺 WATCH UNTIL THE END for the mind-blowing conclusion!

In this video:
🎯 The shocking discovery that changes everything
💡 Evidence that proves the impossible  
🔍 What experts don't want you to know
⚡ The truth that will amaze you
🚀 How this affects YOUR life

TIMESTAMPS:
0:00 - The Hook That Will Shock You
0:30 - Evidence That Changes Everything  
1:00 - The Revelation You Never Expected
2:00 - What This Means For You

🔔 SUBSCRIBE for daily mind-blowing content
👍 LIKE if this amazed you
💬 COMMENT your thoughts below
📤 SHARE with someone who needs to see this

#MindBlowing #Viral #Shocking #MustWatch #Incredible #Amazing #Facts #Discovery''',
                    'tags': ['viral', 'mindblowing', 'shocking', 'amazing', 'incredible', 
                            'mustwatch', 'facts', 'discovery', 'story', 'trending'],
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
            
            print(f"🎉 Uploaded to YouTube: https://www.youtube.com/watch?v={video_id}")
            
            # Log upload
            with open('uploaded_videos.log', 'a', encoding='utf-8') as f:
                f.write(f"VIRAL: {title} - {datetime.now()}\\n")
            
        except Exception as e:
            print(f"Upload failed: {e}")

if __name__ == "__main__":
    maker = WatchableVideoMaker()
    maker.create_engaging_video()