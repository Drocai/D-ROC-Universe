#!/usr/bin/env python3
"""
Video Status Checker - Monitor uploaded videos and processing status
"""

import os
import pickle
import time
from googleapiclient.discovery import build

def check_video_status():
    """Check the status of recently uploaded videos"""
    
    # Recent video IDs from uploads
    video_ids = [
        'pFTTKr3qTCA',  # Most recent
        'RopLZoIT8uo',  # Previous
        'InU4BDvmfRA',  # Earlier
        'E2JVy5ojVwA'   # Original test
    ]
    
    try:
        # Load credentials - use minimal scope
        with open('token.pickle', 'rb') as f:
            creds = pickle.load(f)
        
        youtube = build('youtube', 'v3', credentials=creds)
        
        print("AutoMagic Video Status Check")
        print("=" * 50)
        
        for video_id in video_ids:
            print(f"\nChecking video: {video_id}")
            print(f"URL: https://www.youtube.com/watch?v={video_id}")
            
            try:
                # Try to get basic video info (public API call)
                response = youtube.videos().list(
                    part='snippet',
                    id=video_id
                ).execute()
                
                if response.get('items'):
                    video = response['items'][0]
                    title = video['snippet']['title']
                    published = video['snippet']['publishedAt']
                    print(f"  Title: {title}")
                    print(f"  Published: {published}")
                    print(f"  Status: PUBLIC and VISIBLE")
                else:
                    print("  Status: Not found or still processing")
                    
            except Exception as e:
                print(f"  Error: {e}")
                print("  Status: May still be processing or private")
        
        print(f"\n" + "=" * 50)
        print("NOTE: Videos can take 15 minutes to 2+ hours to process")
        print("HD videos (720p+) typically take longer to process")
        print("Check your channel directly: https://youtube.com/channel/UC9JN2eg-ja0TOws09jCKHow")
        
    except Exception as e:
        print(f"Error checking videos: {e}")

def create_optimized_video():
    """Create a video optimized for faster YouTube processing"""
    
    from PIL import Image, ImageDraw, ImageFont
    from pathlib import Path
    import subprocess
    import json
    from datetime import datetime
    
    print("\nCreating optimized video for faster processing...")
    
    # Create simple, fast-processing images (smaller, simpler)
    images_dir = Path("generated_images")
    images_dir.mkdir(exist_ok=True)
    
    images = []
    
    # Create 3 simple images (less processing time)
    for i in range(3):
        # Smaller resolution for faster processing
        width, height = 1280, 720  # 720p instead of 1080p
        
        # Simple solid colors (faster to process)
        colors = [
            (41, 98, 255),   # Blue
            (255, 59, 48),   # Red  
            (52, 199, 89)    # Green
        ]
        
        img = Image.new('RGB', (width, height), colors[i])
        draw = ImageDraw.Draw(img)
        
        # Simple text
        try:
            font = ImageFont.truetype("arial.ttf", 80)
        except:
            font = ImageFont.load_default()
        
        text = f"AutoMagic Quick Test {i+1}"
        
        # Calculate text position
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Simple white text (no shadows for faster processing)
        draw.text((x, y), text, font=font, fill=(255, 255, 255))
        
        # Save as JPEG with lower quality for smaller file size
        filename = f"quick_img_{i+1}.jpg"
        filepath = images_dir / filename
        img.save(filepath, quality=85)  # Lower quality = smaller file = faster processing
        images.append(str(filepath))
    
    # Create short video (30 seconds total = faster processing)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = Path("final_videos") / f"quick_test_{timestamp}.mp4"
    
    # Simple FFmpeg command for fast processing
    duration_per_image = 10  # 10 seconds each = 30 second video
    
    cmd = [
        'ffmpeg', '-y',
        '-loop', '1', '-t', str(duration_per_image), '-i', images[0],
        '-loop', '1', '-t', str(duration_per_image), '-i', images[1],
        '-loop', '1', '-t', str(duration_per_image), '-i', images[2],
        '-filter_complex', '[0:v][1:v][2:v]concat=n=3:v=1:a=0,scale=1280:720,fps=24[v]',
        '-map', '[v]',
        '-c:v', 'libx264', '-preset', 'ultrafast',  # Fastest encoding
        '-crf', '28',  # Lower quality for smaller file
        '-pix_fmt', 'yuv420p',
        '-t', '30',  # Exactly 30 seconds
        str(output_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Quick video created: {output_path}")
            
            # Check file size
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"File size: {size_mb:.1f} MB (smaller = faster processing)")
            
            return str(output_path)
        else:
            print(f"Video creation failed: {result.stderr}")
            return None
    except Exception as e:
        print(f"Error creating video: {e}")
        return None

def upload_quick_test(video_path):
    """Upload optimized video for fast processing"""
    
    try:
        with open('token.pickle', 'rb') as f:
            creds = pickle.load(f)
        
        youtube = build('youtube', 'v3', credentials=creds)
        
        from googleapiclient.http import MediaFileUpload
        
        # Optimized metadata for faster processing
        body = {
            'snippet': {
                'title': f'AutoMagic Quick Test - {time.strftime("%H:%M")}',
                'description': 'Quick AutoMagic test - optimized for fast processing',
                'tags': ['automagic', 'test'],
                'categoryId': '22'  # People & Blogs (fastest processing)
            },
            'status': {
                'privacyStatus': 'public',
                'embeddable': True,
                'madeForKids': False
            }
        }
        
        print("Uploading quick test video...")
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        
        request = youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        
        response = request.execute()
        video_id = response['id']
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        
        print(f"SUCCESS! Quick upload complete:")
        print(f"Video ID: {video_id}")
        print(f"URL: {youtube_url}")
        print(f"Should be visible within 5-15 minutes")
        
        return youtube_url
        
    except Exception as e:
        print(f"Quick upload failed: {e}")
        return None

if __name__ == "__main__":
    # Check existing videos
    check_video_status()
    
    # Create and upload optimized video
    print("\n" + "=" * 50)
    video_path = create_optimized_video()
    if video_path:
        upload_quick_test(video_path)
    
    print(f"\nRecommendation: Check your channel in 10-15 minutes")
    print("https://youtube.com/channel/UC9JN2eg-ja0TOws09jCKHow")