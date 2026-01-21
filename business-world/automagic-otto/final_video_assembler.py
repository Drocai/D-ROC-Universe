#!/usr/bin/env python3
"""
Final Video Assembler - Fix the FFmpeg concat issue and create complete video
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime

def assemble_final_video():
    """Assemble the video with proper FFmpeg syntax"""
    
    print("ASSEMBLING FINAL ENGAGING VIDEO")
    print("=" * 50)
    
    # Check assets
    assets_dir = Path("video_assets")
    images = list(assets_dir.glob("segment_*.jpg"))
    images.sort()
    
    audio_files = list(assets_dir.glob("narration_*.wav"))
    audio_path = audio_files[0] if audio_files else None
    
    print(f"Found {len(images)} image segments")
    print(f"Audio: {'Yes' if audio_path else 'No'}")
    
    if not images:
        print("No images found!")
        return None
    
    # Define durations for each segment (from the script)
    durations = [8, 12, 15, 18, 15, 12, 8]  # Total: 88 seconds
    
    if len(images) != len(durations):
        print(f"Mismatch: {len(images)} images vs {len(durations)} durations")
        # Adjust durations
        while len(durations) < len(images):
            durations.append(10)
    
    # Create video from images using simple method
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_videos = []
    
    # Create individual videos for each segment
    for i, (img, duration) in enumerate(zip(images, durations)):
        print(f"  Processing segment {i+1}/{len(images)}...")
        
        temp_video = assets_dir / f"temp_video_{i:02d}.mp4"
        
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-t', str(duration),
            '-i', str(img),
            '-vf', 'scale=1920:1080,fps=30',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
            '-pix_fmt', 'yuv420p',
            str(temp_video)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            temp_videos.append(str(temp_video))
        else:
            print(f"    Failed to create segment {i+1}")
            continue
    
    if not temp_videos:
        print("No video segments created!")
        return None
    
    # Concatenate videos
    print("Concatenating video segments...")
    
    concat_list = assets_dir / f"concat_{timestamp}.txt"
    with open(concat_list, 'w') as f:
        for video in temp_videos:
            f.write(f"file '{os.path.abspath(video)}'\n")
    
    # Create concatenated video
    concat_video = assets_dir / f"concat_{timestamp}.mp4"
    
    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat', '-safe', '0',
        '-i', str(concat_list),
        '-c', 'copy',
        str(concat_video)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Concatenation failed: {result.stderr}")
        return None
    
    # Add audio if available
    output_dir = Path("final_videos")
    final_output = output_dir / f"engaging_final_{timestamp}.mp4"
    
    if audio_path:
        print("Adding audio...")
        
        cmd = [
            'ffmpeg', '-y',
            '-i', str(concat_video),
            '-i', str(audio_path),
            '-c:v', 'copy',
            '-c:a', 'aac', '-b:a', '192k',
            '-shortest',
            str(final_output)
        ]
    else:
        print("Adding silent audio...")
        
        total_duration = sum(durations)
        cmd = [
            'ffmpeg', '-y',
            '-i', str(concat_video),
            '-f', 'lavfi', '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100:duration={total_duration}',
            '-c:v', 'copy', '-c:a', 'aac',
            '-shortest',
            str(final_output)
        ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        file_size = os.path.getsize(final_output) / (1024 * 1024)
        print(f"SUCCESS! Video created: {final_output}")
        print(f"Size: {file_size:.1f} MB")
        
        # Clean up temp files
        for temp_video in temp_videos:
            try:
                os.remove(temp_video)
            except:
                pass
        
        try:
            os.remove(concat_list)
            os.remove(concat_video)
        except:
            pass
        
        return str(final_output)
    else:
        print(f"Final assembly failed: {result.stderr}")
        return None

def upload_to_youtube(video_path):
    """Upload the final video"""
    
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        import pickle
        
        with open('token.pickle', 'rb') as f:
            creds = pickle.load(f)
        
        youtube = build('youtube', 'v3', credentials=creds)
        
        title = "This Medical Mystery Will Blow Your Mind! 🤯"
        
        body = {
            'snippet': {
                'title': title,
                'description': '''🔥 This incredible medical mystery will absolutely shock you!

A patient came to the doctor with a bizarre complaint - and what they discovered will change everything you think you know about medical diagnosis!

📺 WATCH UNTIL THE END for the mind-blowing revelation!

In this video:
🎯 The shocking medical mystery that baffled doctors
💡 Evidence that proves the impossible  
🔍 The investigation that revealed the truth
⚡ The revelation that will amaze you
🚀 What this means for medical science

TIMESTAMPS:
0:00 - The Shocking Hook
0:30 - The Medical Mystery Unfolds
1:00 - The Investigation Begins
1:30 - The Evidence Emerges
2:00 - The Mind-Blowing Truth

🔔 SUBSCRIBE for daily mind-blowing medical mysteries
👍 LIKE if this shocked you
💬 COMMENT your theories below
📤 SHARE with someone who loves mysteries

#MindBlowing #Medical #Mystery #Shocking #MustWatch #Incredible #Science #Discovery''',
                'tags': ['medical', 'mystery', 'shocking', 'mindblowing', 'science', 
                        'discovery', 'incredible', 'mustwatch', 'viral', 'amazing'],
                'categoryId': '27'  # Education
            },
            'status': {
                'privacyStatus': 'public',
                'embeddable': True,
                'madeForKids': False
            }
        }
        
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        
        request = youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        
        response = request.execute()
        video_id = response['id']
        
        print(f"UPLOADED TO YOUTUBE: https://www.youtube.com/watch?v={video_id}")
        
        # Log upload
        with open('uploaded_videos.log', 'a', encoding='utf-8') as f:
            f.write(f"ENGAGING: {title} - {datetime.now()}\\n")
        
        return f"https://www.youtube.com/watch?v={video_id}"
        
    except Exception as e:
        print(f"Upload failed: {e}")
        return None

if __name__ == "__main__":
    video_path = assemble_final_video()
    
    if video_path:
        print("\\nUploading to YouTube...")
        youtube_url = upload_to_youtube(video_path)
        
        if youtube_url:
            print(f"\\nSUCCESS! Your engaging video is live: {youtube_url}")
        else:
            print(f"\\nVideo ready for manual upload: {video_path}")
    else:
        print("\\nVideo assembly failed")