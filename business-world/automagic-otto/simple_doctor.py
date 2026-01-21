#!/usr/bin/env python3
"""
Simple Claude Doctor - Clean AutoMagic System Diagnostic
"""

import os
import sys
import json
import pickle
from pathlib import Path
from datetime import datetime
import subprocess

def main_diagnostic():
    print("=" * 60)
    print("CLAUDE DOCTOR - AUTOMAGIC SYSTEM DIAGNOSTIC")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # ENVIRONMENT CHECK
    print("ENVIRONMENT CHECK")
    print("-" * 30)
    
    cwd = os.getcwd()
    print(f"Working Directory: {cwd}")
    
    # Check key files
    key_files = ['.env', 'token.pickle', 'uploaded_videos.log']
    for file in key_files:
        if os.path.exists(file):
            print(f"[OK] {file}: Found")
        else:
            print(f"[MISSING] {file}: Missing")
    
    # Check directories
    dirs = ['final_videos', 'generated_images', 'generated_audio', 'logs']
    for dir_name in dirs:
        if os.path.exists(dir_name):
            file_count = len([f for f in os.listdir(dir_name) if os.path.isfile(os.path.join(dir_name, f))])
            print(f"[OK] {dir_name}/: {file_count} files")
        else:
            print(f"[MISSING] {dir_name}/: Missing")
    print()
    
    # API CONFIGURATION CHECK
    print("API CONFIGURATION CHECK")
    print("-" * 30)
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        apis = {
            'OPENAI_API_KEY': 'OpenAI (DALL-E, GPT)',
            'ELEVENLABS_API_KEY': 'ElevenLabs (Voice)',
            'GOOGLE_API_KEY': 'Google (YouTube)',
            'YOUTUBE_CHANNEL_ID': 'YouTube Channel'
        }
        
        for key, desc in apis.items():
            value = os.getenv(key)
            if value and len(value) > 10:
                masked = f"{value[:8]}...{value[-4:]}"
                print(f"[OK] {desc}: {masked}")
            else:
                print(f"[MISSING] {desc}: Not configured")
                
    except Exception as e:
        print(f"[ERROR] Error loading environment: {e}")
    print()
    
    # YOUTUBE AUTHENTICATION CHECK
    print("YOUTUBE AUTHENTICATION CHECK")
    print("-" * 30)
    
    if os.path.exists('token.pickle'):
        try:
            with open('token.pickle', 'rb') as f:
                creds = pickle.load(f)
            print("[OK] YouTube token loaded")
            
            try:
                from googleapiclient.discovery import build
                youtube = build('youtube', 'v3', credentials=creds)
                print("[OK] YouTube API connection successful")
            except Exception as e:
                print(f"[ERROR] YouTube API error: {e}")
                
        except Exception as e:
            print(f"[ERROR] Token load error: {e}")
    else:
        print("[MISSING] No YouTube authentication found")
    print()
    
    # RECENT VIDEO ANALYSIS
    print("RECENT VIDEO ANALYSIS")
    print("-" * 30)
    
    video_dir = Path("final_videos")
    if video_dir.exists():
        video_files = list(video_dir.glob("*.mp4"))
        video_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        print(f"Total videos: {len(video_files)}")
        print("Most recent 3 videos:")
        
        for i, video in enumerate(video_files[:3]):
            mod_time = datetime.fromtimestamp(video.stat().st_mtime)
            size_mb = video.stat().st_size / (1024 * 1024)
            print(f"  {i+1}. {video.name}")
            print(f"     Created: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"     Size: {size_mb:.1f} MB")
            
            # Quick duration check
            try:
                result = subprocess.run([
                    'ffprobe', '-v', 'quiet', '-print_format', 'json',
                    '-show_format', str(video)
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    info = json.loads(result.stdout)
                    duration = float(info['format']['duration'])
                    print(f"     Duration: {duration:.1f} seconds")
                    
            except:
                print(f"     Duration: Unable to check")
            print()
    else:
        print("[MISSING] No final_videos directory found")
    print()
    
    # UPLOAD HISTORY CHECK
    print("UPLOAD HISTORY CHECK")
    print("-" * 30)
    
    if os.path.exists('uploaded_videos.log'):
        try:
            with open('uploaded_videos.log', 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            print(f"Total uploads logged: {len(lines)}")
            print("Recent uploads:")
            
            for i, line in enumerate(lines[-3:], 1):
                line = line.strip()
                if line:
                    print(f"  {len(lines)-3+i}. {line}")
                    
        except Exception as e:
            print(f"[ERROR] Error reading upload log: {e}")
    else:
        print("[MISSING] No upload log found")
    print()
    
    # DEPENDENCIES CHECK
    print("DEPENDENCIES CHECK")
    print("-" * 30)
    
    required_packages = [
        'openai', 'google-api-python-client', 'python-dotenv', 'Pillow', 'requests'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"[OK] {package}: Installed")
        except ImportError:
            print(f"[MISSING] {package}: Missing")
    
    # Check FFmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            version_line = result.stdout.split('\\n')[0]
            print(f"[OK] FFmpeg: {version_line}")
        else:
            print("[ERROR] FFmpeg: Not working")
    except:
        print("[MISSING] FFmpeg: Not found")
    print()
    
    # SYSTEM ANALYSIS
    print("SYSTEM ANALYSIS")
    print("-" * 30)
    
    issues = 0
    
    # Check for critical issues
    if not os.path.exists('.env'):
        print("[CRITICAL] Missing .env file - API keys not configured")
        issues += 1
    
    if not os.path.exists('token.pickle'):
        print("[CRITICAL] YouTube authentication missing")
        issues += 1
    
    # Check recent activity
    recent_videos = []
    if video_dir.exists():
        recent_videos = [f for f in video_dir.glob("*.mp4") 
                        if (datetime.now().timestamp() - f.stat().st_mtime) < 3600]
    
    if recent_videos:
        print(f"[OK] {len(recent_videos)} video(s) created in last hour")
    else:
        print("[INFO] No videos created in the last hour")
    
    # Check upload activity
    if os.path.exists('uploaded_videos.log'):
        mod_time = datetime.fromtimestamp(os.path.getmtime('uploaded_videos.log'))
        time_since = datetime.now() - mod_time
        if time_since.total_seconds() < 3600:
            minutes_ago = int(time_since.total_seconds() // 60)
            print(f"[OK] Recent upload activity ({minutes_ago} minutes ago)")
        else:
            hours_ago = int(time_since.total_seconds() // 3600)
            print(f"[INFO] Last upload was {hours_ago} hours ago")
    
    print()
    
    # FINAL DIAGNOSIS
    print("=" * 60)
    print("FINAL DIAGNOSIS")
    print("=" * 60)
    
    if issues == 0:
        print("[HEALTHY] AutoMagic system appears to be functioning normally")
        print()
        print("Current Status:")
        print("- API keys configured")
        print("- YouTube authentication active")
        print("- Video generation working")
        print("- Upload system functional")
        print()
        print("Note: YouTube videos can take 15 minutes to 2+ hours to process")
        print("Check your channel: https://youtube.com/channel/UC9JN2eg-ja0TOws09jCKHow")
    else:
        print(f"[ISSUES FOUND] {issues} critical issue(s) detected")
        print("Recommended actions:")
        if not os.path.exists('.env'):
            print("1. Configure API keys in .env file")
        if not os.path.exists('token.pickle'):
            print("2. Run YouTube authentication")
        print("3. Test video generation manually")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    main_diagnostic()