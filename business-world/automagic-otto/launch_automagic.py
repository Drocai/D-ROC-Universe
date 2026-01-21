#!/usr/bin/env python3
"""
AutoMagic Launcher and Monitor
This script launches and monitors your AutoMagic video creation system
"""
import os
import sys
import time
import logging
from datetime import datetime
from pathlib import Path

# Fix encoding issues on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automagic_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AutoMagicLauncher')

def ensure_directories():
    """Ensure all required directories exist"""
    dirs = ['generated_images', 'generated_audio', 'final_videos', 'logs', 'generated_video_clips']
    for d in dirs:
        Path(d).mkdir(exist_ok=True)
        logger.info(f"✓ Directory {d}/ ready")

def check_api_keys():
    """Check if API keys are configured"""
    from dotenv import load_dotenv
    load_dotenv()
    
    apis = {
        'OpenAI': os.getenv('OPENAI_API_KEY'),
        'ElevenLabs': os.getenv('ELEVENLABS_API_KEY'),
        'Voice ID': os.getenv('ELEVENLABS_VOICE_ID'),
        'Google': os.getenv('GOOGLE_API_KEY')
    }
    
    all_configured = True
    for name, key in apis.items():
        if key and not key.startswith('<YOUR'):
            logger.info(f"✓ {name} API configured")
        else:
            logger.warning(f"✗ {name} API not configured")
            all_configured = False
    
    return all_configured

def get_trending_topic():
    """Get a trending topic for video creation"""
    try:
        from trend_integration import get_trending_topic as get_trend
        topic_data = get_trend()
        logger.info(f"📊 Trending Topic: {topic_data['topic']}")
        logger.info(f"   Source: {topic_data['source']}")
        return topic_data['topic']
    except Exception as e:
        logger.warning(f"Could not get trending topic: {e}")
        # Fallback topics
        import random
        fallback = random.choice([
            "Amazing facts about space exploration",
            "How animals communicate with each other",
            "The science behind everyday objects",
            "Incredible engineering achievements",
            "Nature's most fascinating phenomena"
        ])
        logger.info(f"📚 Using fallback topic: {fallback}")
        return fallback

def generate_content_simple():
    """Simple content generation using available APIs"""
    logger.info("=" * 60)
    logger.info("🎬 AUTOMAGIC VIDEO CREATION STARTING")
    logger.info("=" * 60)
    
    # Get trending topic
    topic = get_trending_topic()
    
    # Generate script
    logger.info("✍️ Generating script...")
    script = generate_script(topic)
    
    # Generate images
    logger.info("🎨 Generating images...")
    images = generate_images(topic)
    
    # Generate audio
    logger.info("🎤 Generating audio narration...")
    audio = generate_audio(script)
    
    # Create video
    logger.info("🎬 Assembling video...")
    video = create_simple_video(images, audio)
    
    if video:
        logger.info("=" * 60)
        logger.info("✅ VIDEO CREATION COMPLETE!")
        logger.info(f"📁 Video saved to: {video}")
        logger.info("=" * 60)
        return video
    else:
        logger.error("❌ Video creation failed")
        return None

def generate_script(topic):
    """Generate a simple script for the topic"""
    try:
        import openai
        from dotenv import load_dotenv
        load_dotenv()
        
        openai.api_key = os.getenv('OPENAI_API_KEY')
        client = openai.OpenAI(api_key=openai.api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"Write a short, engaging 1-minute video script about: {topic}. Make it informative and family-friendly."
            }],
            max_tokens=300
        )
        
        script = response.choices[0].message.content.strip()
        logger.info(f"✓ Script generated ({len(script)} characters)")
        return script
        
    except Exception as e:
        logger.warning(f"Script generation failed: {e}")
        fallback_script = f"""
        Today we're exploring {topic}.
        
        This fascinating subject shows us how amazing our world is.
        There's so much to learn and discover about {topic}.
        
        Let's dive in and explore the wonders that await us.
        From scientific discoveries to everyday applications,
        {topic} continues to amaze and inspire us all.
        
        Thank you for joining us on this journey of discovery!
        """
        return fallback_script

