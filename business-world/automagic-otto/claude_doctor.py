#!/usr/bin/env python3
"""
Claude Doctor - Comprehensive AutoMagic System Diagnostic
"""

import os
import sys
import json
import pickle
from pathlib import Path
from datetime import datetime
import subprocess

def diagnostic_header():
    print("=" * 60)
    print("CLAUDE DOCTOR - AUTOMAGIC SYSTEM DIAGNOSTIC")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def check_environment():
    print("ENVIRONMENT CHECK")
    print("-" * 30)
    
    # Check current directory
    cwd = os.getcwd()
    print(f"Working Directory: {cwd}")
    
    # Check if this is the right directory
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
            print(f"✅ {dir_name}/: {file_count} files")
        else:
            print(f"❌ {dir_name}/: Missing")
    print()

def check_api_keys():
    print("🔑 API CONFIGURATION CHECK")
    print("-" * 30)
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check each API key
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
                print(f"✅ {desc}: {masked}")
            else:
                print(f"❌ {desc}: Not configured")
                
    except Exception as e:
        print(f"❌ Error loading environment: {e}")
    print()

def check_youtube_auth():
    print("🎥 YOUTUBE AUTHENTICATION CHECK")
    print("-" * 30)
    
    if os.path.exists('token.pickle'):
        try:
            with open('token.pickle', 'rb') as f:
                creds = pickle.load(f)
            
            # Check if credentials exist
            if hasattr(creds, 'token'):
                print("✅ YouTube token loaded")
                
                if hasattr(creds, 'expired'):
                    if creds.expired:
                        print("⚠️  Token expired (will auto-refresh)")
                    else:
                        print("✅ Token valid")
                        
                # Try to use the token
                try:
                    from googleapiclient.discovery import build
                    youtube = build('youtube', 'v3', credentials=creds)
                    print("✅ YouTube API connection successful")
                except Exception as e:
                    print(f"❌ YouTube API error: {e}")
            else:
                print("❌ Invalid token format")
                
        except Exception as e:
            print(f"❌ Token load error: {e}")
    else:
        print("❌ No YouTube authentication found")
    print()

def check_recent_videos():
    print("📹 RECENT VIDEO ANALYSIS")
    print("-" * 30)
    
    # Check final_videos directory
    video_dir = Path("final_videos")
    if video_dir.exists():
        video_files = list(video_dir.glob("*.mp4"))
        video_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        print(f"Total videos: {len(video_files)}")
        print("Most recent 5 videos:")
        
        for i, video in enumerate(video_files[:5]):
            mod_time = datetime.fromtimestamp(video.stat().st_mtime)
            size_mb = video.stat().st_size / (1024 * 1024)
            print(f"  {i+1}. {video.name}")
            print(f"     Created: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"     Size: {size_mb:.1f} MB")
            
            # Try to get video info with ffprobe
            try:
                result = subprocess.run([
                    'ffprobe', '-v', 'quiet', '-print_format', 'json',
                    '-show_format', str(video)
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    info = json.loads(result.stdout)
                    duration = float(info['format']['duration'])
                    print(f"     Duration: {duration:.1f} seconds")
                    
            except Exception as e:
                print(f"     Duration: Unable to check")
            print()
    else:
        print("❌ No final_videos directory found")
    print()

def check_upload_log():
    print("📤 UPLOAD HISTORY CHECK")
    print("-" * 30)
    
    if os.path.exists('uploaded_videos.log'):
        try:
            with open('uploaded_videos.log', 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            print(f"Total uploads logged: {len(lines)}")
            print("Recent uploads:")
            
            for i, line in enumerate(lines[-5:], 1):
                line = line.strip()
                if line:
                    print(f"  {len(lines)-5+i}. {line}")
                    
        except Exception as e:
            print(f"❌ Error reading upload log: {e}")
    else:
        print("❌ No upload log found")
    print()

def check_dependencies():
    print("📦 DEPENDENCIES CHECK")
    print("-" * 30)
    
    required_packages = [
        'openai',
        'google-api-python-client', 
        'python-dotenv',
        'Pillow',
        'requests'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}: Installed")
        except ImportError:
            print(f"❌ {package}: Missing")
    
    # Check FFmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            version_line = result.stdout.split('\\n')[0]
            print(f"✅ FFmpeg: {version_line}")
        else:
            print("❌ FFmpeg: Not working")
    except:
        print("❌ FFmpeg: Not found")
    print()

def system_recommendations():
    print("💡 SYSTEM RECOMMENDATIONS")
    print("-" * 30)
    
    recommendations = []
    
    # Check for common issues
    if not os.path.exists('.env'):
        recommendations.append("❗ Missing .env file - API keys not configured")
    
    if not os.path.exists('token.pickle'):
        recommendations.append("❗ YouTube authentication required")
    
    # Check recent activity
    video_dir = Path("final_videos")
    if video_dir.exists():
        recent_videos = [f for f in video_dir.glob("*.mp4") 
                        if (datetime.now().timestamp() - f.stat().st_mtime) < 3600]
        if not recent_videos:
            recommendations.append("ℹ️  No videos created in the last hour")
        else:
            recommendations.append(f"✅ {len(recent_videos)} video(s) created recently")
    
    # Check upload log
    if os.path.exists('uploaded_videos.log'):
        mod_time = datetime.fromtimestamp(os.path.getmtime('uploaded_videos.log'))
        time_since = datetime.now() - mod_time
        if time_since.total_seconds() < 3600:
            recommendations.append(f"✅ Recent upload activity ({time_since.seconds//60} minutes ago)")
        else:
            recommendations.append(f"ℹ️  Last upload was {time_since.seconds//3600} hours ago")
    
    if not recommendations:
        recommendations.append("✅ System appears to be functioning normally")
    
    for rec in recommendations:
        print(f"  {rec}")
    print()

def quick_test():
    print("🔬 QUICK FUNCTIONALITY TEST")
    print("-" * 30)
    
    try:
        # Test image generation
        from PIL import Image
        test_img = Image.new('RGB', (100, 100), (255, 0, 0))
        test_path = Path("generated_images") / "doctor_test.jpg"
        test_img.save(test_path)
        print("✅ Image generation: Working")
        test_path.unlink()  # Clean up
    except Exception as e:
        print(f"❌ Image generation: Failed - {e}")
    
    try:
        # Test environment loading
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment loading: Working")
    except Exception as e:
        print(f"❌ Environment loading: Failed - {e}")
    
    try:
        # Test YouTube API import
        from googleapiclient.discovery import build
        print("✅ YouTube API import: Working")
    except Exception as e:
        print(f"❌ YouTube API import: Failed - {e}")
    
    print()

def main():
    diagnostic_header()
    check_environment()
    check_api_keys()
    check_youtube_auth()
    check_recent_videos()
    check_upload_log()
    check_dependencies()
    quick_test()
    system_recommendations()
    
    print("=" * 60)
    print("🩺 DIAGNOSTIC COMPLETE")
    print("=" * 60)
    print()
    print("If you're experiencing issues:")
    print("1. Check the recommendations above")
    print("2. Ensure all APIs are properly configured")
    print("3. Verify YouTube authentication is working")
    print("4. Remember: YouTube videos can take 15min-2hrs to process")
    print()
    print("Channel URL: https://youtube.com/channel/UC9JN2eg-ja0TOws09jCKHow")

if __name__ == "__main__":
    main()