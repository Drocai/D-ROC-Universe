#!/usr/bin/env python3
# test_ffmpeg.py - Test FFmpeg installation and basic media generation
import os
import sys
import tempfile
from pathlib import Path

print("Testing FFmpeg installation and basic media generation...")

# Try to import ffmpeg-python
try:
    import ffmpeg
    print("✓ ffmpeg-python: Installed")
except ImportError:
    print("❌ ffmpeg-python: Not installed")
    sys.exit(1)

# Try to create a test image using PIL
try:
    from PIL import Image, ImageDraw, ImageFont
    
    # Create a simple test image
    test_image_path = os.path.join("generated_images", "test_image.jpg")
    os.makedirs("generated_images", exist_ok=True)
    
    img = Image.new('RGB', (640, 480), color=(73, 109, 137))
    draw = ImageDraw.Draw(img)
    
    # Add some text
    font = ImageFont.load_default()
    draw.text((320, 240), "FFmpeg Test Image", fill=(255, 255, 255), anchor="mm")
    
    # Save the image
    img.save(test_image_path)
    print(f"✓ Created test image: {test_image_path}")
except Exception as e:
    print(f"❌ Failed to create test image: {e}")
    sys.exit(1)

# Try to create a test audio file using ffmpeg
try:
    test_audio_path = os.path.join("generated_audio", "test_audio.mp3")
    os.makedirs("generated_audio", exist_ok=True)
    
    # Create a silent audio file - 3 seconds duration
    (
        ffmpeg
        .input('anullsrc', format='lavfi', t='3')
        .output(test_audio_path, acodec='libmp3lame', ar='44100')
        .overwrite_output()
        .run(capture_stdout=True, capture_stderr=True, quiet=True)
    )
    print(f"✓ Created test audio: {test_audio_path}")
except Exception as e:
    print(f"❌ Failed to create test audio: {e}")
    sys.exit(1)

# Try to create a test video from the image and audio
try:
    test_video_path = os.path.join("final_videos", "test_video.mp4")
    os.makedirs("final_videos", exist_ok=True)
    
    # Create a temporary file list for ffmpeg's concat demuxer
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as tmpf:
        test_image_abs_path = os.path.abspath(test_image_path)
        clean_img_path = test_image_abs_path.replace('\\', '/')
        tmpf.write(f"file '{clean_img_path}'\n")
        tmpf.write(f"duration 3\n")
        temp_concat_file_path = tmpf.name

    # Create silent video from image
    temp_video_path = os.path.join(tempfile.gettempdir(), "temp_silent_video.mp4")
    print("Creating silent video...")
    # First, create silent video from image
    (
        ffmpeg
        .input(temp_concat_file_path, format='concat', safe=0)
        .output(temp_video_path, vcodec='libx264', pix_fmt='yuv420p', r='24')
        .overwrite_output()
        .run(capture_stdout=True, capture_stderr=True)
    )
    print(f"Silent video created at: {temp_video_path}")
    
    # Check that the silent video was created
    if not os.path.exists(temp_video_path):
        print(f"❌ Silent video was not created at {temp_video_path}")
        sys.exit(1)
    
    print("Adding audio to video...")
    # Then add audio to create final video - correct approach
    video_stream = ffmpeg.input(temp_video_path)
    audio_stream = ffmpeg.input(test_audio_path)
    
    try:
        (
            ffmpeg
            .output(video_stream, audio_stream, test_video_path, 
                    vcodec='copy', acodec='aac', shortest=None)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
    except Exception as e:
        print(f"❌ Error adding audio: {e}")
        # Try alternative syntax
        try:
            print("Trying alternative FFmpeg syntax...")
            result = ffmpeg.concat(video_stream, audio_stream, v=1, a=1).output(
                test_video_path, vcodec='copy', acodec='aac'
            ).overwrite_output().run(capture_stdout=True, capture_stderr=True)
            print("Alternative syntax worked!")
        except Exception as e2:
            print(f"❌ Alternative syntax also failed: {e2}")
            raise e  # Re-raise the original error
    
    print(f"✓ Created test video: {test_video_path}")
    print("\n✓ All tests PASSED! FFmpeg is working correctly.")
    
    # Clean up temporary files
    if os.path.exists(temp_concat_file_path):
        os.remove(temp_concat_file_path)
    if os.path.exists(temp_video_path):
        os.remove(temp_video_path)
        
except Exception as e:
    print(f"❌ Failed to create test video: {e}")
    print("\n❌ FFmpeg test FAILED.")
    sys.exit(1)
