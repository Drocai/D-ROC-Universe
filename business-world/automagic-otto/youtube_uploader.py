#!/usr/bin/env python3
"""
Simple YouTube uploader for AutoMagic
"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime
import json

logger = logging.getLogger('YouTubeUploader')

def upload_to_youtube(video_path, title, description=None):
    """Upload video to YouTube using Google API"""
    
    logger.info(f"🎯 Starting YouTube upload: {title}")
    
    try:
        # Import Google API libraries
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        from googleapiclient.http import MediaFileUpload
        
        # YouTube API scope
        SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
        
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Get credentials file path
        creds_file = os.getenv('GOOGLE_API_CREDENTIALS_FILE')
        if not creds_file:
            logger.error("❌ No GOOGLE_API_CREDENTIALS_FILE found in .env")
            return False
        
        # Check if credentials file exists
        if not os.path.exists(creds_file):
            logger.error(f"❌ Credentials file not found: {creds_file}")
            return False
        
        # Check for existing token
        token_path = 'youtube_token.json'
        creds = None
        
        if os.path.exists(token_path):
            try:
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
                logger.info("✓ Loaded existing YouTube token")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load existing token: {e}")
        
        # If no valid credentials, run OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info("✓ Refreshed YouTube token")
                except Exception as e:
                    logger.warning(f"⚠️ Token refresh failed: {e}")
                    creds = None
            
            if not creds:
                logger.info("🔐 Starting YouTube OAuth authentication...")
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                    logger.info("✓ YouTube authentication successful")
                except Exception as e:
                    logger.error(f"❌ YouTube authentication failed: {e}")
                    return False
            
            # Save credentials for next time
            try:
                with open(token_path, 'w') as f:
                    f.write(creds.to_json())
                logger.info("✓ Saved YouTube token for future use")
            except Exception as e:
                logger.warning(f"⚠️ Failed to save token: {e}")
        
        # Build YouTube service
        try:
            youtube = build('youtube', 'v3', credentials=creds)
            logger.info("✓ YouTube API service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize YouTube service: {e}")
            return False
        
        # Prepare video metadata
        if not description:
            description = f"Automated video created by AutoMagic on {datetime.now().strftime('%Y-%m-%d')}"
        
        tags = ['AutoMagic', 'AI Generated', 'Educational', 'Daily Content']
        
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': '22'  # People & Blogs category
            },
            'status': {
                'privacyStatus': 'public'  # Change to 'private' or 'unlisted' if needed
            }
        }
        
        # Create media upload object
        try:
            media = MediaFileUpload(
                video_path,
                chunksize=-1,
                resumable=True,
                mimetype='video/mp4'
            )
            logger.info(f"✓ Prepared video file for upload: {video_path}")
        except Exception as e:
            logger.error(f"❌ Failed to prepare video file: {e}")
            return False
        
        # Upload video
        logger.info("🚀 Uploading to YouTube...")
        try:
            insert_request = youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            # Execute upload with progress tracking
            response = None
            while response is None:
                try:
                    status, response = insert_request.next_chunk()
                    if status:
                        progress = int(status.progress() * 100)
                        logger.info(f"📊 Upload progress: {progress}%")
                except HttpError as e:
                    if e.resp.status in [500, 502, 503, 504]:
                        # Recoverable error, retry
                        logger.warning(f"⚠️ Recoverable error {e.resp.status}, retrying...")
                        continue
                    else:
                        raise
            
            # Check upload result
            if response and 'id' in response:
                video_id = response['id']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                
                logger.info("🎉 SUCCESS! Video uploaded to YouTube!")
                logger.info(f"📺 Video ID: {video_id}")
                logger.info(f"🔗 Video URL: {video_url}")
                
                # Log successful upload
                log_upload_success(title, video_id, video_url)
                
                return True
            else:
                logger.error("❌ Upload failed - no video ID returned")
                return False
                
        except HttpError as e:
            logger.error(f"❌ YouTube API error: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Upload error: {e}")
            return False
            
    except ImportError as e:
        logger.error(f"❌ Missing required libraries: {e}")
        logger.error("   Install with: pip install google-api-python-client google-auth-oauthlib")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during YouTube upload: {e}")
        return False

def log_upload_success(title, video_id, video_url):
    """Log successful upload to file"""
    try:
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'title': title,
            'video_id': video_id,
            'video_url': video_url
        }
        
        # Append to uploaded videos log
        with open('uploaded_videos.log', 'a', encoding='utf-8') as f:
            f.write(f"{title}\n")
        
        # Also save detailed JSON log
        uploads_file = 'youtube_uploads.json'
        uploads = []
        
        if os.path.exists(uploads_file):
            try:
                with open(uploads_file, 'r', encoding='utf-8') as f:
                    uploads = json.load(f)
            except:
                uploads = []
        
        uploads.append(log_entry)
        
        with open(uploads_file, 'w', encoding='utf-8') as f:
            json.dump(uploads, f, indent=2, ensure_ascii=False)
        
        logger.info("✓ Upload logged successfully")
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to log upload: {e}")

def test_youtube_upload():
    """Test YouTube upload functionality"""
    logger.info("🧪 Testing YouTube upload functionality...")
    
    # Check if we have a test video
    test_videos = [
        'final_videos/automagic_video_20251021_051132.mp4',
        'final_videos/test_video.mp4'
    ]
    
    test_video = None
    for video in test_videos:
        if os.path.exists(video):
            test_video = video
            break
    
    if not test_video:
        logger.error("❌ No test video found for upload")
        return False
    
    # Test upload
    title = f"AutoMagic Test Upload - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    description = "This is a test upload from the AutoMagic system to verify YouTube integration is working."
    
    return upload_to_youtube(test_video, title, description)

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Test upload
    success = test_youtube_upload()
    
    if success:
        print("\n🎉 YouTube upload test SUCCESSFUL!")
        print("   Your AutoMagic system can now upload to YouTube!")
    else:
        print("\n❌ YouTube upload test FAILED")
        print("   Check the logs above for details")
    
    input("\nPress Enter to exit...")