#!/usr/bin/env python3
"""
Test Public Upload - Create and upload a video that's definitely public
"""

import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from pathlib import Path
import time

def create_test_upload():
    """Upload the most recent video with guaranteed public settings"""
    
    # Find the most recent video
    video_dir = Path("final_videos")
    video_files = [f for f in video_dir.glob("*.mp4") if f.is_file()]
    
    if not video_files:
        print("No video files found!")
        return
    
    # Get the most recent video
    latest_video = max(video_files, key=lambda f: f.stat().st_mtime)
    print(f"Uploading: {latest_video}")
    
    try:
        # Load YouTube credentials
        with open('token.pickle', 'rb') as f:
            creds = pickle.load(f)
        
        youtube = build('youtube', 'v3', credentials=creds)
        
        # Create upload metadata with explicit public settings
        body = {
            'snippet': {
                'title': f'AutoMagic Public Test - {time.strftime("%Y-%m-%d %H:%M")}',
                'description': '''🚀 AutoMagic AI Video Generator Test

This video was automatically created and uploaded by AutoMagic AI system.

Features:
✅ Automated content generation
✅ AI-powered video assembly  
✅ Trending topic detection
✅ Smart YouTube integration

Subscribe for more AI-generated content!

#AutoMagic #AI #Automation #Technology''',
                'tags': [
                    'AutoMagic',
                    'AI',
                    'automation', 
                    'technology',
                    'artificial intelligence',
                    'video generation',
                    'trending'
                ],
                'categoryId': '28',  # Science & Technology
                'defaultLanguage': 'en',
                'defaultAudioLanguage': 'en'
            },
            'status': {
                'privacyStatus': 'public',  # Explicitly public
                'embeddable': True,
                'license': 'youtube',
                'publicStatsViewable': True,
                'madeForKids': False
            }
        }
        
        # Upload the video
        print("Starting public upload...")
        media = MediaFileUpload(str(latest_video), chunksize=-1, resumable=True)
        
        request = youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        
        response = request.execute()
        video_id = response['id']
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        
        print(f"SUCCESS!")
        print(f"Video ID: {video_id}")
        print(f"URL: {youtube_url}")
        print(f"Privacy: {response.get('status', {}).get('privacyStatus', 'unknown')}")
        
        # Log the upload
        with open('uploaded_videos.log', 'a', encoding='utf-8') as f:
            f.write(f"AutoMagic Public Test - {time.strftime('%Y-%m-%d %H:%M')}\\n")
        
        # Double-check the upload status
        time.sleep(2)
        
        check_response = youtube.videos().list(
            part='status,snippet',
            id=video_id
        ).execute()
        
        if check_response.get('items'):
            video_info = check_response['items'][0]
            status = video_info['status']
            print(f"\\nUpload Verification:")
            print(f"   Privacy Status: {status.get('privacyStatus')}")
            print(f"   Upload Status: {status.get('uploadStatus')}")
            print(f"   Processing Status: {status.get('processingStatus', 'N/A')}")
            print(f"   Embeddable: {status.get('embeddable')}")
            
        return youtube_url
        
    except Exception as e:
        print(f"Upload failed: {e}")
        return None

if __name__ == "__main__":
    print("AutoMagic Public Upload Test")
    print("=" * 50)
    result = create_test_upload()
    
    if result:
        print(f"\\nVideo should be visible at: {result}")
        print("\\nIf the video doesn't appear immediately:")
        print("   - YouTube may still be processing it")
        print("   - Check your channel's Videos tab")
        print("   - Processing can take 1-15 minutes for HD videos")
    else:
        print("\\nUpload failed - check the error above")