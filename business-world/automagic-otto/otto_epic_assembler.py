#!/usr/bin/env python3
"""
OTTO Epic Assembler - Fast assembly of epic video with existing assets
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime

def assemble_otto_epic():
    """Assemble epic OTTO video quickly"""
    
    print("ASSEMBLING OTTO'S EPIC MEDICAL MYSTERY")
    print("=" * 50)
    
    assets_dir = Path("epic_video_assets")
    
    # Check for assets
    images = [assets_dir / f"medical_fallback_{i:02d}.jpg" for i in range(7)]
    audio_path = assets_dir / "otto_narration.wav"
    
    print(f"Medical images: {len([img for img in images if img.exists()])}/7")
    print(f"OTTO voice: {'Yes' if audio_path.exists() else 'No'}")
    
    # Durations for dramatic pacing
    durations = [8, 10, 12, 14, 12, 15, 13]  # Total: 84 seconds
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_videos = []
    
    # Create video segments with medical effects
    for i, (img, duration) in enumerate(zip(images, durations)):
        if not img.exists():
            continue
            
        print(f"  Creating medical segment {i+1}/7...")
        
        temp_video = assets_dir / f"otto_segment_{i:02d}.mp4"
        
        # Medical documentary effects
        if i in [0, 1]:  # Mysterious opening
            effect = "zoompan=z='min(zoom+0.002,1.3)':d={}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',eq=contrast=1.1:brightness=-0.1".format(duration*30)
        elif i in [2, 3]:  # Shocking revelation  
            effect = "scale=2000:1200,crop=1792:1024:'t*30':0,eq=contrast=1.2:saturation=0.8"
        else:  # Resolution and triumph
            effect = "zoompan=z='if(lte(zoom,1.0),1.2,max(1.001,zoom-0.002))':d={}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',eq=brightness=0.1:saturation=1.2".format(duration*30)
        
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1', '-t', str(duration),
            '-i', str(img),
            '-vf', f'{effect},fps=30',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '22',
            '-pix_fmt', 'yuv420p',
            str(temp_video)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            temp_videos.append(str(temp_video))
            print(f"    [OK] Medical segment {i+1}")
        else:
            print(f"    [FAIL] Segment {i+1}: {result.stderr}")
    
    if not temp_videos:
        print("No video segments created!")
        return None
    
    # Concatenate medical segments
    print("Assembling medical documentary...")
    
    concat_list = assets_dir / f"otto_concat_{timestamp}.txt"
    with open(concat_list, 'w') as f:
        for video in temp_videos:
            f.write(f"file '{os.path.abspath(video)}'\n")
    
    concat_video = assets_dir / f"otto_medical_{timestamp}.mp4"
    
    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat', '-safe', '0',
        '-i', str(concat_list),
        '-c', 'copy',
        str(concat_video)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Assembly failed: {result.stderr}")
        return None
    
    # Add OTTO's voice
    epic_dir = Path("epic_videos") 
    epic_dir.mkdir(exist_ok=True)
    final_output = epic_dir / f"otto_medical_epic_{timestamp}.mp4"
    
    if audio_path.exists():
        print("Adding OTTO's legendary voice...")
        
        cmd = [
            'ffmpeg', '-y',
            '-i', str(concat_video),
            '-i', str(audio_path),
            '-c:v', 'copy',
            '-c:a', 'aac', '-b:a', '192k',
            '-filter:a', 'volume=1.1',
            '-shortest',
            str(final_output)
        ]
    else:
        print("Creating silent medical documentary...")
        
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
        print(f"OTTO'S EPIC VIDEO COMPLETED: {final_output}")
        print(f"Size: {file_size:.1f} MB")
        
        # Cleanup
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

def upload_otto_epic(video_path):
    """Upload OTTO's epic video to YouTube"""
    
    try:
        from final_video_assembler import upload_to_youtube
        
        print("Uploading OTTO's epic medical mystery...")
        youtube_url = upload_to_youtube(video_path)
        
        if youtube_url:
            print(f"OTTO'S EPIC VIDEO LIVE: {youtube_url}")
            return youtube_url
        else:
            print(f"Ready for manual upload: {video_path}")
            return None
            
    except Exception as e:
        print(f"Upload failed: {e}")
        return None

if __name__ == "__main__":
    video_path = assemble_otto_epic()
    
    if video_path:
        youtube_url = upload_otto_epic(video_path)
        
        if youtube_url:
            print(f"\nOTTO'S EPIC SUCCESS: {youtube_url}")
        else:
            print(f"\nOTTO video ready: {video_path}")
    else:
        print("\nOTTO epic assembly failed")