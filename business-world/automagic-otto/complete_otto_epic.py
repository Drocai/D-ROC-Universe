#!/usr/bin/env python3
"""
Complete OTTO Epic - Finish the epic video with existing segments
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime

def complete_otto_epic():
    """Complete OTTO's epic video with existing segments"""
    
    print("COMPLETING OTTO'S EPIC MEDICAL MYSTERY")
    print("=" * 50)
    
    assets_dir = Path("epic_video_assets")
    
    # Find existing segments
    segments = []
    for i in range(7):
        segment_path = assets_dir / f"otto_segment_{i:02d}.mp4"
        if segment_path.exists():
            segments.append(str(segment_path))
            print(f"  Found segment {i}: {segment_path}")
    
    if not segments:
        print("No segments found!")
        return None
    
    print(f"Found {len(segments)} segments to assemble")
    
    # Create remaining segments quickly
    missing_segments = []
    for i in range(len(segments), 7):
        print(f"  Creating missing segment {i}...")
        
        img_path = assets_dir / f"medical_fallback_{i:02d}.jpg"
        if not img_path.exists():
            continue
            
        segment_path = assets_dir / f"otto_segment_{i:02d}.mp4"
        duration = [8, 10, 12, 14, 12, 15, 13][i]
        
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1', '-t', str(duration),
            '-i', str(img_path),
            '-vf', 'scale=1792:1024,fps=30',
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '25',
            '-pix_fmt', 'yuv420p',
            str(segment_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            segments.append(str(segment_path))
            missing_segments.append(str(segment_path))
            print(f"    [OK] Created segment {i}")
        else:
            print(f"    [FAIL] Segment {i}: {result.stderr}")
    
    # Concatenate all segments
    print("Assembling OTTO's epic video...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    concat_list = assets_dir / f"otto_final_{timestamp}.txt"
    
    with open(concat_list, 'w') as f:
        for segment in segments:
            f.write(f"file '{os.path.abspath(segment)}'\n")
    
    concat_video = assets_dir / f"otto_concat_{timestamp}.mp4"
    
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
    
    # Add OTTO's voice
    epic_dir = Path("epic_videos")
    epic_dir.mkdir(exist_ok=True)
    final_output = epic_dir / f"otto_epic_complete_{timestamp}.mp4"
    
    audio_path = assets_dir / "otto_narration.wav"
    
    if audio_path.exists():
        print("Adding OTTO's legendary voice...")
        
        cmd = [
            'ffmpeg', '-y',
            '-i', str(concat_video),
            '-i', str(audio_path),
            '-c:v', 'copy',
            '-c:a', 'aac', '-b:a', '192k',
            '-filter:a', 'volume=1.2',
            '-shortest',
            str(final_output)
        ]
    else:
        print("No OTTO voice found - creating silent version...")
        
        cmd = [
            'ffmpeg', '-y',
            '-i', str(concat_video),
            '-c', 'copy',
            str(final_output)
        ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        file_size = os.path.getsize(final_output) / (1024 * 1024)
        print(f"OTTO'S EPIC VIDEO COMPLETED: {final_output}")
        print(f"Size: {file_size:.1f} MB")
        print(f"Segments used: {len(segments)}")
        
        # Cleanup temp files
        try:
            os.remove(concat_list)
            os.remove(concat_video)
            for segment in missing_segments:
                try:
                    os.remove(segment)
                except:
                    pass
        except:
            pass
        
        return str(final_output)
    else:
        print(f"Final assembly failed: {result.stderr}")
        return None

def upload_otto_video(video_path):
    """Upload OTTO's epic video"""
    
    try:
        from final_video_assembler import upload_to_youtube
        
        print("Uploading OTTO's epic to YouTube...")
        youtube_url = upload_to_youtube(video_path)
        
        if youtube_url:
            print(f"OTTO'S EPIC LIVE: {youtube_url}")
            return youtube_url
        else:
            print(f"Ready for manual upload: {video_path}")
            return None
            
    except Exception as e:
        print(f"Upload error: {e}")
        return None

if __name__ == "__main__":
    video_path = complete_otto_epic()
    
    if video_path:
        youtube_url = upload_otto_video(video_path)
        
        if youtube_url:
            print(f"\nOTTO'S EPIC SUCCESS: {youtube_url}")
        else:
            print(f"\nOTTO epic ready: {video_path}")
    else:
        print("\nOTTO epic completion failed")