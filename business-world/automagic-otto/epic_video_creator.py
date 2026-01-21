#!/usr/bin/env python3
"""
Epic Video Creator - Creates truly engaging videos with real imagery and OTTO's voice
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import math
import random

class EpicVideoCreator:
    def __init__(self):
        self.assets_dir = Path("epic_video_assets")
        self.assets_dir.mkdir(exist_ok=True)
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.elevenlabs_key = os.getenv("ELEVENLABS_API_KEY") 
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "SBySMDeS4TryzE8AQWrm")
        
    def generate_epic_story(self):
        """Generate an epic medical mystery story"""
        
        story = {
            "title": "The Impossible Medical Case That Shocked Doctors Worldwide",
            "hook": "A 34-year-old patient walked into the ER with symptoms that defied all medical knowledge...",
            "segments": [
                {
                    "text": "Meet Sarah Chen, a healthy 34-year-old engineer who woke up one morning with the most bizarre symptom doctors had ever seen.",
                    "visual_prompt": "Professional medical consultation room, concerned female patient talking to doctor, realistic medical setting, cinematic lighting",
                    "duration": 8,
                    "emotion": "mysterious"
                },
                {
                    "text": "Her blood was turning blue. Not metaphorically - literally blue. And it was happening in real time as doctors watched.",
                    "visual_prompt": "Medical laboratory, blue-tinted blood sample in test tube, shocked laboratory technician examining sample, dramatic lighting",
                    "duration": 10,
                    "emotion": "shocking"
                },
                {
                    "text": "The medical team ran every test imaginable. Toxicology, blood chemistry, genetic analysis. Everything came back normal except for one impossible detail.",
                    "visual_prompt": "High-tech medical laboratory, multiple doctors analyzing test results on computer screens, medical equipment, intense atmosphere",
                    "duration": 12,
                    "emotion": "intense"
                },
                {
                    "text": "Her hemoglobin was somehow binding with an unknown compound that shouldn't exist in the human body. The mystery deepened when they discovered...",
                    "visual_prompt": "Microscopic view of blood cells, strange blue compound visible under microscope, scientist adjusting microscope settings, discovery moment",
                    "duration": 14,
                    "emotion": "revelation"
                },
                {
                    "text": "Sarah had been exposed to a rare industrial chemical at her engineering job. But here's the mind-blowing part - the exposure happened 20 years ago.",
                    "visual_prompt": "Industrial engineering facility flashback, young woman working with chemicals, time-lapse effect showing years passing",
                    "duration": 12,
                    "emotion": "amazement"
                },
                {
                    "text": "The chemical had been dormant in her system for two decades, only activating when triggered by a specific medication she took for a headache.",
                    "visual_prompt": "Split screen showing chemical molecular structure and medicine bottle, medical reaction visualization, scientific breakthrough moment",
                    "duration": 15,
                    "emotion": "understanding"
                },
                {
                    "text": "This discovery revolutionized how we understand long-term chemical exposure and led to new safety protocols worldwide. Sarah made a full recovery.",
                    "visual_prompt": "Modern medical breakthrough celebration, healthy Sarah Chen smiling, medical team celebrating, worldwide impact visualization",
                    "duration": 13,
                    "emotion": "triumph"
                }
            ]
        }
        
        return story
        
    def generate_real_images(self, story):
        """Generate actual medical imagery using DALL-E"""
        
        print("Generating epic medical imagery...")
        
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        
        images = []
        
        for i, segment in enumerate(story["segments"]):
            print(f"  Creating image {i+1}/7: {segment['emotion']} scene...")
            
            # Enhanced prompt for medical realism
            enhanced_prompt = f"""
            High-quality medical documentary style image: {segment['visual_prompt']}.
            Photorealistic, professional medical photography, cinematic composition, 
            dramatic lighting, medical accuracy, documentary style, high detail, 
            {segment['emotion']} atmosphere, suitable for medical education video.
            """
            
            payload = {
                "model": "dall-e-3",
                "prompt": enhanced_prompt,
                "size": "1792x1024",
                "quality": "hd",
                "n": 1,
                "style": "natural"
            }
            
            try:
                response = requests.post(
                    "https://api.openai.com/v1/images/generations",
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    image_url = result["data"][0]["url"]
                    
                    # Download image
                    img_response = requests.get(image_url, timeout=30)
                    image_path = self.assets_dir / f"medical_scene_{i:02d}.jpg"
                    
                    with open(image_path, 'wb') as f:
                        f.write(img_response.content)
                    
                    images.append({
                        "path": str(image_path),
                        "segment": segment,
                        "index": i
                    })
                    
                    print(f"    [OK] Created: {image_path}")
                    
                else:
                    print(f"    [FAIL] Failed: {response.status_code}")
                    # Create fallback with medical theme
                    fallback_path = self.create_medical_fallback(i, segment)
                    images.append({
                        "path": fallback_path,
                        "segment": segment, 
                        "index": i
                    })
                    
            except Exception as e:
                print(f"    [ERROR] Error: {e}")
                fallback_path = self.create_medical_fallback(i, segment)
                images.append({
                    "path": fallback_path,
                    "segment": segment,
                    "index": i
                })
        
        return images
        
    def create_medical_fallback(self, index, segment):
        """Create medical-themed fallback image"""
        
        # Medical color schemes based on emotion
        color_schemes = {
            "mysterious": [(20, 30, 60), (40, 60, 120), (60, 90, 180)],
            "shocking": [(120, 20, 20), (180, 40, 40), (220, 60, 60)],
            "intense": [(60, 20, 80), (120, 40, 160), (180, 60, 240)],
            "revelation": [(20, 80, 120), (40, 160, 240), (60, 200, 255)],
            "amazement": [(80, 60, 20), (160, 120, 40), (240, 180, 60)],
            "understanding": [(20, 120, 60), (40, 240, 120), (60, 255, 180)],
            "triumph": [(60, 120, 20), (120, 240, 40), (180, 255, 60)]
        }
        
        colors = color_schemes.get(segment["emotion"], [(50, 50, 50), (100, 100, 100), (150, 150, 150)])
        
        # Create 1792x1024 image
        img = Image.new('RGB', (1792, 1024), colors[0])
        draw = ImageDraw.Draw(img)
        
        # Medical cross symbol
        cross_color = colors[2]
        cross_size = 200
        cross_x = 1792 // 2
        cross_y = 1024 // 2
        
        # Horizontal bar
        draw.rectangle([
            cross_x - cross_size, cross_y - 30,
            cross_x + cross_size, cross_y + 30
        ], fill=cross_color)
        
        # Vertical bar  
        draw.rectangle([
            cross_x - 30, cross_y - cross_size,
            cross_x + 30, cross_y + cross_size
        ], fill=cross_color)
        
        # Medical wave pattern
        for wave in range(5):
            wave_y = 200 + wave * 150
            points = []
            for x in range(0, 1792, 20):
                y = wave_y + math.sin(x * 0.01 + index) * 50
                points.extend([x, y])
            
            if len(points) >= 4:
                draw.line(points, fill=colors[1], width=8)
        
        # Pulse line effect
        pulse_points = []
        for x in range(0, 1792, 10):
            if x % 200 < 50:  # Pulse spike
                y = 100 + math.sin(x * 0.1) * 40
            else:  # Flat line
                y = 100
            pulse_points.extend([x, y])
            
        if len(pulse_points) >= 4:
            draw.line(pulse_points, fill=colors[2], width=6)
        
        # Add text overlay
        try:
            font_size = 72
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Title text
        title = f"Medical Mystery #{index + 1}"
        bbox = draw.textbbox((0, 0), title, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (1792 - text_width) // 2
        
        # Text shadow
        draw.text((text_x + 4, 50 + 4), title, font=font, fill=(0, 0, 0))
        draw.text((text_x, 50), title, font=font, fill=colors[2])
        
        # Save image
        fallback_path = self.assets_dir / f"medical_fallback_{index:02d}.jpg"
        img.save(fallback_path, quality=95)
        
        return str(fallback_path)
        
    def generate_otto_voice(self, story):
        """Generate OTTO's iconic female voice using ElevenLabs"""
        
        print("Generating OTTO's voice narration...")
        
        # Combine all text with dramatic pauses
        full_script = f"""
        I'm OTTO, and I'm about to tell you about a medical case that will absolutely blow your mind.
        
        {story['hook']}
        
        """
        
        for segment in story["segments"]:
            full_script += f"{segment['text']}\n\n"
        
        full_script += """
        This is OTTO, bringing you the most incredible medical mysteries. 
        Subscribe for more mind-blowing cases that will change how you see medicine forever.
        """
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.elevenlabs_key
        }
        
        payload = {
            "text": full_script,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8,
                "style": 0.6,
                "use_speaker_boost": True
            }
        }
        
        try:
            print(f"  Using ElevenLabs voice ID: {self.voice_id}")
            
            response = requests.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}",
                json=payload,
                headers=headers,
                timeout=120
            )
            
            if response.status_code == 200:
                audio_path = self.assets_dir / "otto_narration.wav"
                with open(audio_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"  [OK] OTTO voice created: {audio_path}")
                return str(audio_path)
            else:
                print(f"  [FAIL] ElevenLabs failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return self.create_fallback_voice(full_script)
                
        except Exception as e:
            print(f"  [ERROR] ElevenLabs error: {e}")
            return self.create_fallback_voice(full_script)
    
    def create_fallback_voice(self, text):
        """Create voice using Windows SAPI with female voice"""
        
        print("  Creating fallback voice with Windows SAPI...")
        
        audio_path = self.assets_dir / "otto_narration.wav"
        
        # PowerShell script for female voice
        ps_script = f'''
Add-Type -AssemblyName System.Speech
$synthesizer = New-Object System.Speech.Synthesis.SpeechSynthesizer

# Try to select a female voice
$voices = $synthesizer.GetInstalledVoices()
foreach ($voice in $voices) {{
    if ($voice.VoiceInfo.Gender -eq "Female") {{
        $synthesizer.SelectVoice($voice.VoiceInfo.Name)
        break
    }}
}}

# Set speech parameters for more engaging delivery
$synthesizer.Rate = 0
$synthesizer.Volume = 100

$synthesizer.SetOutputToWaveFile("{os.path.abspath(audio_path)}")
$synthesizer.Speak(@"
{text}
"@)
$synthesizer.Dispose()
'''
        
        script_path = self.assets_dir / "voice_script.ps1"
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(ps_script)
        
        try:
            result = subprocess.run([
                "powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_path)
            ], capture_output=True, text=True, timeout=180)
            
            if audio_path.exists():
                print(f"  [OK] Fallback voice created: {audio_path}")
                script_path.unlink()
                return str(audio_path)
            else:
                print(f"  [FAIL] Voice creation failed")
                return None
                
        except Exception as e:
            print(f"  [ERROR] Voice error: {e}")
            return None
    
    def create_epic_video(self, story, images, audio_path):
        """Create epic video with dynamic effects and real imagery"""
        
        print("Creating epic video with cinematic effects...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_videos = []
        
        # Create individual video segments with effects
        for i, img_data in enumerate(images):
            print(f"  Processing epic segment {i+1}/7...")
            
            segment = img_data["segment"]
            duration = segment["duration"]
            
            temp_video = self.assets_dir / f"epic_segment_{i:02d}.mp4"
            
            # Advanced FFmpeg with cinematic effects
            effects = []
            
            # Ken Burns effect with emotion-based movement
            if segment["emotion"] in ["mysterious", "shocking"]:
                # Zoom in dramatically
                effects.append("scale=2000:1125,crop=1792:1024:iw/2-896:ih/2-512")
                effects.append(f"zoompan=z='min(zoom+0.001,1.2)':d={duration*30}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'")
            elif segment["emotion"] in ["intense", "revelation"]:
                # Pan across image
                effects.append(f"scale=2000:1125,crop=1792:1024:'t*50':0")
            else:
                # Subtle zoom out
                effects.append(f"zoompan=z='if(lte(zoom,1.0),1.1,max(1.001,zoom-0.001))':d={duration*30}")
            
            # Color grading based on emotion
            if segment["emotion"] == "shocking":
                effects.append("eq=contrast=1.2:brightness=0.1:saturation=0.8")
            elif segment["emotion"] == "mysterious":
                effects.append("eq=contrast=1.1:brightness=-0.1:saturation=1.2")
            elif segment["emotion"] == "triumph":
                effects.append("eq=contrast=1.1:brightness=0.1:saturation=1.3")
            
            # Combine effects
            video_filter = ",".join(effects) if effects else "scale=1792:1024"
            
            cmd = [
                'ffmpeg', '-y',
                '-loop', '1',
                '-t', str(duration),
                '-i', img_data["path"],
                '-vf', f'{video_filter},fps=30',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '20',
                '-pix_fmt', 'yuv420p',
                str(temp_video)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                temp_videos.append(str(temp_video))
                print(f"    [OK] Epic segment {i+1} created")
            else:
                print(f"    [FAIL] Segment {i+1} failed: {result.stderr}")
        
        if not temp_videos:
            print("No video segments created!")
            return None
        
        # Concatenate with smooth transitions
        print("Assembling epic final video...")
        
        concat_list = self.assets_dir / f"epic_concat_{timestamp}.txt"
        with open(concat_list, 'w') as f:
            for video in temp_videos:
                f.write(f"file '{os.path.abspath(video)}'\n")
        
        concat_video = self.assets_dir / f"epic_concat_{timestamp}.mp4"
        
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
        
        # Add OTTO's voice with audio enhancement
        final_dir = Path("epic_videos")
        final_dir.mkdir(exist_ok=True)
        final_output = final_dir / f"otto_epic_medical_{timestamp}.mp4"
        
        if audio_path and os.path.exists(audio_path):
            print("Adding OTTO's epic narration...")
            
            cmd = [
                'ffmpeg', '-y',
                '-i', str(concat_video),
                '-i', audio_path,
                '-c:v', 'copy',
                '-c:a', 'aac', '-b:a', '256k',
                '-filter:a', 'volume=1.2,loudnorm',  # Audio enhancement
                '-shortest',
                str(final_output)
            ]
        else:
            print("No audio - creating silent version...")
            
            total_duration = sum(seg["duration"] for seg in story["segments"])
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
            print(f"SUCCESS! Epic OTTO video created: {final_output}")
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

def create_epic_video():
    """Main function to create epic video"""
    
    print("CREATING EPIC OTTO MEDICAL MYSTERY VIDEO")
    print("=" * 60)
    
    creator = EpicVideoCreator()
    
    # Generate epic story
    story = creator.generate_epic_story()
    print(f"Story: {story['title']}")
    
    # Generate real medical imagery
    images = creator.generate_real_images(story)
    
    # Generate OTTO's voice
    audio_path = creator.generate_otto_voice(story)
    
    # Create epic video
    video_path = creator.create_epic_video(story, images, audio_path)
    
    if video_path:
        print(f"\nEPIC VIDEO READY: {video_path}")
        return video_path
    else:
        print("\nEpic video creation failed")
        return None

if __name__ == "__main__":
    create_epic_video()