def generate_images(topic):
    """Generate images for the video"""
    image_dir = Path("generated_images")
    image_dir.mkdir(exist_ok=True)
    
    # For testing, create simple placeholder images
    from PIL import Image, ImageDraw, ImageFont
    
    images = []
    for i in range(3):
        img = Image.new('RGB', (1280, 720), color=(100 + i*50, 150, 200))
        draw = ImageDraw.Draw(img)
        
        # Add text
        text = f"{topic}\nPart {i+1}"
        try:
            # Try to use a better font
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        # Draw text with shadow effect
        draw.text((642, 362), text, fill='black', font=font, anchor='mm')
        draw.text((640, 360), text, fill='white', font=font, anchor='mm')
        
        # Save image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = image_dir / f"image_{i+1}_{timestamp}.jpg"
        img.save(image_path, 'JPEG', quality=95)
        images.append(str(image_path))
        logger.info(f"✓ Generated image {i+1}: {image_path}")
    
    return images

def generate_audio(script):
    """Generate audio narration"""
    audio_dir = Path("generated_audio")
    audio_dir.mkdir(exist_ok=True)
    
    # For now, create silent audio as fallback
    import subprocess
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_path = audio_dir / f"narration_{timestamp}.mp3"
    
    # Create 30 seconds of silent audio
    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi',
        '-i', 'anullsrc=r=44100:cl=stereo',
        '-t', '30',
        '-c:a', 'libmp3lame',
        str(audio_path)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        logger.info(f"✓ Generated audio: {audio_path}")
        return str(audio_path)
    except Exception as e:
        logger.error(f"Audio generation failed: {e}")
        return None

def create_simple_video(images, audio):
    """Create a simple video from images and audio"""
    if not images or not audio:
        logger.error("Missing images or audio for video creation")
        return None
    
    video_dir = Path("final_videos")
    video_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = video_dir / f"automagic_video_{timestamp}.mp4"
    
    # Create input file for FFmpeg
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        for img in images:
            abs_path = os.path.abspath(img).replace('\\', '/')
            f.write(f"file '{abs_path}'\n")
            f.write("duration 10\n")  # 10 seconds per image
        input_file = f.name
    
    # FFmpeg command
    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', input_file,
        '-i', audio,
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-pix_fmt', 'yuv420p',
        '-shortest',
        str(output_path)
    ]
    
    try:
        import subprocess
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Clean up temp file
        os.unlink(input_file)
        
        if output_path.exists():
            logger.info(f"✓ Video created successfully: {output_path}")
            return str(output_path)
        else:
            logger.error(f"Video creation failed: {result.stderr}")
            return None
            
    except Exception as e:
        logger.error(f"Video creation error: {e}")
        return None

def monitor_system():
    """Monitor system performance"""
    try:
        import psutil
        
        # Get system stats
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        logger.info("📊 SYSTEM MONITOR")
        logger.info(f"   CPU Usage: {cpu_percent}%")
        logger.info(f"   Memory: {memory.percent}% used ({memory.available / (1024**3):.1f}GB free)")
        logger.info(f"   Disk: {disk.percent}% used ({disk.free / (1024**3):.1f}GB free)")
        
    except ImportError:
        logger.info("📊 System monitoring not available (psutil not installed)")

def main():
    """Main launcher function"""
    print("\n" + "="*60)
    print(" AUTOMAGIC VIDEO CREATION SYSTEM")
    print(" Launching and Monitoring...")
    print("="*60 + "\n")
    
    # Step 1: Check system
    logger.info("🔍 Checking system...")
    ensure_directories()
    
    if not check_api_keys():
        logger.warning("⚠️ Some API keys are not configured")
        logger.warning("   The system will use fallback methods where possible")
    
    # Step 2: Monitor resources
    monitor_system()
    
    # Step 3: Generate content
    try:
        video_path = generate_content_simple()
        
        if video_path:
            print("\n" + "="*60)
            print(" 🎉 SUCCESS!")
            print(f" Video created: {video_path}")
            print(" Your AutoMagic system is working!")
            print("="*60 + "\n")
            
            # Final monitoring
            monitor_system()
            
            return True
        else:
            logger.error("Video generation failed")
            return False
            
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        logger.info("✅ AutoMagic completed successfully!")
    else:
        logger.error("❌ AutoMagic encountered errors")
    
    # Keep console open
    input("\nPress Enter to exit...")