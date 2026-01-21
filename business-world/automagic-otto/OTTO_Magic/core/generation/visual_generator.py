# core/generation/visual_generator.py - Generates images and video clips
import os
import requests
import time
from pathlib import Path
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
OUTPUT_DIR = Path("generated_assets/visuals")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

def _generate_dalle_image(prompt: str) -> Path | None:
    """Generates a single image using DALL-E 3."""
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1792x1024", # Widescreen for video
            quality="hd",
            response_format="url"
        )
        image_url = response.data[0].url
        img_data = requests.get(image_url).content
        
        img_path = OUTPUT_DIR / f"dalle_image_{int(time.time())}.png"
        with open(img_path, 'wb') as f:
            f.write(img_data)
        return img_path
    except Exception as e:
        print(f"❌ DALL-E 3 image generation failed: {e}")
        return None

def _create_placeholder_image(text: str, output_dir: Path) -> Path | None:
    """Creates a simple placeholder image for testing."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple colored image with text
        img = Image.new('RGB', (1792, 1024), color=(70, 130, 180))  # Steel blue
        draw = ImageDraw.Draw(img)
        
        # Try to use a font, fall back to default if not available
        try:
            font = ImageFont.truetype("arial.ttf", 48)
        except:
            font = ImageFont.load_default()
        
        # Add text
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (1792 - text_width) // 2
        y = (1024 - text_height) // 2
        
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        
        # Save image
        output_dir.mkdir(exist_ok=True, parents=True)
        img_path = output_dir / f"placeholder_{int(time.time())}.png"
        img.save(img_path)
        print(f"✅ Placeholder image created: {img_path}")
        return img_path
    except Exception as e:
        print(f"❌ Placeholder image creation failed: {e}")
        return None

def generate_visuals(brief: dict) -> Path | None:
    """
    Main visual generation function.
    Currently generates a DALL-E image. This will be expanded to create a video clip.
    """
    print("🎨 Generating primary visual...")
    
    # Try to get the visual prompt from the brief
    prompt = brief.get("visual_prompt") or brief.get("positive_prompt") or brief.get("theme", "Abstract AI concept")
    
    # For now, we generate a high-quality image. The video creation will be a separate step.
    image_path = _generate_dalle_image(prompt)
    
    # If DALL-E fails, create a placeholder
    if not image_path:
        print("🔄 Falling back to placeholder image...")
        image_path = _create_placeholder_image(prompt, OUTPUT_DIR)
    
    # Placeholder for future Image-to-Video step
    # video_path = generate_video_from_image(image_path, brief["theme"])
    # return video_path

    return image_path
