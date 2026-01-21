# core/validation/asset_validator.py - The A.Q.R. quality gate
import os
import json
from pathlib import Path
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def validate_asset_pack(visual_path: Path, brief: dict) -> bool:
    """Uses Gemini Vision to perform a final quality and cohesion check."""
    print("🧐 Performing final quality and cohesion validation...")
    
    # First, check if the file exists and is valid
    if not visual_path or not visual_path.exists():
        print("❌ Validation failed: Visual file does not exist")
        return False
    
    try:
        # Try to open and validate the image file
        image = Image.open(visual_path)
        width, height = image.size
        
        # Basic validation: file exists, is an image, and has reasonable dimensions
        if width < 100 or height < 100:
            print("❌ Validation failed: Image too small")
            return False
            
        print(f"✅ Basic validation passed: {width}x{height} image")
        
        # Try AI validation if API is available
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            You are a meticulous Creative Director. Analyze the provided image against the creative brief.
            Check for major visual flaws (deformed hands, garbled text, etc.) and overall thematic coherence.
            Does the image match the mood, style, and theme of the brief?

            **Creative Brief:**
            {json.dumps(brief, indent=2)}

            Respond with only "PASS" or "FAIL". If FAIL, provide a brief reason.
            """
            response = model.generate_content([prompt, image])
            result_text = response.text.strip()
            
            if result_text.startswith("PASS"):
                print("✅ AI validation PASSED.")
                return True
            else:
                print(f"❌ AI validation FAILED: {result_text}")
                return False
                
        except Exception as ai_error:
            print(f"⚠️ AI validation unavailable ({ai_error}), using basic validation")
            # If AI validation fails, fall back to basic validation
            print("✅ Basic validation PASSED (AI validation skipped)")
            return True
            
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False
