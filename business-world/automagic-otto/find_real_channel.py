#!/usr/bin/env python3
"""
Find Real Channel - Determine which channel videos are uploading to
"""

import requests
import re
import time

def get_channel_from_video(video_id):
    """Extract channel info from a YouTube video page"""
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # Look for channel ID in the page source
            channel_id_pattern = r'"channelId":"([^"]+)"'
            channel_id_match = re.search(channel_id_pattern, content)
            
            # Look for channel name
            channel_name_pattern = r'"author":"([^"]+)"'
            channel_name_match = re.search(channel_name_pattern, content)
            
            # Alternative channel name pattern
            if not channel_name_match:
                channel_name_pattern2 = r'"ownerChannelName":"([^"]+)"'
                channel_name_match = re.search(channel_name_pattern2, content)
            
            channel_id = channel_id_match.group(1) if channel_id_match else "Unknown"
            channel_name = channel_name_match.group(1) if channel_name_match else "Unknown"
            
            return channel_id, channel_name
        
        return None, None
        
    except Exception as e:
        return f"Error: {e}", None

def main():
    print("=" * 60)
    print("FINDING WHICH CHANNEL VIDEOS ARE UPLOADED TO")
    print("=" * 60)
    
    # Working video IDs (the ones that exist)
    working_videos = [
        ('rw7aZH5_6qI', 'Investigation test (just uploaded)'),
        ('LkT-ZPr0HDk', 'Quick test'),
        ('pFTTKr3qTCA', 'Public test')
    ]
    
    expected_channel_id = "UC9JN2eg-ja0TOws09jCKHow"
    expected_channel_url = f"https://youtube.com/channel/{expected_channel_id}"
    
    print(f"Expected Channel ID: {expected_channel_id}")
    print(f"Expected Channel URL: {expected_channel_url}")
    print()
    
    print("Checking where videos actually uploaded...")
    print()
    
    channels_found = set()
    
    for video_id, description in working_videos:
        print(f"Checking: {description}")
        print(f"Video ID: {video_id}")
        print(f"URL: https://www.youtube.com/watch?v={video_id}")
        
        channel_id, channel_name = get_channel_from_video(video_id)
        
        if channel_id and channel_id != "Unknown":
            print(f"Channel ID: {channel_id}")
            print(f"Channel Name: {channel_name}")
            print(f"Channel URL: https://youtube.com/channel/{channel_id}")
            
            channels_found.add((channel_id, channel_name))
            
            if channel_id == expected_channel_id:
                print("[SUCCESS] Video is on the CORRECT channel!")
            else:
                print("[PROBLEM] Video is on WRONG channel!")
                print(f"Expected: {expected_channel_id}")
                print(f"Actual: {channel_id}")
        else:
            print("[ERROR] Could not determine channel")
        
        print("-" * 40)
        time.sleep(2)  # Don't overwhelm YouTube
    
    print()
    print("SUMMARY:")
    print("=" * 40)
    
    if len(channels_found) == 1:
        channel_id, channel_name = list(channels_found)[0]
        print(f"All videos are uploading to: {channel_name}")
        print(f"Channel ID: {channel_id}")
        print(f"Channel URL: https://youtube.com/channel/{channel_id}")
        
        if channel_id == expected_channel_id:
            print()
            print("[DIAGNOSIS] Videos are on the correct channel!")
            print("Issue might be:")
            print("- Videos are unlisted/private")
            print("- Channel settings hiding them")
            print("- YouTube processing delays")
            print()
            print("SOLUTION: Check your channel directly:")
            print(f"https://youtube.com/channel/{channel_id}/videos")
        else:
            print()
            print("[DIAGNOSIS] Videos are uploading to the WRONG CHANNEL!")
            print("This explains why you don't see them on your target channel.")
            print()
            print("SOLUTION:")
            print("1. Re-authenticate YouTube with the correct account")
            print("2. Make sure you're signed into the right Google account")
            print("3. Check which account owns the target channel")
    else:
        print("Videos are uploading to multiple different channels!")
        print("This indicates an authentication problem.")
    
    print()
    print("Next steps:")
    print("1. Visit the actual channel URL where videos are uploading")
    print("2. Verify the account authentication")
    print("3. Re-authenticate if necessary")

if __name__ == "__main__":
    main()