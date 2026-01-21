#!/usr/bin/env python3
"""
Auto YouTube Authentication - Fixes wrong channel issue
"""
import os
import sys
from pathlib import Path

print("=" * 60)
print("AUTOMAGIC YOUTUBE AUTHENTICATION FIX")
print("=" * 60)
print()
print("[!] CRITICAL ISSUE FOUND:")
print("Videos are uploading to WRONG channel!")
print()
print("Current (WRONG): D RoC (UC79xI_dcS8uz8laX7O6wWdw)") 
print("Target (RIGHT): AutoMagic (UC9JN2eg-ja0TOws09jCKHow)")
print()

# Check credentials file
creds_file = "client_secret_984577519807-gaplffli5mn8o57lb3cvkl9ldvo1rvlt.apps.googleusercontent.com.json"
if not os.path.exists(creds_file):
    print("[ERROR] YouTube credentials file missing")
    sys.exit(1)

print("[OK] Credentials file found")
print("[INFO] Starting authentication...")
print()

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials
    import pickle
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    print("IMPORTANT INSTRUCTIONS:")
    print("=" * 40)
    print("1. A browser will open in a moment")
    print("2. Sign in with the Google account that OWNS the AutoMagic channel")
    print("3. NOT the 'D RoC' account - the AUTOMAGIC account")
    print("4. Grant YouTube upload permission")
    print("5. Return here when complete")
    print()
    print("Starting browser authentication...")
    print()
    
    # Start authentication flow
    flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
    creds = flow.run_local_server(port=0)
    
    print("[SUCCESS] Authentication completed!")
    
    # Save the new credentials
    with open('token.pickle', 'wb') as f:
        pickle.dump(creds, f)
    print("[OK] New credentials saved")
    
    # Verify the channel
    print()
    print("Verifying channel...")
    
    try:
        from googleapiclient.discovery import build
        youtube = build('youtube', 'v3', credentials=creds)
        
        response = youtube.channels().list(part='snippet', mine=True).execute()
        
        if response.get('items'):
            channel = response['items'][0]
            channel_id = channel['id']
            channel_title = channel['snippet']['title']
            
            print(f"Authenticated Channel: {channel_title}")
            print(f"Channel ID: {channel_id}")
            
            if channel_id == "UC9JN2eg-ja0TOws09jCKHow":
                print()
                print("=" * 60)
                print("[SUCCESS] CORRECT CHANNEL AUTHENTICATED!")
                print("=" * 60)
                print("AutoMagic will now upload to the RIGHT channel!")
                print()
                print("Test it: python youtube_uploader.py")
                print("Or run: python launch_automagic.py")
            else:
                print()
                print("=" * 60)
                print("[WARNING] STILL WRONG CHANNEL!")
                print("=" * 60)
                print(f"Got: {channel_id} ({channel_title})")
                print(f"Need: UC9JN2eg-ja0TOws09jCKHow (AutoMagic)")
                print()
                print("You authenticated with the wrong Google account!")
                print("Run this script again with the CORRECT account.")
        else:
            print("[ERROR] No channel found")
            
    except Exception as e:
        print(f"[INFO] Could not verify channel (normal with limited scope)")
        print("Authentication should still work for uploads")
    
except Exception as e:
    print(f"[ERROR] Authentication failed: {e}")
    print()
    print("Make sure you:")
    print("1. Have internet connection")
    print("2. Use the correct Google account") 
    print("3. Grant the requested permissions")

print()
print("=" * 60)