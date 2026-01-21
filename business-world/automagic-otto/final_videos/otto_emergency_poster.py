import os
import sys

# Print Python environment details for debugging
print(f"DEBUG: Python Executable: {sys.executable}")
print(f"DEBUG: Python Version: {sys.version}")
print(f"DEBUG: sys.path: {sys.path}")

import uuid
import datetime
import argparse
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip

# Insert script directory resolution
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Define project root as parent of script directory
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
# switch to project root so relative paths resolve correctly
os.chdir(PROJECT_ROOT)

# ========== CONFIG ==========
POST_TEXT = (
    "I bend time with my breath and rebuild cities in silence.\n"
    "They wanted peace—I gave 'em pressure.\n"
    "My thoughts don't echo—they detonate.\n"
    "You lookin' for calm? Wrong channel.\n"
    "This frequency don't soothe—it slaps."
)
# Font fallback system with multiple options
FONT_PATHS = {
    "linux": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
    ],
    "windows": [
        r"C:\Windows\Fonts\Arial.ttf",
        r"C:\Windows\Fonts\ArialBD.ttf",
        r"C:\Windows\Fonts\Calibri.ttf"
    ],
    "darwin": [
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/SFNSDisplay-Bold.otf",
        "/System/Library/Fonts/Helvetica.ttc"
    ]
}

# Select appropriate font paths list based on operating system
if os.name == "nt":
    FONT_PATH_LIST = FONT_PATHS["windows"]
elif sys.platform == "darwin":
    FONT_PATH_LIST = FONT_PATHS["darwin"]
else:
    FONT_PATH_LIST = FONT_PATHS["linux"]

# Use first font path as default
FONT_PATH = FONT_PATH_LIST[0]

IMAGE_SIZE = (1080, 1080)
FONT_SIZE = 36
VIDEO_DURATION = 20
# directories relative to project root
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "final_videos")
# use existing generated_images folder
SAVE_DIRECTORY = os.path.join(PROJECT_ROOT, "generated_images")

# ========== SETUP ==========
os.makedirs(SAVE_DIRECTORY, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_available_font(font_paths):
    """Try to find an available font from the provided list."""
    for path in font_paths:
        if os.path.exists(path):
            try:
                # Test if font can be loaded
                ImageFont.truetype(path, 12)
                return path
            except Exception:
                continue
    
    # If no font is found, use default PIL font
    print("WARNING: No suitable font found. Using default font.")
    return None

def smart_text_wrap(text, font, max_width):
    """Respects explicit newlines while also wrapping long lines."""
    lines = []
    for line in text.split('\n'):
        if not line:
            lines.append('')
            continue
            
        # Split long lines
        if font.getlength(line) <= max_width:
            lines.append(line)
        else:
            words = line.split(' ')
            current_line = words[0]
            
            for word in words[1:]:
                test_line = current_line + ' ' + word
                if font.getlength(test_line) <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
                
    return lines

def create_image(text, save_dir, font_path):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(save_dir, f"otto_img_{uuid.uuid4().hex[:6]}.png")
    img = Image.new("RGB", IMAGE_SIZE, color=(10, 10, 10))
    draw = ImageDraw.Draw(img)
    
    # Get a valid font or use default
    font_path = get_available_font(FONT_PATH_LIST) if font_path == FONT_PATH else font_path
    
    try:
        font = ImageFont.truetype(font_path, FONT_SIZE) if font_path else ImageFont.load_default()
    except Exception as e:
        print(f"Font error: {e}, using default")
        font = ImageFont.load_default()
    
    # Smart text wrapping
    max_width = IMAGE_SIZE[0] - 80  # 40px padding on each side
    lines = smart_text_wrap(text, font, max_width)
    
    # Calculate text height for vertical centering
    line_height = font.getbbox("Ay")[3] + 10  # Approximate line height with padding
    total_height = line_height * len(lines)
    y_position = max(100, (IMAGE_SIZE[1] - total_height) // 2)
    
    # Draw each line
    for line in lines:
        draw.text((40, y_position), line, fill=(255, 255, 255), font=font)
        y_position += line_height
    
    img.save(filename)
    return filename

def build_video(image_path, duration, out_dir):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
        
    clip = ImageClip(image_path).set_duration(duration)
    zoom = clip.resize(lambda t: 1 + 0.02 * t).set_position("center")
    out = os.path.join(out_dir, f"otto_video_{uuid.uuid4().hex[:6]}.mp4")
    # video processing logs controlled by debug flag
    verbose = getattr(build_video, 'verbose', False)
    logger = 'bar' if verbose else None
    
    try:
        zoom.write_videofile(out, fps=24, verbose=verbose, logger=logger)
        return out
    except Exception as e:
        print(f"Video generation error: {e}")
        # Try with simpler settings if initial attempt fails
        try:
            print("Retrying with simpler video settings...")
            clip.write_videofile(out, fps=24, verbose=verbose, logger=logger)
            return out
        except Exception as e2:
            print(f"Failed to create video with simpler settings: {e2}")
            raise

def main():
    parser = argparse.ArgumentParser(description="Generate Otto poster video")
    parser.add_argument("--text", default=POST_TEXT, help="Post copy text")
    parser.add_argument("--font", default=FONT_PATH, help="Path to TTF font")
    parser.add_argument("--out-img-dir", default=SAVE_DIRECTORY)
    parser.add_argument("--out-vid-dir", default=OUTPUT_DIR)
    parser.add_argument("--duration", type=int, default=VIDEO_DURATION)
    parser.add_argument("--debug", action="store_true", help="Enable debug mode with verbose logs")
    args = parser.parse_args()

    print("🚀 OTTO EMERGENCY POST RUNNING…")
    # setup debug for build_video
    setattr(build_video, 'verbose', args.debug)
    try:
        img = create_image(args.text, args.out_img_dir, args.font)
        print(f"🖼️  Image created: {img}")
        vid = build_video(img, args.duration, args.out_vid_dir)
        print(f"✅ VIDEO READY: {vid}")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    main()