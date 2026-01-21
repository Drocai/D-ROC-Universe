#!/usr/bin/env python3
"""
Deep Investigation - Find out why videos aren't appearing
"""

import os
import pickle
from googleapiclient.discovery import build
import requests
from datetime import datetime

def investigate_uploads():
    print("=" * 60)
    print("DEEP INVESTIGATION - WHY NO VIDEOS APPEARING")
    print("=" * 60)
    
    # Get all recent video IDs we think we uploaded
    video_ids = [
        'LkT-ZPr0HDk',  # Most recent quick test
        'pFTTKr3qTCA',  # Public test
        'RopLZoIT8uo',  # Previous upload
        'InU4BDvmfRA',  # Earlier upload  
        'E2JVy5ojVwA'   # Original test
    ]
    
    print(f"Checking {len(video_ids)} supposedly uploaded videos...")
    print()
    
    # Load credentials
    try:
        with open('token.pickle', 'rb') as f:
            creds = pickle.load(f)
        
        youtube = build('youtube', 'v3', credentials=creds)
        
        # Check which channel we're authenticated as
        print("1. CHECKING AUTHENTICATED CHANNEL")
        print("-" * 40)
        try:
            channel_response = youtube.channels().list(part='snippet', mine=True).execute()
            
            if channel_response.get('items'):
                channel = channel_response['items'][0]
                auth_channel_id = channel['id']
                auth_channel_title = channel['snippet']['title']
                print(f"Authenticated as: {auth_channel_title}")
                print(f"Channel ID: {auth_channel_id}")
                
                expected_channel = "UC9JN2eg-ja0TOws09jCKHow"
                if auth_channel_id == expected_channel:
                    print("[OK] Correct channel authenticated")
                else:
                    print(f"[PROBLEM] Wrong channel! Expected: {expected_channel}")
                    print("This explains why videos aren't appearing!")
            else:
                print("[PROBLEM] No channel found for authenticated account")
        except Exception as e:
            print(f"[ERROR] Could not check authenticated channel: {e}")
        
        print()
        
        # Check if videos exist but are private/unlisted
        print("2. CHECKING VIDEO PRIVACY STATUS")
        print("-" * 40)
        
        for i, video_id in enumerate(video_ids, 1):
            print(f"Video {i}: {video_id}")
            print(f"URL: https://www.youtube.com/watch?v={video_id}")
            
            try:
                # Try to get video details
                response = youtube.videos().list(
                    part='snippet,status',
                    id=video_id
                ).execute()
                
                if response.get('items'):
                    video = response['items'][0]
                    title = video['snippet']['title']
                    privacy = video['status']['privacyStatus']
                    upload_status = video['status']['uploadStatus']
                    channel_id = video['snippet']['channelId']
                    
                    print(f"  Title: {title}")
                    print(f"  Privacy: {privacy}")
                    print(f"  Upload Status: {upload_status}")
                    print(f"  Channel: {channel_id}")
                    
                    if privacy != 'public':
                        print(f"  [PROBLEM] Video is {privacy}, not public!")
                    if upload_status != 'processed':
                        print(f"  [PROBLEM] Upload status: {upload_status}")
                    
                else:
                    print("  [NOT FOUND] Video does not exist")
                    
            except Exception as e:
                print(f"  [ERROR] {e}")
            
            print()
        
        # Check recent uploads on the channel
        print("3. CHECKING RECENT UPLOADS ON TARGET CHANNEL")
        print("-" * 40)
        
        try:
            # Get recent videos from the target channel
            search_response = youtube.search().list(
                part='snippet',
                channelId='UC9JN2eg-ja0TOws09jCKHow',
                type='video',
                order='date',
                maxResults=10
            ).execute()
            
            print("Recent videos on target channel:")
            if search_response.get('items'):
                for i, item in enumerate(search_response['items'], 1):
                    title = item['snippet']['title']
                    video_id = item['id']['videoId']
                    published = item['snippet']['publishedAt']
                    print(f"  {i}. {title}")
                    print(f"     ID: {video_id} | Published: {published}")
            else:
                print("  No recent videos found on target channel")
                
        except Exception as e:
            print(f"[ERROR] Could not check channel uploads: {e}")
        
        print()
        
    except Exception as e:
        print(f"[CRITICAL ERROR] {e}")

