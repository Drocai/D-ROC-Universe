#!/usr/bin/env python3
"""
AutoMagic with Multi-Provider Support
Enhanced version with automatic fallbacks for all API services
"""

import os
import sys
import logging
import tempfile
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Import the new provider system
from api_providers import ProviderManager

load_dotenv()

# Configure logging
log_path = os.getenv("LOG_FILE_PATH", "logs/automagic_multi.log")
os.makedirs(os.path.dirname(log_path), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("AutoMagic.MultiProvider")


class MultiProviderVideoProduction:
    """Video production using multiple API providers with automatic fallbacks"""

    def __init__(self):
        self.logger = logger
        self.provider_manager = ProviderManager()

        # Create directories
        for dir_path in [
            os.getenv("IMAGE_SAVE_PATH", "generated_images/"),
            os.getenv("AUDIO_SAVE_PATH", "generated_audio/"),
            os.getenv("FINAL_VIDEO_SAVE_PATH", "final_videos/")
        ]:
            os.makedirs(dir_path, exist_ok=True)

        # Check provider status
        self._check_providers()

    def _check_providers(self):
        """Check which providers are available"""
        self.logger.info("Checking provider availability...")
        status = self.provider_manager.get_status()

        # Check each category
        script_ready = any(p["connected"] for p in status["script_providers"])
        image_ready = any(p["connected"] for p in status["image_providers"])
        voice_ready = any(p["connected"] for p in status["voice_providers"])

        if not (script_ready and image_ready and voice_ready):
            self.logger.error("Not all provider categories are configured!")
            if not script_ready:
                self.logger.error("  ❌ No script generation providers available")
            if not image_ready:
                self.logger.error("  ❌ No image generation providers available")
            if not voice_ready:
                self.logger.error("  ❌ No voice generation providers available")
            self.logger.error("\nRun 'python setup_providers.py' to configure providers")
            sys.exit(1)

        # Log available providers
        self.logger.info("✅ Providers ready:")
        for p in status["script_providers"]:
            if p["connected"]:
                self.logger.info(f"   📝 {p['name']} (Priority: {p['priority']})")
        for p in status["image_providers"]:
            if p["connected"]:
                self.logger.info(f"   🎨 {p['name']} (Priority: {p['priority']})")
        for p in status["voice_providers"]:
            if p["connected"]:
                self.logger.info(f"   🎤 {p['name']} (Priority: {p['priority']})")

    def generate_content_idea(self):
        """Generate or fetch a content idea"""
        self.logger.info("Generating content idea...")

        # Try to use trending topics if available
        try:
            from working_trend_scraper import get_trending_topics
            topics = get_trending_topics()
            if topics:
                topic = topics[0].get('topic', 'Technology trends')
                self.logger.info(f"Using trending topic: {topic}")
                return topic
        except Exception as e:
            self.logger.debug(f"Trending topics not available: {e}")

        # Fallback topics
        import random
        topics = [
            "The secret to perfect sourdough bread",
            "5 mind-blowing facts about space exploration",
            "How to train your brain to remember anything",
            "The psychology behind procrastination",
            "Unusual morning routines of successful people"
        ]
        return random.choice(topics)

    def generate_script(self, topic: str) -> str:
        """Generate script using available providers with fallback"""
        self.logger.info(f"Generating script for: {topic}")

        try:
            script = self.provider_manager.generate_script_with_fallback(topic)
            self.logger.info(f"✅ Script generated ({len(script)} characters)")
            return script
        except Exception as e:
            self.logger.error(f"All script providers failed: {e}")
            # Return a basic fallback script
            return f"""# {topic}

## Introduction
Today we're exploring an fascinating topic: {topic}

## Main Points
Here are the key things you need to know about this subject.

## Conclusion
Thanks for watching! Don't forget to like and subscribe for more content.
"""

    def generate_images(self, script: str, count: int = 3) -> list:
        """Generate images using available providers with fallback"""
        self.logger.info(f"Generating {count} images...")

        # Use AI to generate relevant image prompts from script content
        try:
            prompt_generation = f"""Analyze this video script and generate {count} detailed image prompts that visually represent the key concepts.

Script:
{script[:1500]}

Generate exactly {count} image prompts (one per line) that:
- Are highly specific to the script content
- Would make great YouTube video thumbnails/B-roll
- Are detailed enough for AI image generation (include style, mood, colors, composition)
- Match the tone and subject matter exactly

Format: Just list the prompts, one per line, no numbering or extra text."""

            response = self.provider_manager.generate_script_with_fallback(
                topic="image_prompts",
                prompt=prompt_generation
            )

            # Parse prompts from response
            prompts = [line.strip() for line in response.split('\n')
                      if line.strip() and not line.startswith('#') and len(line.strip()) > 20][:count]

            self.logger.info(f"Generated {len(prompts)} AI-powered image prompts")

        except Exception as e:
            self.logger.warning(f"Could not generate AI prompts: {e}, using fallback")
            prompts = []

        # Fallback: Extract from script headers
        if len(prompts) < count:
            lines = [line.strip() for line in script.split('\n') if line.strip()]
            for line in lines:
                if line.startswith('#') and len(prompts) < count:
                    prompt = f"Professional photograph: {line.replace('#', '').strip()}, cinematic lighting, 4k quality"
                    prompts.append(prompt)

        # Final fallback: Use script topic keywords
        while len(prompts) < count:
            topic_words = script[:200].replace('#', '').replace('\n', ' ').strip()
            prompts.append(f"High-quality photograph related to: {topic_words}, professional, detailed, cinematic")

        # Generate images
        image_files = []
        for idx, prompt in enumerate(prompts[:count], 1):
            try:
                self.logger.info(f"Generating image {idx}/{count}: {prompt[:50]}...")

                image_data = self.provider_manager.generate_image_with_fallback(prompt)

                # Save image
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                img_path = os.path.join(
                    os.getenv("IMAGE_SAVE_PATH", "generated_images/"),
                    f"image_{idx}_{timestamp}.jpg"
                )

                with open(img_path, 'wb') as f:
                    f.write(image_data)

                image_files.append(img_path)
                self.logger.info(f"✅ Image {idx} saved: {img_path}")

            except Exception as e:
                self.logger.error(f"Failed to generate image {idx}: {e}")
                # Create better placeholder image with gradient
                try:
                    from PIL import Image, ImageDraw, ImageFont
                    import random

                    # Create gradient background
                    img = Image.new('RGB', (1280, 720))
                    draw = ImageDraw.Draw(img)

                    # Nice color schemes
                    colors = [
                        [(25, 42, 86), (220, 107, 107)],  # Navy to coral
                        [(13, 27, 42), (27, 163, 156)],   # Dark blue to teal
                        [(34, 40, 49), (220, 152, 73)],   # Dark to gold
                        [(44, 62, 80), (149, 165, 166)],  # Blue gray
                        [(26, 28, 67), (247, 37, 133)]    # Deep purple to pink
                    ]

                    start_color, end_color = random.choice(colors)

                    # Draw gradient
                    for y in range(720):
                        r = int(start_color[0] + (end_color[0] - start_color[0]) * y / 720)
                        g = int(start_color[1] + (end_color[1] - start_color[1]) * y / 720)
                        b = int(start_color[2] + (end_color[2] - start_color[2]) * y / 720)
                        draw.line([(0, y), (1280, y)], fill=(r, g, b))

                    # Add text with better styling
                    text = prompt[:50] if len(prompt) > 50 else prompt

                    # Try to get a nice font
                    font_size = 48
                    try:
                        font = ImageFont.truetype("arial.ttf", font_size)
                    except:
                        try:
                            font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", font_size)
                        except:
                            font = ImageFont.load_default()

                    # Add semi-transparent overlay for text readability
                    overlay = Image.new('RGBA', (1280, 720), (0, 0, 0, 0))
                    overlay_draw = ImageDraw.Draw(overlay)
                    overlay_draw.rectangle([(100, 300), (1180, 420)], fill=(0, 0, 0, 120))
                    img.paste(Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB'))

                    # Draw text
                    draw = ImageDraw.Draw(img)
                    bbox = draw.textbbox((640, 360), text, font=font, anchor="mm")
                    draw.text((640, 360), text, fill=(255, 255, 255), font=font, anchor="mm")

                    placeholder_path = os.path.join(
                        os.getenv("IMAGE_SAVE_PATH", "generated_images/"),
                        f"placeholder_{idx}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    )
                    img.save(placeholder_path, quality=95)
                    image_files.append(placeholder_path)
                    self.logger.info(f"Created enhanced placeholder: {placeholder_path}")
                except Exception as e2:
                    self.logger.error(f"Failed to create placeholder: {e2}")

        return image_files

    def generate_voice(self, script: str) -> str:
        """Generate voice narration using available providers with fallback"""
        self.logger.info("Generating voice narration...")

        # Clean script for narration - remove ALL formatting and notes
        import re

        lines = []
        for line in script.split('\n'):
            # Skip empty lines
            if not line.strip():
                continue
            # Skip markdown headers
            if line.strip().startswith('#'):
                continue
            # Skip lines that are just formatting (**, __, etc)
            if re.match(r'^[\*_\-=]+$', line.strip()):
                continue
            # Remove bold/italic markdown
            line = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)
            line = re.sub(r'\*([^*]+)\*', r'\1', line)
            line = re.sub(r'__([^_]+)__', r'\1', line)
            line = re.sub(r'_([^_]+)_', r'\1', line)
            # Remove anything in parentheses (stage directions)
            line = re.sub(r'\([^)]*\)', '', line)
            # Remove anything in square brackets [notes]
            line = re.sub(r'\[[^\]]*\]', '', line)
            # Remove timestamps like (0:00 - 0:30)
            line = re.sub(r'\(\d+:\d+[^)]*\)', '', line)
            # Clean up extra whitespace
            line = ' '.join(line.split())

            if line.strip():
                lines.append(line.strip())

        narration_text = ' '.join(lines)

        try:
            audio_data = self.provider_manager.generate_voice_with_fallback(narration_text)

            # Save audio
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_path = os.path.join(
                os.getenv("AUDIO_SAVE_PATH", "generated_audio/"),
                f"narration_{timestamp}.mp3"
            )

            with open(audio_path, 'wb') as f:
                f.write(audio_data)

            self.logger.info(f"✅ Voice generated: {audio_path}")
            return audio_path

        except Exception as e:
            self.logger.error(f"All voice providers failed: {e}")
            # Create silent audio as fallback
            audio_path = os.path.join(
                os.getenv("AUDIO_SAVE_PATH", "generated_audio/"),
                f"silent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
            )

            try:
                subprocess.run(
                    ['ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
                     '-t', '20', '-q:a', '9', '-acodec', 'libmp3lame', audio_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True
                )
                self.logger.info(f"Created silent fallback audio: {audio_path}")
            except Exception as e2:
                self.logger.error(f"Failed to create fallback audio: {e2}")

            return audio_path

    def _get_audio_duration(self, audio_file: str) -> float:
        """Get duration of audio file in seconds"""
        try:
            import ffmpeg
            probe = ffmpeg.probe(audio_file)
            duration = float(probe['streams'][0]['duration'])
            return duration
        except Exception as e:
            self.logger.warning(f"Could not get audio duration: {e}, defaulting to 30s")
            return 30.0

    def _apply_ken_burns(self, image_path: str, output_path: str, duration: float, effect_type: int) -> bool:
        """Apply Ken Burns effect (pan/zoom) to a single image"""
        fps = 25
        frames = int(duration * fps)

        # Different Ken Burns effects
        effects = [
            # Slow zoom in from center
            f"zoompan=z='min(zoom+0.001,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1280x720:fps={fps}",
            # Slow zoom out
            f"zoompan=z='if(lte(zoom,1.0),1.3,max(1.001,zoom-0.001))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1280x720:fps={fps}",
            # Pan left to right with slight zoom
            f"zoompan=z='1.15':x='if(lte(on,1),0,min(x+2,iw-iw/zoom))':y='ih/2-(ih/zoom/2)':d={frames}:s=1280x720:fps={fps}",
            # Pan right to left with slight zoom
            f"zoompan=z='1.15':x='if(lte(on,1),iw-iw/zoom,max(x-2,0))':y='ih/2-(ih/zoom/2)':d={frames}:s=1280x720:fps={fps}",
            # Zoom in on upper portion
            f"zoompan=z='min(zoom+0.001,1.25)':x='iw/2-(iw/zoom/2)':y='if(lte(zoom,1.0),ih/3,ih/3-(ih/zoom/6))':d={frames}:s=1280x720:fps={fps}",
        ]

        effect = effects[effect_type % len(effects)]

        try:
            cmd = [
                'ffmpeg', '-y', '-loop', '1', '-i', image_path,
                '-vf', effect,
                '-t', str(duration),
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                output_path
            ]
            result = subprocess.run(cmd, capture_output=True, timeout=120)
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Ken Burns effect failed: {e}")
            return False

    def create_video(self, image_files: list, audio_file: str) -> str:
        """Create final video with Ken Burns effects from images and audio"""
        self.logger.info("Creating video with Ken Burns effects...")

        if not image_files:
            self.logger.error("No images provided for video creation")
            return None

        # Create output path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_path = os.path.join(
            os.getenv("FINAL_VIDEO_SAVE_PATH", "final_videos/"),
            f"automagic_video_{timestamp}.mp4"
        )

        try:
            import ffmpeg

            # Get audio duration to properly time images
            audio_duration = self._get_audio_duration(audio_file)
            num_images = len(image_files)

            # Calculate duration per image (distribute evenly across audio)
            duration_per_image = audio_duration / num_images
            self.logger.info(f"Audio: {audio_duration:.1f}s, Images: {num_images}, Duration per image: {duration_per_image:.1f}s")

            # Apply Ken Burns effect to each image
            clip_files = []
            for i, img in enumerate(image_files):
                clip_path = tempfile.mktemp(suffix=f'_clip{i}.mp4')
                self.logger.info(f"Applying Ken Burns effect to image {i+1}/{num_images}...")

                if self._apply_ken_burns(img, clip_path, duration_per_image, i):
                    clip_files.append(clip_path)
                else:
                    self.logger.warning(f"Ken Burns failed for image {i+1}, using static fallback")
                    # Fallback to static image
                    cmd = [
                        'ffmpeg', '-y', '-loop', '1', '-i', img,
                        '-vf', 'scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2',
                        '-t', str(duration_per_image),
                        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                        clip_path
                    ]
                    subprocess.run(cmd, capture_output=True, timeout=60)
                    clip_files.append(clip_path)

            # Create concat file for the clips
            concat_file = tempfile.mktemp(suffix='.txt')
            with open(concat_file, 'w') as f:
                for clip in clip_files:
                    f.write(f"file '{clip.replace(chr(92), '/')}'\n")

            # Concatenate all clips
            silent_video = tempfile.mktemp(suffix='.mp4')
            concat_cmd = [
                'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_file,
                '-c', 'copy', silent_video
            ]
            subprocess.run(concat_cmd, capture_output=True, timeout=120)

            # Add audio
            final_cmd = [
                'ffmpeg', '-y', '-i', silent_video, '-i', audio_file,
                '-c:v', 'copy', '-c:a', 'aac', '-t', str(audio_duration),
                video_path
            ]
            subprocess.run(final_cmd, capture_output=True, timeout=120)

            # Cleanup
            os.remove(concat_file)
            os.remove(silent_video)
            for clip in clip_files:
                if os.path.exists(clip):
                    os.remove(clip)

            self.logger.info(f"Video created: {video_path}")
            return video_path

        except Exception as e:
            self.logger.error(f"Video creation failed: {e}")
            return None

    def verify_production(self, images: list, audio: str, video: str) -> dict:
        """
        Verify all production outputs meet quality standards.
        Returns dict with pass/fail status and details for each check.
        """
        results = {
            "passed": True,
            "checks": {},
            "errors": []
        }

        # Check 1: Images generated (not placeholders)
        check_name = "images_generated"
        if not images or len(images) == 0:
            results["checks"][check_name] = {"passed": False, "detail": "No images generated"}
            results["errors"].append("No images generated")
            results["passed"] = False
        else:
            placeholder_count = sum(1 for img in images if "placeholder" in img.lower())
            if placeholder_count > 0:
                results["checks"][check_name] = {
                    "passed": False,
                    "detail": f"{placeholder_count}/{len(images)} are placeholders"
                }
                results["errors"].append(f"{placeholder_count} placeholder images used instead of AI-generated")
                results["passed"] = False
            else:
                results["checks"][check_name] = {"passed": True, "detail": f"{len(images)} AI-generated images"}

        # Check 2: Image file sizes (should be substantial, not tiny placeholders)
        check_name = "image_quality"
        min_size = 30000  # 30KB minimum for real images
        small_images = []
        for img in images:
            if os.path.exists(img):
                size = os.path.getsize(img)
                if size < min_size:
                    small_images.append((img, size))
        if small_images:
            results["checks"][check_name] = {
                "passed": False,
                "detail": f"{len(small_images)} images under {min_size/1000}KB"
            }
            results["errors"].append(f"Low quality images detected: {small_images}")
            results["passed"] = False
        else:
            results["checks"][check_name] = {"passed": True, "detail": "All images meet size threshold"}

        # Check 3: Audio file exists and has content
        check_name = "audio_generated"
        if not audio or not os.path.exists(audio):
            results["checks"][check_name] = {"passed": False, "detail": "Audio file not found"}
            results["errors"].append("Audio file not generated")
            results["passed"] = False
        else:
            audio_size = os.path.getsize(audio)
            if audio_size < 10000:  # Less than 10KB is suspicious
                results["checks"][check_name] = {
                    "passed": False,
                    "detail": f"Audio too small ({audio_size} bytes)"
                }
                results["errors"].append("Audio file too small - may be silent/corrupted")
                results["passed"] = False
            else:
                results["checks"][check_name] = {"passed": True, "detail": f"Audio: {audio_size/1000:.1f}KB"}

        # Check 4: Audio duration is reasonable (10-120 seconds for short-form)
        check_name = "audio_duration"
        try:
            audio_duration = self._get_audio_duration(audio)
            if audio_duration < 10:
                results["checks"][check_name] = {
                    "passed": False,
                    "detail": f"Audio too short ({audio_duration:.1f}s)"
                }
                results["errors"].append(f"Audio only {audio_duration:.1f}s - too short")
                results["passed"] = False
            elif audio_duration > 180:
                results["checks"][check_name] = {
                    "passed": False,
                    "detail": f"Audio too long ({audio_duration:.1f}s)"
                }
                results["errors"].append(f"Audio {audio_duration:.1f}s - exceeds limit")
                results["passed"] = False
            else:
                results["checks"][check_name] = {"passed": True, "detail": f"Duration: {audio_duration:.1f}s"}
        except Exception as e:
            results["checks"][check_name] = {"passed": False, "detail": f"Could not check: {e}"}
            results["errors"].append(f"Audio duration check failed: {e}")

        # Check 5: Video file exists and has content
        check_name = "video_created"
        if not video or not os.path.exists(video):
            results["checks"][check_name] = {"passed": False, "detail": "Video file not found"}
            results["errors"].append("Video file not created")
            results["passed"] = False
        else:
            video_size = os.path.getsize(video)
            if video_size < 100000:  # Less than 100KB is suspicious
                results["checks"][check_name] = {
                    "passed": False,
                    "detail": f"Video too small ({video_size/1000:.1f}KB)"
                }
                results["errors"].append("Video file too small - may be corrupted")
                results["passed"] = False
            else:
                results["checks"][check_name] = {"passed": True, "detail": f"Video: {video_size/1000000:.2f}MB"}

        # Check 6: Video duration matches audio
        check_name = "video_audio_sync"
        try:
            import ffmpeg
            video_probe = ffmpeg.probe(video)
            video_duration = float(video_probe['streams'][0]['duration'])
            audio_duration = self._get_audio_duration(audio)

            diff = abs(video_duration - audio_duration)
            if diff > 2.0:  # More than 2 seconds difference
                results["checks"][check_name] = {
                    "passed": False,
                    "detail": f"Video ({video_duration:.1f}s) != Audio ({audio_duration:.1f}s)"
                }
                results["errors"].append(f"Video/audio duration mismatch: {diff:.1f}s difference")
                results["passed"] = False
            else:
                results["checks"][check_name] = {
                    "passed": True,
                    "detail": f"Synced (diff: {diff:.1f}s)"
                }
        except Exception as e:
            results["checks"][check_name] = {"passed": False, "detail": f"Could not verify: {e}"}

        return results

    def print_verification_report(self, results: dict):
        """Print a formatted verification report"""
        print("\n" + "="*60)
        print("VERIFICATION REPORT")
        print("="*60)

        for check_name, check_result in results["checks"].items():
            status = "PASS" if check_result["passed"] else "FAIL"
            symbol = "[OK]" if check_result["passed"] else "[FAIL]"
            print(f"  {symbol} {check_name}: {check_result['detail']}")

        print("-"*60)
        if results["passed"]:
            print("  OVERALL: ALL CHECKS PASSED")
        else:
            print("  OVERALL: FAILED")
            print("\n  Errors:")
            for error in results["errors"]:
                print(f"    - {error}")

        print("="*60 + "\n")

    def run_production(self):
        """Run the complete video production pipeline with verification"""
        self.logger.info("="*60)
        self.logger.info("STARTING AUTOMAGIC PRODUCTION (MULTI-PROVIDER)")
        self.logger.info("="*60)

        images = []
        audio = None
        video = None

        try:
            # Step 1: Generate content idea
            topic = self.generate_content_idea()
            self.logger.info(f"Topic: {topic}")

            # Step 2: Generate script
            script = self.generate_script(topic)

            # Step 3: Generate images
            images = self.generate_images(script)

            # Step 4: Generate voice
            audio = self.generate_voice(script)

            # Step 5: Create video
            video = self.create_video(images, audio)

            # Step 6: VERIFY all outputs
            self.logger.info("Running verification checks...")
            verification = self.verify_production(images, audio, video)
            self.print_verification_report(verification)

            if verification["passed"]:
                self.logger.info("="*60)
                self.logger.info("PRODUCTION COMPLETE - ALL CHECKS PASSED!")
                self.logger.info(f"Video: {video}")
                self.logger.info("="*60)
                return {"success": True, "video": video, "verification": verification}
            else:
                self.logger.error("="*60)
                self.logger.error("PRODUCTION FAILED VERIFICATION")
                for error in verification["errors"]:
                    self.logger.error(f"  - {error}")
                self.logger.error("="*60)
                return {"success": False, "video": video, "verification": verification}

        except Exception as e:
            self.logger.error(f"Production error: {e}", exc_info=True)
            return {"success": False, "video": None, "error": str(e)}


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='AutoMagic Multi-Provider')
    parser.add_argument('--now', action='store_true', help='Run immediately')
    parser.add_argument('--status', action='store_true', help='Show provider status')
    args = parser.parse_args()

    if args.status:
        # Show status only
        manager = ProviderManager()
        status = manager.get_status()

        print("\n" + "="*60)
        print("PROVIDER STATUS")
        print("="*60)

        print("\n📝 Script Providers:")
        for p in status["script_providers"]:
            symbol = "✅" if p["connected"] else "⚠️" if p["available"] else "❌"
            print(f"  {symbol} {p['name']} (Priority: {p['priority']})")

        print("\n🎨 Image Providers:")
        for p in status["image_providers"]:
            symbol = "✅" if p["connected"] else "⚠️" if p["available"] else "❌"
            print(f"  {symbol} {p['name']} (Priority: {p['priority']})")

        print("\n🎤 Voice Providers:")
        for p in status["voice_providers"]:
            symbol = "✅" if p["connected"] else "⚠️" if p["available"] else "❌"
            print(f"  {symbol} {p['name']} (Priority: {p['priority']})")

        print("\n" + "="*60)
        return

    # Run production
    production = MultiProviderVideoProduction()

    if args.now:
        result = production.run_production()

        # Exit with appropriate code based on verification
        if result and result.get("success"):
            print(f"\nVideo ready: {result['video']}")
            sys.exit(0)
        else:
            print("\nProduction did not pass verification checks.")
            if result and result.get("verification"):
                print("See errors above for details.")
            sys.exit(1)
    else:
        print("Use --now to run production immediately")
        print("Use --status to check provider configuration")


if __name__ == "__main__":
    main()
