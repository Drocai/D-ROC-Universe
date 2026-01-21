#!/usr/bin/env python3
# test_ffmpeg_simple.py - Simpler test for FFmpeg
import os
import sys
import tempfile
import shutil
from pathlib import Path

print("Testing FFmpeg functionality...")

# Try to import ffmpeg
try:
    import ffmpeg
    print("✅ ffmpeg-python package is installed")
except ImportError:
    print("❌ ffmpeg-python package is not installed")
    sys.exit(1)

# Set up paths
test_dir = os.path.join(os.getcwd(), "test_output")
os.makedirs(test_dir, exist_ok=True)

# Test 1: Create silent audio
silent_audio_path = os.path.join(test_dir, "silent.mp3")
print(f"Creating silent audio file: {silent_audio_path}")

try:
    (
        ffmpeg
        .input('anullsrc', format='lavfi', t='3')
        .output(silent_audio_path, acodec='libmp3lame', ar='44100')
        .overwrite_output()
        .run(capture_stdout=True, capture_stderr=True, quiet=True)
    )
    
    if os.path.exists(silent_audio_path) and os.path.getsize(silent_audio_path) > 0:
        print("✅ Successfully created silent audio")
    else:
        print("❌ Failed to create silent audio file")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error creating silent audio: {e}")
    sys.exit(1)

# Test 2: Create a color test video
color_video_path = os.path.join(test_dir, "color.mp4")
print(f"Creating color test video: {color_video_path}")

try:
    (
        ffmpeg
        .input('color=c=blue:s=1280x720:d=3', format='lavfi')
        .output(color_video_path, vcodec='libx264', pix_fmt='yuv420p')
        .overwrite_output()
        .run(capture_stdout=True, capture_stderr=True)
    )
    
    if os.path.exists(color_video_path) and os.path.getsize(color_video_path) > 0:
        print("✅ Successfully created color test video")
    else:
        print("❌ Failed to create color test video")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error creating color video: {e}")
    sys.exit(1)

# Test 3: Combine video and audio
final_video_path = os.path.join(test_dir, "final.mp4")
print(f"Creating final video with audio: {final_video_path}")

try:
    # Create input streams
    video_stream = ffmpeg.input(color_video_path)
    audio_stream = ffmpeg.input(silent_audio_path)
    
    # Combine streams
    print("Combining video and audio streams...")
    (
        ffmpeg
        .output(video_stream, audio_stream, final_video_path, vcodec='copy', acodec='aac')
        .overwrite_output()
        .run(capture_stdout=True, capture_stderr=True)
    )
    
    if os.path.exists(final_video_path) and os.path.getsize(final_video_path) > 0:
        print("✅ Successfully created final video with audio")
    else:
        print("❌ Failed to create final video")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error creating final video: {e}")
    sys.exit(1)

print("\n✅ All FFmpeg tests passed successfully!")
print(f"Test files are available in: {test_dir}")
