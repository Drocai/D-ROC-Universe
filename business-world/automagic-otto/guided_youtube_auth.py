#!/usr/bin/env python3
"""
Guided YouTube Authentication for AutoMagic
This will walk you through the authentication step by step
"""
import os
import sys
import webbrowser
from pathlib import Path

print("AutoMagic YouTube Authentication Guide")
print("=" * 50)
print()

# Step 1: Check what we have
print("STEP 1: Checking your system...")
print("-" * 30)

# Check credentials file
creds_file = "client_secret_984577519807-gaplffli5mn8o57lb3cvkl9ldvo1rvlt.apps.googleusercontent.com.json"
if os.path.exists(creds_file):
    print("[OK] YouTube credentials file found")
else:
    print("✗ YouTube credentials file missing")
    print("  This is required for authentication")
    sys.exit(1)

# Check existing token
if os.path.exists('token.pickle'):
    print("✓ Existing authentication token found")
    print("  Your system may already be authenticated")
else:
    print("- No existing token found")
    print("  We'll create a new one")

print()
print("STEP 2: Your YouTube Channel")
print("-" * 30)
channel_url = "https://youtube.com/channel/UC9JN2eg-ja0TOws09jCKHow"
print(f"Your AutoMagic channel: {channel_url}")
print()
print("IMPORTANT: Remember which Google account you use for this channel!")
print("You'll need to use the SAME account for authentication.")
print()

# Ask user if they want to continue
print("STEP 3: Ready to Authenticate?")
print("-" * 30)
print("When you're ready, I'll start the authentication process.")
print("A browser window will open asking you to sign in to Google.")
print()
print("You should:")
print("1. Sign in with the Google account that owns your YouTube channel")
print("2. Grant permission for AutoMagic to upload videos")
print("3. The browser will show a success message")
print()

response = input("Ready to start? Type 'yes' to continue: ").strip().lower()

if response != 'yes':
    print("Authentication cancelled. Run this script again when ready.")
    sys.exit(0)

print()
print("STEP 4: Starting Authentication...")
print("-" * 30)

try:
    # Import required libraries
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    print("✓ Google API libraries loaded")
    
    # Load existing credentials if available
    creds = None
    if os.path.exists('token.pickle'):
        try:
            import pickle
            with open('token.pickle', 'rb') as f:
                creds = pickle.load(f)
            print("✓ Loaded existing credentials")
        except Exception as e:
            print(f"- Could not load existing credentials: {e}")
    
    # Check if credentials are valid
    if creds and creds.valid:
        print("🎉 SUCCESS! You're already authenticated!")
        print("Your AutoMagic system can upload to YouTube right now.")
        print()
        print("Try running a test upload to confirm everything works.")
    else:
        # Need to authenticate
        if creds and creds.expired and creds.refresh_token:
            print("- Credentials expired, trying to refresh...")
            try:
                creds.refresh(Request())
                print("✓ Credentials refreshed successfully!")
            except Exception as e:
                print(f"- Refresh failed: {e}")
                creds = None
        
        if not creds:
            print()
            print("🔐 BROWSER AUTHENTICATION REQUIRED")
            print("=" * 40)
            print("A browser window will open shortly...")
            print("Please:")
            print("1. Sign in with your Google account")
            print("2. Click 'Allow' to grant YouTube upload permission")
            print("3. Return here when done")
            print()
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
                creds = flow.run_local_server(port=0)
                
                print("🎉 AUTHENTICATION SUCCESSFUL!")
                print()
                
                # Save credentials
                import pickle
                with open('token.pickle', 'wb') as f:
                    pickle.dump(creds, f)
                print("✓ Authentication saved for future use")
                
            except Exception as e:
                print(f"[ERROR] Authentication failed: {e}")
                print()
                print("Common issues:")
                print("- Make sure you're using the correct Google account")
                print("- Check that your YouTube channel exists")
                print("- Ensure you have internet connection")
                sys.exit(1)
    
    print()
    print("🎯 FINAL VERIFICATION")
    print("=" * 40)
    
    # Test the credentials by accessing YouTube API
    try:
        from googleapiclient.discovery import build
        youtube = build('youtube', 'v3', credentials=creds)
        
        # Try to get channel info
        response = youtube.channels().list(part='snippet', mine=True).execute()
        
        if response.get('items'):
            channel = response['items'][0]
            channel_title = channel['snippet']['title']
            print(f"✓ Connected to YouTube channel: {channel_title}")
            print("✓ AutoMagic can now upload videos automatically!")
        else:
            print("⚠️ Connected to Google, but no YouTube channel found")
            print("  Make sure you have a YouTube channel set up")
    
    except Exception as e:
        print(f"⚠️ Could not verify YouTube access: {e}")
        print("  Authentication may still work for uploads")
    
    print()
    print("🚀 SETUP COMPLETE!")
    print("=" * 40)
    print("Your AutoMagic system is now ready to upload to YouTube!")
    print()
    print("Next steps:")
    print("1. Test upload: python youtube_uploader.py")
    print("2. Run full AutoMagic: python launch_automagic.py")
    print("3. Set up daily automation if desired")
    
except ImportError as e:
    print(f"❌ Missing required libraries: {e}")
    print("Install with: pip install google-api-python-client google-auth-oauthlib")
except Exception as e:
    print(f"❌ Unexpected error: {e}")

print()
input("Press Enter to exit...")