#!/usr/bin/env python3
"""
Verify Channel Fix - Test if we're now on the right channel
"""

import os
import pickle
from pathlib import Path
from datetime import datetime

print("=" * 60)
print("VERIFYING CHANNEL AUTHENTICATION")
print("=" * 60)
print()

# Create a simple test video
from PIL import Image, ImageDraw, ImageFont
import subprocess
import time

# Create test image
print("Creating test video...")
img = Image.new('RGB', (1280, 720), (0, 255, 0))  # Green = success
draw = ImageDraw.Draw(img)

try:
    font = ImageFont.truetype("arial.ttf", 60)
except:
    font = ImageFont.load_default()

text = f"CHANNEL FIX TEST {datetime.now().strftime('%H:%M')}"
bbox = draw.textbbox((0, 0), text, font=font)
x = (1280 - bbox[2] + bbox[0]) // 2
y = (720 - bbox[3] + bbox[1]) // 2
draw.text((x, y), text, font=font, fill=(255, 255, 255))

# Save image
test_img = Path("generated_images") / "channel_fix_test.jpg"
img.save(test_img)

# Create video
test_video = Path("final_videos") / f"channel_fix_test_{int(time.time())}.mp4"
cmd = [
    'ffmpeg', '-y',
    '-loop', '1', '-t', '10', '-i', str(test_img),
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
    str(test_video)
]

result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print(f"[ERROR] Failed to create test video: {result.stderr}")
    exit(1)

print(f"[OK] Test video created: {test_video.name}")
print()

# Upload to YouTube
print("Uploading test video...")

try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    
    with open('token.pickle', 'rb') as f:
        creds = pickle.load(f)
    
    youtube = build('youtube', 'v3', credentials=creds)
    
    body = {
        'snippet': {
            'title': f'CHANNEL FIX VERIFICATION - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
            'description': f'''This test verifies AutoMagic is uploading to the correct channel.

Test Time: {datetime.now()}
Expected Channel: AutoMagic (UC9JN2eg-ja0TOws09jCKHow)

If this video appears on the AutoMagic channel, the fix worked!''',
            'tags': ['test', 'verification', 'automagic'],
            'categoryId': '22'
        },
        'status': {
            'privacyStatus': 'public',
            'embeddable': True,
            'madeForKids': False
        }
    }
    
    media = MediaFileUpload(str(test_video), chunksize=-1, resumable=True)
    
    request = youtube.videos().insert(
        part='snippet,status',
        body=body,
        media_body=media
    )
    
    response = request.execute()
    video_id = response['id']
    
    print("=" * 60)
    print("[SUCCESS] TEST VIDEO UPLOADED!")
    print("=" * 60)
    print(f"Video ID: {video_id}")
    print(f"URL: https://www.youtube.com/watch?v={video_id}")
    print()
    
    # Now check which channel it went to
    print("Checking which channel received the video...")
    
    import requests
    import re
    time.sleep(3)  # Give YouTube a moment
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        content = response.text
        
        # Extract channel ID
        channel_id_pattern = r'"channelId":"([^"]+)"'
        channel_id_match = re.search(channel_id_pattern, content)
        
        if channel_id_match:
            actual_channel_id = channel_id_match.group(1)
            expected_channel_id = "UC9JN2eg-ja0TOws09jCKHow"
            
            print(f"Video uploaded to channel: {actual_channel_id}")
            
            if actual_channel_id == expected_channel_id:
                print()
                print("=" * 60)
                print("[SUCCESS] CHANNEL FIX CONFIRMED!")
                print("=" * 60)
                print("Videos are NOW uploading to the CORRECT AutoMagic channel!")
                print("Channel URL: https://youtube.com/channel/UC9JN2eg-ja0TOws09jCKHow")
                print()
                print("The AutoMagic system is now fully operational!")
                print("Run: python launch_automagic.py to create content")
            else:
                print()
                print("[WARNING] Still uploading to wrong channel!")
                print(f"Expected: {expected_channel_id}")
                print(f"Got: {actual_channel_id}")
                print()
                print("The authentication may not have switched accounts properly.")
                print("Try signing out of ALL Google accounts and re-authenticating.")
    else:
        print("[INFO] Could not immediately verify channel")
        print("Check the video manually in a few minutes")
    
    # Update upload log
    with open('uploaded_videos.log', 'a', encoding='utf-8') as f:
        f.write(f"Channel Fix Test - {datetime.now().strftime('%Y-%m-%d %H:%M')}\\n")
    
except Exception as e:
    print(f"[ERROR] Upload failed: {e}")

print()
print("Check your channel in 5-10 minutes:")
print("https://youtube.com/channel/UC9JN2eg-ja0TOws09jCKHow")
print()
print("=" * 60)