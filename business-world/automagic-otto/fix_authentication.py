#!/usr/bin/env python3
"""
Fix Authentication - Re-authenticate with correct YouTube channel
"""

import os
import pickle
from pathlib import Path

def fix_youtube_auth():
    print("=" * 60)
    print("FIXING YOUTUBE CHANNEL AUTHENTICATION")
    print("=" * 60)
    
    print("PROBLEM IDENTIFIED:")
    print("Videos are uploading to the wrong channel!")
    print()
    print("Current uploads go to: D RoC (UC79xI_dcS8uz8laX7O6wWdw)")
    print("Target channel: AutoMagic (UC9JN2eg-ja0TOws09jCKHow)")
    print()
    
    # Backup current token
    if os.path.exists('token.pickle'):
        print("Backing up current token...")
        backup_path = f"token_backup_{int(__import__('time').time())}.pickle"
        __import__('shutil').copy2('token.pickle', backup_path)
        print(f"Current token backed up to: {backup_path}")
        
        # Remove current token
        os.remove('token.pickle')
        print("Current token removed")
    else:
        print("No existing token found")
    
    print()
    print("AUTHENTICATION STEPS:")
    print("=" * 40)
    print("1. Make sure you're signed into the CORRECT Google account")
    print("   - The account that owns the AutoMagic channel")
    print("   - Channel: https://youtube.com/channel/UC9JN2eg-ja0TOws09jCKHow")
    print()
    print("2. Run the guided authentication:")
    print("   python guided_youtube_auth.py")
    print()
    print("3. When the browser opens:")
    print("   - Check which Google account is selected")
    print("   - Switch accounts if necessary")
    print("   - Grant permission for YouTube upload")
    print()
    print("4. Verify the correct channel:")
    print("   - After authentication, check the channel ID")
    print("   - It should be: UC9JN2eg-ja0TOws09jCKHow")
    print()
    
    print("IMPORTANT:")
    print("- Sign out of all Google accounts in your browser first")
    print("- Sign in ONLY to the account that owns the AutoMagic channel")
    print("- Double-check the channel URL matches the target")
    print()
    
    response = input("Ready to start re-authentication? (yes/no): ").strip().lower()
    
    if response == 'yes':
        print()
        print("Starting guided authentication...")
        
        try:
            # Import and run the guided auth
            import subprocess
            result = subprocess.run(['python', 'guided_youtube_auth.py'], 
                                  capture_output=False, text=True)
            
            if result.returncode == 0:
                print("Authentication completed!")
                
                # Test the new authentication
                print("Testing new authentication...")
                test_new_auth()
            else:
                print("Authentication may have failed. Check the output above.")
                
        except Exception as e:
            print(f"Error running authentication: {e}")
            print("Please run manually: python guided_youtube_auth.py")
    else:
        print("Authentication cancelled.")
        print("Run when ready: python guided_youtube_auth.py")

def test_new_auth():
    """Test the new authentication to verify correct channel"""
    
    print()
    print("TESTING NEW AUTHENTICATION")
    print("=" * 40)
    
    try:
        if not os.path.exists('token.pickle'):
            print("No token found - authentication may have failed")
            return
        
        from googleapiclient.discovery import build
        
        with open('token.pickle', 'rb') as f:
            creds = pickle.load(f)
        
        youtube = build('youtube', 'v3', credentials=creds)
        
        # Get channel info
        try:
            response = youtube.channels().list(part='snippet', mine=True).execute()
            
            if response.get('items'):
                channel = response['items'][0]
                channel_id = channel['id']
                channel_title = channel['snippet']['title']
                
                print(f"Authenticated as: {channel_title}")
                print(f"Channel ID: {channel_id}")
                print(f"Channel URL: https://youtube.com/channel/{channel_id}")
                
                expected_id = "UC9JN2eg-ja0TOws09jCKHow"
                if channel_id == expected_id:
                    print()
                    print("[SUCCESS] Correct channel authenticated!")
                    print("AutoMagic will now upload to the right channel.")
                else:
                    print()
                    print("[WRONG CHANNEL] Still authenticated to wrong account!")
                    print(f"Expected: {expected_id}")
                    print(f"Got: {channel_id}")
                    print("Please try authentication again with correct account.")
            else:
                print("No channel found for authenticated account")
                
        except Exception as e:
            print(f"Could not verify channel due to API scope: {e}")
            print("This is normal - the authentication should still work for uploads")
        
    except Exception as e:
        print(f"Error testing authentication: {e}")

if __name__ == "__main__":
    fix_youtube_auth()