def test_public_upload():
    """Create and upload a test video with maximum visibility"""
    
    print("4. CREATING TEST UPLOAD WITH MAXIMUM VISIBILITY")
    print("-" * 40)
    
    # Create a simple test video
    from PIL import Image
    from pathlib import Path
    import subprocess
    import time
    
    try:
        # Create simple test image
        img = Image.new('RGB', (1280, 720), (255, 0, 0))  # Red background
        from PIL import ImageDraw, ImageFont
        
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 100)
        except:
            font = ImageFont.load_default()
        
        text = f"TEST {datetime.now().strftime('%H:%M')}"
        
        # Center text
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (1280 - text_width) // 2
        y = (720 - text_height) // 2
        
        draw.text((x, y), text, font=font, fill=(255, 255, 255))
        
        # Save test image
        test_img_path = Path("generated_images") / "test_investigation.jpg"
        img.save(test_img_path, quality=95)
        
        # Create test video
        test_video_path = Path("final_videos") / f"investigation_test_{int(time.time())}.mp4"
        
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1', '-t', '15', '-i', str(test_img_path),
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-r', '30',
            str(test_video_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[ERROR] Failed to create test video: {result.stderr}")
            return None
        
        print(f"Test video created: {test_video_path}")
        
        # Upload with maximum public settings
        with open('token.pickle', 'rb') as f:
            creds = pickle.load(f)
        
        youtube = build('youtube', 'v3', credentials=creds)
        
        from googleapiclient.http import MediaFileUpload
        
        # Explicit public settings
        body = {
            'snippet': {
                'title': f'INVESTIGATION TEST - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                'description': f'''DEEP INVESTIGATION TEST VIDEO

This video is a test to determine why AutoMagic uploads are not appearing on the channel.

Upload Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Purpose: Channel visibility investigation
Status: Should be PUBLIC and VISIBLE

If you can see this video, the upload system is working.
If not, there is a configuration issue.

#test #investigation #automagic''',
                'tags': ['test', 'investigation', 'automagic', 'visibility'],
                'categoryId': '22',  # People & Blogs
                'defaultLanguage': 'en'
            },
            'status': {
                'privacyStatus': 'public',  # EXPLICITLY PUBLIC
                'embeddable': True,
                'license': 'youtube',
                'publicStatsViewable': True,
                'madeForKids': False,
                'selfDeclaredMadeForKids': False
            }
        }
        
        print("Uploading test video with explicit public settings...")
        
        media = MediaFileUpload(str(test_video_path), chunksize=-1, resumable=True)
        
        request = youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        
        response = request.execute()
        video_id = response['id']
        
        print(f"[SUCCESS] Test video uploaded!")
        print(f"Video ID: {video_id}")
        print(f"URL: https://www.youtube.com/watch?v={video_id}")
        
        # Immediately check the upload
        check_response = youtube.videos().list(
            part='snippet,status',
            id=video_id
        ).execute()
        
        if check_response.get('items'):
            video_info = check_response['items'][0]
            status = video_info['status']
            print(f"Privacy Status: {status.get('privacyStatus')}")
            print(f"Upload Status: {status.get('uploadStatus')}")
            print(f"Channel ID: {video_info['snippet']['channelId']}")
        
        return video_id
        
    except Exception as e:
        print(f"[ERROR] Test upload failed: {e}")
        return None

def main():
    investigate_uploads()
    print()
    test_video_id = test_public_upload()
    
    print()
    print("=" * 60)
    print("INVESTIGATION SUMMARY")
    print("=" * 60)
    
    print("Key things to check:")
    print("1. Are we uploading to the correct channel?")
    print("2. Are videos being set to private/unlisted by mistake?")
    print("3. Are videos being processed but rejected?")
    print("4. Is there an authentication scope issue?")
    print()
    
    if test_video_id:
        print(f"Test video uploaded: https://www.youtube.com/watch?v={test_video_id}")
        print("Check if this test video appears on your channel within 10 minutes.")
        print("If it doesn't appear, the issue is confirmed.")
    
    print()
    print("Target Channel: https://youtube.com/channel/UC9JN2eg-ja0TOws09jCKHow")
    print("Check manually to see what videos are actually visible.")

if __name__ == "__main__":
    main()