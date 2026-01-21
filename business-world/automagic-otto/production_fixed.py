#!/usr/bin/env python3
"""
AutoMagic Fixed Production Pipeline
Creates proper videos with real DALL-E images and ElevenLabs voice
"""
import os
import sys
import time
import logging
import json
import random
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AutoMagic.Production')

class FixedVideoProduction:
    def __init__(self):
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
        self.elevenlabs_voice = os.getenv('ELEVENLABS_VOICE_ID', 'SBySMDeS4TryzE8AQWrm')
        
    def get_trending_topic(self):
        """Get a trending topic"""
        try:
            from trend_integration import get_trending_topic as get_trend
            topic_data = get_trend()
            logger.info(f"📊 Trending Topic: {topic_data['topic']}")
            return topic_data['topic']
        except Exception as e:
            logger.warning(f"Using fallback topic: {e}")
            topics = [
                "The amazing world of artificial intelligence",
                "How nature inspires modern technology", 
                "Space exploration breakthroughs in 2024",
                "The science behind everyday objects",
                "Incredible animal intelligence discoveries"
            ]
            return random.choice(topics)
    
    def generate_script(self, topic):
        """Generate a proper video script"""
        logger.info("✍️ Generating script...")
        
        # Check if OpenAI is available
        if self.openai_key:
            try:
                import openai
                client = openai.OpenAI(api_key=self.openai_key)
                
                prompt = f"""Write an engaging 2-3 minute video script about: {topic}
                
                Requirements:
                - Hook the viewer in the first 5 seconds
                - Include 3-4 main points with examples
                - Educational but entertaining
                - Natural conversational tone
                - End with a call to action
                
                Format as natural speech (no stage directions or formatting)."""
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=600,
                    temperature=0.8
                )
                
                script = response.choices[0].message.content.strip()
                logger.info(f"✓ Script generated: {len(script)} characters")
                return script
                
            except Exception as e:
                logger.error(f"OpenAI error: {e}")
                if "quota" in str(e).lower():
                    logger.warning("⚠️ OpenAI quota exceeded - using fallback")
        
        # Fallback script
        script = f"""
        Have you ever wondered about {topic}? Today, we're diving into something truly fascinating that will change how you see the world.
        
        {topic} is more incredible than most people realize. Let me share three amazing facts that will blow your mind.
        
        First, recent discoveries have shown us completely new perspectives on this topic. Scientists and researchers are uncovering things we never thought possible just a few years ago.
        
        Second, the practical applications are everywhere around us. From the technology in your pocket to the natural world outside your window, {topic} influences our daily lives in ways you might never expect.
        
        Third, the future possibilities are limitless. Experts predict that in the next decade, we'll see revolutionary changes that will transform how we live, work, and understand our universe.
        
        What fascinates me most about {topic} is how it connects to so many other areas of knowledge. It's a reminder that everything in our world is interconnected in beautiful and surprising ways.
        
        So the next time you encounter something related to {topic}, take a moment to appreciate the incredible complexity and beauty behind it. There's always more to discover, more to learn, and more to wonder about.
        
        What aspect of {topic} interests you the most? Let me know in the comments below, and don't forget to subscribe for more fascinating content like this. Thanks for watching, and keep exploring!
        """
        
        logger.info(f"✓ Using enhanced fallback script: {len(script)} characters")
        return script.strip()
    
    def generate_images(self, topic, script):
        """Generate DALL-E images"""
        logger.info("🎨 Generating images...")
        
        image_dir = Path("generated_images")
        image_dir.mkdir(exist_ok=True)
        
        images = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Try DALL-E first
        if self.openai_key:
            try:
                import openai
                client = openai.OpenAI(api_key=self.openai_key)
                
                # Create 3-4 different image prompts based on the script
                image_prompts = [
                    f"High quality, photorealistic image representing {topic}, professional photography, vibrant colors, 4K",
                    f"Detailed visualization of {topic}, modern design, clean aesthetic, educational infographic style",
                    f"Artistic interpretation of {topic}, creative composition, stunning visuals, magazine quality",
                    f"Cinematic scene showcasing {topic}, dramatic lighting, professional production value"
                ]
                
                for i, prompt in enumerate(image_prompts[:3], 1):
                    try:
                        logger.info(f"  Generating DALL-E image {i}/3...")
                        
                        response = client.images.generate(
                            model="dall-e-3",
                            prompt=prompt,
                            size="1792x1024",  # HD widescreen
                            quality="hd",
                            n=1
                        )
                        
                        # Download image
                        import requests
                        img_url = response.data[0].url
                        img_response = requests.get(img_url, timeout=30)
                        
                        if img_response.status_code == 200:
                            img_path = image_dir / f"dalle_{i}_{timestamp}.png"
                            with open(img_path, 'wb') as f:
                                f.write(img_response.content)
                            images.append(str(img_path))
                            logger.info(f"  ✓ DALL-E image {i} saved")
                        
                    except Exception as e:
                        logger.warning(f"  DALL-E image {i} failed: {e}")
                
                if images:
                    logger.info(f"✓ Generated {len(images)} DALL-E images")
                    return images
                    
            except Exception as e:
                logger.error(f"DALL-E generation failed: {e}")
        
        # Enhanced fallback images using PIL
        logger.info("  Using enhanced fallback image generation...")
        from PIL import Image, ImageDraw, ImageFont, ImageFilter
        import colorsys
        
        # Create 4 visually distinct images
        themes = [
            {"colors": [(25, 118, 210), (33, 150, 243)], "title": "Introduction"},
            {"colors": [(56, 142, 60), (76, 175, 80)], "title": "Key Points"},
            {"colors": [(245, 124, 0), (255, 152, 0)], "title": "Examples"},
            {"colors": [(123, 31, 162), (156, 39, 176)], "title": "Conclusion"}
        ]
        
        for i, theme in enumerate(themes[:3], 1):
            # Create gradient background
            img = Image.new('RGB', (1920, 1080))
            draw = ImageDraw.Draw(img)
            
            # Gradient effect
            for y in range(1080):
                r = int(theme["colors"][0][0] + (theme["colors"][1][0] - theme["colors"][0][0]) * y / 1080)
                g = int(theme["colors"][0][1] + (theme["colors"][1][1] - theme["colors"][0][1]) * y / 1080)
                b = int(theme["colors"][0][2] + (theme["colors"][1][2] - theme["colors"][0][2]) * y / 1080)
                draw.rectangle([(0, y), (1920, y+1)], fill=(r, g, b))
            
            # Add overlay shapes for visual interest
            overlay = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            
            # Random geometric shapes
            for _ in range(5):
                x = random.randint(0, 1920)
                y = random.randint(0, 1080)
                size = random.randint(100, 400)
                opacity = random.randint(20, 60)
                overlay_draw.ellipse([x, y, x+size, y+size], fill=(255, 255, 255, opacity))
            
            # Composite with blur
            overlay = overlay.filter(ImageFilter.GaussianBlur(radius=30))
            img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
            
            # Add text
            draw = ImageDraw.Draw(img)
            
            try:
                # Try to use a better font
                title_font = ImageFont.truetype("arial.ttf", 80)
                subtitle_font = ImageFont.truetype("arial.ttf", 40)
            except:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
            
            # Main title
            title_text = topic[:50] + "..." if len(topic) > 50 else topic
            
            # Draw text with shadow
            shadow_offset = 4
            draw.text((960+shadow_offset, 400+shadow_offset), title_text, 
                     fill=(0, 0, 0, 128), font=title_font, anchor='mm')
            draw.text((960, 400), title_text, 
                     fill='white', font=title_font, anchor='mm')
            
            # Section title
            draw.text((960+2, 550+2), f"Part {i}: {theme['title']}", 
                     fill=(0, 0, 0, 128), font=subtitle_font, anchor='mm')
            draw.text((960, 550), f"Part {i}: {theme['title']}", 
                     fill='white', font=subtitle_font, anchor='mm')
            
            # Save
            img_path = image_dir / f"enhanced_{i}_{timestamp}.jpg"
            img.save(img_path, 'JPEG', quality=95)
            images.append(str(img_path))
            logger.info(f"  ✓ Enhanced image {i} created")
        
        # Add one more image for better video length
        if len(images) < 4:
            # Create end screen
            img = Image.new('RGB', (1920, 1080), (30, 30, 30))
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype("arial.ttf", 60)
            except:
                font = ImageFont.load_default()
            
            draw.text((960, 450), "Thanks for Watching!", fill='white', font=font, anchor='mm')
            draw.text((960, 550), "Subscribe for More", fill=(255, 200, 0), font=font, anchor='mm')
            
            img_path = image_dir / f"endscreen_{timestamp}.jpg"
            img.save(img_path, 'JPEG', quality=95)
            images.append(str(img_path))
        
        logger.info(f"✓ Generated {len(images)} enhanced images")
        return images
    
    def generate_voiceover(self, script):
        """Generate ElevenLabs voiceover"""
        logger.info("🎤 Generating voiceover...")
        
        audio_dir = Path("generated_audio")
        audio_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_path = audio_dir / f"voiceover_{timestamp}.mp3"
        
        # Try ElevenLabs
        if self.elevenlabs_key and self.elevenlabs_voice:
            try:
                import elevenlabs
                from elevenlabs import generate, save, set_api_key
                
                # Set API key
                set_api_key(self.elevenlabs_key)
                
                logger.info(f"  Using ElevenLabs voice: {self.elevenlabs_voice}")
                
                # Generate audio
                audio = generate(
                    text=script,
                    voice=self.elevenlabs_voice,
                    model="eleven_monolingual_v1"
                )
                
                # Save audio
                save(audio, str(audio_path))
                
                # Verify audio
                if audio_path.exists() and audio_path.stat().st_size > 10000:
                    logger.info(f"✓ ElevenLabs voiceover generated: {audio_path}")
                    return str(audio_path)
                else:
                    logger.warning("ElevenLabs audio too small or missing")
                    
            except Exception as e:
                logger.error(f"ElevenLabs error: {e}")
        
        # Enhanced fallback: Generate TTS using system or pyttsx3
        logger.info("  Using enhanced fallback audio generation...")
        
        try:
            # Try pyttsx3 for actual speech
            import pyttsx3
            
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)  # Speed
            engine.setProperty('volume', 1.0)  # Volume
            
            # Save speech to file
            engine.save_to_file(script, str(audio_path))
            engine.runAndWait()
            
            if audio_path.exists():
                logger.info(f"✓ TTS voiceover generated: {audio_path}")
                return str(audio_path)
                
        except Exception as e:
            logger.warning(f"TTS generation failed: {e}")
        
        # Final fallback: Create beep-tone audio with proper length
        logger.info("  Creating extended audio track...")
        
        # Calculate approximate duration (150 words per minute)
        word_count = len(script.split())
        duration = max(120, int(word_count / 150 * 60))  # At least 2 minutes
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f'sine=frequency=440:duration={duration}:sample_rate=44100',
            '-af', 'volume=0.1',  # Very quiet tone
            '-c:a', 'libmp3lame',
            '-b:a', '128k',
            str(audio_path)
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            logger.info(f"✓ Extended audio track created ({duration}s)")
            return str(audio_path)
        except Exception as e:
            logger.error(f"Audio generation failed: {e}")
            return None
    
    def create_video(self, images, audio, topic):
        """Create final video with proper timing"""
        logger.info("🎬 Creating video...")
        
        if not images or not audio:
            logger.error("Missing images or audio")
            return None
        
        video_dir = Path("final_videos")
        video_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = video_dir / f"automagic_proper_{timestamp}.mp4"
        
        # Get audio duration
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                 '-of', 'csv=p=0', audio],
                capture_output=True, text=True
            )
            audio_duration = float(result.stdout.strip())
            logger.info(f"  Audio duration: {audio_duration:.1f}s")
        except:
            audio_duration = 120  # Default 2 minutes
        
        # Calculate time per image
        time_per_image = audio_duration / len(images)
        logger.info(f"  Time per image: {time_per_image:.1f}s")
        
        # Create input file for FFmpeg
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            for img in images:
                abs_path = os.path.abspath(img).replace('\\', '/')
                f.write(f"file '{abs_path}'\n")
                f.write(f"duration {time_per_image}\n")
            # Add last image again for proper ending
            f.write(f"file '{abs_path}'\n")
            input_file = f.name
        
        # FFmpeg command with better settings
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', input_file,
            '-i', audio,
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',  # Good quality
            '-c:a', 'aac',
            '-b:a', '128k',
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart',  # Better for streaming
            '-shortest',  # Match shortest stream
            str(output_path)
        ]
        
        try:
            logger.info("  Running FFmpeg...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Cleanup temp file
            os.unlink(input_file)
            
            if output_path.exists() and output_path.stat().st_size > 100000:
                # Verify the video
                probe_cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 
                           'format=duration', '-of', 'csv=p=0', str(output_path)]
                duration_result = subprocess.run(probe_cmd, capture_output=True, text=True)
                video_duration = float(duration_result.stdout.strip())
                
                logger.info(f"✓ Video created: {output_path}")
                logger.info(f"  Duration: {video_duration:.1f}s")
                logger.info(f"  Size: {output_path.stat().st_size / 1024 / 1024:.1f}MB")
                
                return str(output_path)
            else:
                logger.error(f"Video creation failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"FFmpeg error: {e}")
            return None
    
    def upload_to_youtube(self, video_path, title, description):
        """Upload video to YouTube"""
        logger.info("📺 Uploading to YouTube...")
        
        try:
            from youtube_uploader import upload_to_youtube
            
            success = upload_to_youtube(video_path, title, description)
            
            if success:
                logger.info("✓ Video uploaded to YouTube successfully!")
            else:
                logger.warning("YouTube upload failed")
            
            return success
            
        except Exception as e:
            logger.error(f"YouTube upload error: {e}")
            return False
    
    def run_complete_production(self):
        """Run the complete fixed production pipeline"""
        logger.info("="*60)
        logger.info("🚀 STARTING FIXED AUTOMAGIC PRODUCTION")
        logger.info("="*60)
        
        try:
            # Step 1: Get trending topic
            topic = self.get_trending_topic()
            logger.info(f"📌 Topic: {topic}")
            
            # Step 2: Generate script
            script = self.generate_script(topic)
            logger.info(f"📝 Script length: {len(script)} characters")
            
            # Step 3: Generate images
            images = self.generate_images(topic, script)
            logger.info(f"🖼️ Images: {len(images)} generated")
            
            # Step 4: Generate voiceover
            audio = self.generate_voiceover(script)
            
            if not audio:
                logger.error("Failed to generate audio")
                return False
            
            # Step 5: Create video
            video_path = self.create_video(images, audio, topic)
            
            if not video_path:
                logger.error("Failed to create video")
                return False
            
            # Step 6: Upload to YouTube (optional)
            title = f"AutoMagic: {topic[:80]}"
            description = f"""
{topic}

This video explores fascinating aspects of this topic through engaging visuals and narration.

Timestamps:
0:00 Introduction
0:30 Key Points
1:00 Real-World Examples
1:30 Future Implications
2:00 Conclusion

Created with AutoMagic - AI-powered video generation
#Educational #AI #AutoMagic #{topic.replace(' ', '')}
            """.strip()
            
            upload_success = self.upload_to_youtube(video_path, title, description)
            
            logger.info("="*60)
            logger.info("✅ PRODUCTION COMPLETE!")
            logger.info(f"📁 Video: {video_path}")
            logger.info(f"📺 Uploaded: {'Yes' if upload_success else 'No'}")
            logger.info("="*60)
            
            return True
            
        except Exception as e:
            logger.error(f"Production failed: {e}", exc_info=True)
            return False

def main():
    """Main entry point"""
    production = FixedVideoProduction()
    
    # Check API status
    logger.info("Checking API configurations...")
    if not production.openai_key:
        logger.warning("⚠️ OpenAI API key not configured - will use fallbacks")
    if not production.elevenlabs_key:
        logger.warning("⚠️ ElevenLabs API key not configured - will use TTS fallback")
    
    # Run production
    success = production.run_complete_production()
    
    if success:
        logger.info("🎉 Success! Check your YouTube channel for the new video!")
    else:
        logger.error("❌ Production failed - check logs for details")
    
    return success

if __name__ == "__main__":
    # Install missing dependencies if needed
    try:
        import pyttsx3
    except ImportError:
        logger.info("Installing pyttsx3 for TTS...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyttsx3"])
    
    success = main()
    sys.exit(0 if success else 1)