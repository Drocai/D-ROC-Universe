#!/usr/bin/env python3
"""
Direct Video Check - Test if uploaded videos actually exist
"""

import requests
import time

def check_video_exists(video_id):
    """Check if a YouTube video exists by trying to access it"""
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    try:
        # Simple request to see if video exists
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            # Check if it's actually a video page or error page
            content = response.text.lower()
            
            if "video unavailable" in content:
                return "unavailable"
            elif "private video" in content:
                return "private"
            elif "this video has been removed" in content:
                return "removed"
            elif "video" in content and "watch" in content:
                return "exists"
            else:
                return "unknown"
        else:
            return "not_found"
            
    except Exception as e:
        return f"error: {e}"

def main():
    print("=" * 60)
    print("DIRECT VIDEO EXISTENCE CHECK")
    print("=" * 60)
    
    # All video IDs we think we uploaded
    video_ids = [
        ('rw7aZH5_6qI', 'Investigation test (just uploaded)'),
        ('LkT-ZPr0HDk', 'Quick test from earlier'),
        ('pFTTKr3qTCA', 'Public test'),
        ('RopLZoIT8uo', 'Previous upload'),
        ('InU4BDvmfRA', 'Earlier upload'),
        ('E2JVy5ojVwA', 'Original test')
    ]
    
    print("Checking if videos actually exist on YouTube...")
    print()
    
    for video_id, description in video_ids:
        print(f"Testing: {description}")
        print(f"ID: {video_id}")
        print(f"URL: https://www.youtube.com/watch?v={video_id}")
        
        status = check_video_exists(video_id)
        
        print(f"Status: {status}")
        
        if status == "exists":
            print("[SUCCESS] Video exists and is accessible!")
        elif status == "private":
            print("[ISSUE] Video exists but is private")
        elif status == "unavailable":
            print("[ISSUE] Video is unavailable")
        elif status == "removed":
            print("[ISSUE] Video was removed")
        elif status == "not_found":
            print("[PROBLEM] Video does not exist")
        else:
            print(f"[UNCLEAR] Status unclear: {status}")
        
        print("-" * 40)
        time.sleep(1)  # Don't overwhelm YouTube
    
    print()
    print("DIAGNOSIS:")
    print("If videos show as 'exists' but aren't on your channel:")
    print("- They may be uploading to wrong account")
    print("- They may be set to unlisted/private")
    print("- Authentication may be for different channel")
    print()
    print("If videos show as 'not_found':")
    print("- Upload process is actually failing")
    print("- Video IDs are invalid")
    print("- Videos are being immediately removed")

if __name__ == "__main__":
    main()