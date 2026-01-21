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

    def create_video(self, image_files: list, audio_file: str) -> str:
        """Create final video from images and audio using ffmpeg"""
        self.logger.info("Creating video...")

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

            # Create concat file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                for img in image_files:
                    abs_path = os.path.abspath(img).replace('\\', '/')
                    f.write(f"file '{abs_path}'\n")
                    f.write("duration 5\n")
                concat_file = f.name

            # Create silent video from images
            silent_video = tempfile.mktemp(suffix='.mp4')

            (
                ffmpeg
                .input(concat_file, format='concat', safe=0)
                .output(silent_video, vcodec='libx264', pix_fmt='yuv420p', r=25)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )

            # Add audio
            video_stream = ffmpeg.input(silent_video)
            audio_stream = ffmpeg.input(audio_file)

            (
                ffmpeg
                .output(video_stream, audio_stream, video_path,
                       vcodec='copy', acodec='aac')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )

            # Cleanup
            os.remove(concat_file)
            os.remove(silent_video)

            self.logger.info(f"✅ Video created: {video_path}")
            return video_path

        except Exception as e:
            self.logger.error(f"Video creation failed: {e}")
            return None

    def run_production(self):
        """Run the complete video production pipeline"""
        self.logger.info("="*60)
        self.logger.info("🎬 STARTING AUTOMAGIC PRODUCTION (MULTI-PROVIDER)")
        self.logger.info("="*60)

        try:
            # Step 1: Generate content idea
            topic = self.generate_content_idea()
            self.logger.info(f"📝 Topic: {topic}")

            # Step 2: Generate script
            script = self.generate_script(topic)

            # Step 3: Generate images
            images = self.generate_images(script)

            # Step 4: Generate voice
            audio = self.generate_voice(script)

            # Step 5: Create video
            video = self.create_video(images, audio)

            if video and os.path.exists(video):
                self.logger.info("="*60)
                self.logger.info("✅ PRODUCTION COMPLETE!")
                self.logger.info(f"📁 Video: {video}")
                self.logger.info("="*60)
                return video
            else:
                self.logger.error("Production failed - video not created")
                return None

        except Exception as e:
            self.logger.error(f"Production error: {e}", exc_info=True)
            return None


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
        production.run_production()
    else:
        print("Use --now to run production immediately")
        print("Use --status to check provider configuration")


if __name__ == "__main__":
    main()
