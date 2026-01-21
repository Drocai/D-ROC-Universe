# core/pipelines/youtube_uploader.py - Handles the YouTube upload process
from ..auth import get_youtube_service
from googleapiclient.http import MediaFileUpload

def upload_to_youtube(video_path, title, description, tags):
    """Uploads a video file to YouTube with metadata."""
    print(f"🚀 Uploading '{title}' to YouTube...")
    try:
        youtube = get_youtube_service()
        request_body = {
            'snippet': {
                'categoryId': '22', # People & Blogs
                'title': title,
                'description': description,
                'tags': tags
            },
            'status': {
                'privacyStatus': 'private', # Upload as private first
                'selfDeclaredMadeForKids': False
            }
        }
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        insert_request = youtube.videos().insert(
            part=','.join(request_body.keys()),
            body=request_body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = insert_request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%.")
        
        print(f"✅ Video uploaded successfully! Video ID: {response.get('id')}")
        return True
    except Exception as e:
        print(f"❌ YouTube upload failed: {e}")
        return False
