# core/pipelines/video_assembler.py - Assembles the final video
import os
import subprocess
from pathlib import Path
import time

VIDEO_OUTPUT_DIR = Path("final_videos")
VIDEO_OUTPUT_DIR.mkdir(exist_ok=True)

def assemble_video(visual_path, voiceover_path, music_path, brief: dict):
    """Creates a final video with visuals, audio, and dynamic effects using FFmpeg."""
    print("🎬 Assembling final video...")
    try:
        # Convert to Path objects if needed
        visual_path = Path(visual_path) if visual_path else None
        voiceover_path = Path(voiceover_path) if voiceover_path else None
        music_path = Path(music_path) if music_path else None
        
        # Check if visual path exists
        if not visual_path or not visual_path.exists():
            print(f"❌ Visual file not found: {visual_path}")
            return None
        
        # Create output filename
        timestamp = int(time.time())
        output_path = VIDEO_OUTPUT_DIR / f"otto_video_{timestamp}.mp4"
        
        # Build FFmpeg command
        cmd = [
            "ffmpeg", "-y",  # Overwrite output files without asking
            "-loop", "1",    # Loop the image
            "-i", str(visual_path),  # Input image
        ]
        
        # Add audio if available
        if voiceover_path and voiceover_path.exists():
            cmd.extend(["-i", str(voiceover_path)])
            cmd.extend(["-c:a", "aac"])  # Audio codec
            cmd.extend(["-shortest"])    # Duration matches shortest input
        else:
            cmd.extend(["-t", "10"])     # Default 10 second duration
            
        # Video settings
        cmd.extend([
            "-c:v", "libx264",    # Video codec
            "-pix_fmt", "yuv420p", # Pixel format for compatibility
            "-vf", "scale=1920:1080,zoompan=z='min(zoom+0.0015,1.5)':d=250",  # Scale and zoom effect
            str(output_path)
        ])
        
        print(f"Running FFmpeg command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Video assembled successfully: {output_path}")
            return output_path
        else:
            print(f"❌ FFmpeg failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Video assembly failed: {e}")
        return None

        # Prepare audio
        voiceover_clip = mpy.AudioFileClip(str(voiceover_path))
        final_duration = voiceover_clip.duration + 1.5 # Add padding
        
        final_visual_clip = final_visual_clip.set_duration(final_duration)

        # Add text overlay
        txt_clip = mpy.TextClip(brief["affirmation_text"], fontsize=70, color='white', font='Impact',
                                stroke_color='black', stroke_width=2,
                                size=(final_visual_clip.w * 0.9, None), method='caption')
        txt_clip = txt_clip.set_position(('center', 'center')).set_duration(final_duration).fadein(0.5).fadeout(0.5)

        # Combine audio tracks
        audio_clips = [voiceover_clip]
        if music_path:
            music_clip = mpy.AudioFileClip(str(music_path)).fx(mpy.afx.volumex, 0.1)
            # Loop music if shorter than video
            if music_clip.duration < final_duration:
                music_clip = music_clip.fx(mpy.afx.audio_loop, duration=final_duration)
            else:
                music_clip = music_clip.subclip(0, final_duration)
            audio_clips.append(music_clip)

        final_audio = mpy.CompositeAudioClip(audio_clips)

        # Compose final video
        video = mpy.CompositeVideoClip([final_visual_clip, txt_clip])
        video.audio = final_audio
        
        video_filename = f"OTTO_Magic_{brief['theme'].replace(' ', '_')}_{int(time.time())}.mp4"
        output_path = VIDEO_OUTPUT_DIR / video_filename
        
        video.write_videofile(str(output_path), codec="libx264", audio_codec="aac")
        
        return output_path
    except Exception as e:
        print(f"❌ Video assembly failed: {e}")
        return None
