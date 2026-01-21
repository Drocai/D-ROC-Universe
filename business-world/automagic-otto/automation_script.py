#!/usr/bin/env python3
# automation_script.py - Main automation script for AutoMagic
import os
import sys
import logging
import schedule
import time
import json
import random
import subprocess
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import ffmpeg  # Added for ffmpeg-python
import tempfile  # Added for temporary files
import openai # Add OpenAI import
import requests # Added for making HTTP requests, e.g., in generate_images
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import shutil
import elevenlabs
# from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Add trend integration
try:
    from trend_integration import get_trending_topic, get_content_adaptation
    TREND_MODULE_AVAILABLE = True
except ImportError:
    TREND_MODULE_AVAILABLE = False

# Add mask_api_key function at the top
def mask_api_key(key):
    """Mask an API key for secure display."""
    if not key or len(key) < 8:
        return "Not configured"
    return f"{key[:4]}...{key[-4:]}"

# Load environment variables
load_dotenv()

# Configure logging
log_path = os.getenv("LOG_FILE_PATH", "logs/automagic.log")
log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO"))
os.makedirs(os.path.dirname(log_path), exist_ok=True) # Corrected this line

logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("AutoMagic")

# Make sure directories exist
for dir_path in [
    os.getenv("IMAGE_SAVE_PATH", "generated_images/"),
    os.getenv("AUDIO_SAVE_PATH", "generated_audio/"),
    os.getenv("FINAL_VIDEO_SAVE_PATH", "final_videos/")
]:
    os.makedirs(dir_path, exist_ok=True)

class VideoProduction:
    def __init__(self):
        self.season = int(os.getenv("SEASON", 1))
        self.day_number = int(os.getenv("DAY_NUMBER", 1))
        self.logger = logger
        
        # Check if required API keys are present
        self._check_api_keys()

        # Initialize API Clients
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.elevenlabs_client = None 
        self._initialize_elevenlabs_client()
        self.youtube_upload_enabled = self._initialize_youtube_client() # Store success/failure


    def _initialize_elevenlabs_client(self):
        """Initialize the ElevenLabs client if the API key is available."""
        elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        if elevenlabs_api_key and not elevenlabs_api_key.startswith("YOUR_"):
            elevenlabs.set_api_key(elevenlabs_api_key)
            self.elevenlabs_client = elevenlabs
            self.logger.info("ElevenLabs client initialized.")
        else:
            self.logger.warning("ElevenLabs API key not configured. Voice generation will be disabled.")

    def _initialize_youtube_client(self):
        """Initialize the YouTube API client."""
        self.logger.info("Initializing YouTube client...")
        creds = None
        token_path = Path(os.getenv("YOUTUBE_TOKEN_PATH", "youtube_token.json"))
        client_secrets_path = Path(os.getenv("YOUTUBE_CLIENT_SECRETS_PATH", "client_secret.json"))

        if not client_secrets_path.exists():
            self.logger.error(f"YouTube client secrets file not found at {client_secrets_path}. Cannot initialize YouTube client.")
            self.logger.error("Please download your client_secret.json from Google Cloud Console and place it in the specified path.")
            return False

        if token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(token_path), scopes=["https://www.googleapis.com/auth/youtube.upload"])
            except Exception as e:
                self.logger.warning(f"Failed to load YouTube credentials from token: {e}. Will attempt to re-authenticate.")
                creds = None # Ensure creds is None if loading fails
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    self.logger.info("YouTube credentials refreshed.")
                except Exception as e:
                    self.logger.error(f"Failed to refresh YouTube credentials: {e}. Need to re-authenticate.")
                    # Attempt to delete the potentially corrupted token file to force re-authentication
                    if token_path.exists():
                        try:
                            token_path.unlink()
                            self.logger.info(f"Removed potentially corrupted token file: {token_path}")
                        except OSError as oe:
                            self.logger.error(f"Error removing token file {token_path}: {oe}")
                    creds = None # Ensure re-authentication flow is triggered
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(client_secrets_path), scopes=["https://www.googleapis.com/auth/youtube.upload"]
                    )
                    # Try to run with a local server, fall back to console if port is occupied or other issues
                    try:
                        creds = flow.run_local_server(port=0)
                    except OSError as e:
                        self.logger.warning(f"Failed to start local server for OAuth: {e}. Falling back to console authentication.")
                        creds = flow.run_console()
                    self.logger.info("YouTube authentication successful.")
                except FileNotFoundError:
                    self.logger.error(f"YouTube client secrets file not found at {client_secrets_path}. Cannot authenticate.")
                    return False
                except Exception as e:
                    self.logger.error(f"Error during YouTube authentication flow: {e}")
                    return False
            
            try:
                with open(str(token_path), 'w') as token_file:
                    token_file.write(creds.to_json())
                self.logger.info(f"YouTube credentials saved to {token_path}")
            except Exception as e:
                self.logger.error(f"Failed to save YouTube token: {e}")

        if creds and creds.valid:
            try:
                self.youtube_client = build("youtube", "v3", credentials=creds)
                self.logger.info("YouTube client initialized successfully.")
                return True
            except Exception as e:
                self.logger.error(f"Failed to build YouTube service: {e}")
                return False
        else:
            self.logger.error("Failed to obtain valid YouTube credentials.")
            return False

    def _check_api_keys(self):
        """Verify that required API keys are present"""
        required_keys = [
            ("OPENAI_API_KEY", "OpenAI"),
            ("ELEVENLABS_API_KEY", "ElevenLabs"),
            ("GOOGLE_API_KEY", "Google Cloud")
        ]
        
        missing_keys = []
        for env_var, name in required_keys:
            value = os.getenv(env_var)
            if not value or value.startswith("YOUR_") or value == "":
                missing_keys.append(name)
        
        if missing_keys:
            self.logger.error(f"Missing required API keys: {', '.join(missing_keys)}")
            self.logger.error("Please check API_SETUP_GUIDE.txt for instructions")
            sys.exit(1)
        else:
            self.logger.info("All required API keys are configured")

    def generate_content_idea(self):
        """Generate a new content idea using AI or trend scraper"""
        self.logger.info("Generating content idea...")
        
        # Try to use trend scraper via integration module
        if TREND_MODULE_AVAILABLE:
            try:
                self.logger.info("Attempting to use trend integration module")
                trend_data = get_trending_topic()
                if trend_data and 'topic' in trend_data:
                    self.logger.info(f"Using trending topic: {trend_data['topic']} from source: {trend_data['source']}")
                    return trend_data['topic']
            except Exception as e:
                self.logger.warning(f"Error using trend integration: {str(e)}")
        
        # Fallback to OpenAI if trend scraper fails or isn't available
        try:
            self.logger.info("Generating content idea using OpenAI...")
            
            # Add retry decorator with exponential backoff for API resilience
            @retry(
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=1, min=2, max=10),
                retry=retry_if_exception_type((openai.RateLimitError, openai.APITimeoutError))
            )
            def _generate_with_openai():
                response = self.openai_client.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                    messages=[
                        {"role": "system", "content": "You are a creative assistant that generates engaging YouTube video ideas."},
                        {"role": "user", "content": "Suggest a short, catchy, and interesting YouTube video topic. The topic should be suitable for a general audience and have potential for visual storytelling. Provide just the topic, nothing else."}
                    ],
                    max_tokens=50,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
                
            topic = _generate_with_openai()
            self.logger.info(f"Generated content idea with OpenAI: {topic}")
            return topic
        except Exception as e:
            self.logger.error(f"Error generating content idea with OpenAI: {e}")
            self.logger.info("Falling back to predefined content ideas")
            
            # Fallback to predefined topics
            topics = [
                "The secret to perfect sourdough bread",
                "5 mind-blowing facts about space exploration",
                "How to train your brain to remember anything",
                "The psychology behind procrastination",
                "Unusual morning routines of successful people"
            ]
            selected_topic = random.choice(topics)
            self.logger.info(f"Using fallback topic: {selected_topic}")
            return selected_topic
    
    def generate_script(self, topic):
        """Generate a video script based on the topic using AI"""
        self.logger.info(f"Generating script for topic: {topic} using OpenAI")
        
        prompt_template = f"""
Create a concise and engaging YouTube video script for the topic: "{topic}".
The script should have the following structure:
1.  **Introduction** (Hook the viewer, introduce the topic) - Approx 2-3 sentences.
2.  **Main Points** (Present 3 key points or segments related to the topic. Each point should be clearly explained) - Approx 2-3 sentences per point.
3.  **Conclusion** (Summarize, call to action e.g., like, subscribe, comment) - Approx 2-3 sentences.

Keep the language simple and conversational. The entire script should be narratable in about 1-2 minutes.
Format the output clearly, for example:

# Video Title: {topic}

## Introduction
...

## Main Point 1
...

## Main Point 2
...

## Main Point 3
...

## Conclusion
...
"""
        try:
            response = self.openai_client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that writes YouTube video scripts."},
                    {"role": "user", "content": prompt_template}
                ],
                max_tokens=500, # Increased max_tokens for a more complete script
                temperature=0.7
            )
            script_content = response.choices[0].message.content.strip()
            self.logger.info(f"Successfully generated script for topic: {topic}")
            return script_content
        except Exception as e:
            self.logger.error(f"Error generating script with OpenAI: {e}")
            self.logger.info("Falling back to simulated script.")
            # Fallback to simulated script
            return f"""
# {topic}

## Introduction
Welcome to another exciting episode! Today we're diving into {topic}. We'll uncover some fascinating aspects about it!

## Main Point 1
First, let's understand the basics of {topic}. It's really interesting how it all works.

## Main Point 2
Next, we'll explore some interesting examples or facts related to {topic}. Prepare to be amazed!

## Main Point 3
Finally, I'll share some practical tips or thoughts on {topic} that you can use or ponder today.

## Conclusion
Thanks for watching! If you enjoyed this video and want to see more content like this, don't forget to like, subscribe, and hit that notification bell!
"""

    def generate_images(self, script):
        """Generate images based on the script using DALL-E via OpenAI client"""
        self.logger.info("Generating images using DALL-E...")
        
        from PIL import Image, ImageDraw, ImageFont # Keep PIL for fallback
        from io import BytesIO # For handling image data from response

        # Extract potential image prompts from script (e.g., from main points)
        lines = script.strip().split('\n')
        image_prompts = []
        collecting = False
        for line in lines:
            if line.startswith("## Main Point"):
                collecting = True
                # Try to extract a concise prompt from the line itself or subsequent lines
                # This is a simple heuristic; more sophisticated NLP could be used
                prompt_candidate = line.replace("## Main Point", "").strip()
                if prompt_candidate and len(prompt_candidate.split()) > 2: # Ensure it's not just "1" or "2"
                    image_prompts.append(f"A visually appealing image representing: {prompt_candidate}")
            elif collecting and line.strip() and not line.startswith("##"):
                # If we are in a main point section, add the first descriptive line as a prompt basis
                if not any(line.startswith(p) for p in image_prompts):
                     image_prompts.append(f"Illustrate: {line.strip()}")
                collecting = False # Assume one key descriptive line per point for simplicity
        
        # If no specific prompts extracted, create generic ones based on topic
        if not image_prompts:
            topic_line = next((line for line in lines if line.startswith("# Video Title:")), script.split('\n')[0])
            topic = topic_line.replace("# Video Title:", "").strip()
            image_prompts = [
                f"A vibrant and engaging image for a YouTube video about {topic}",
                f"An illustrative visual for {topic}",
                f"A conceptual image related to {topic}"
            ]

        image_files = []
        image_save_path = os.getenv("IMAGE_SAVE_PATH", "generated_images/")
        os.makedirs(image_save_path, exist_ok=True)

        for i, prompt in enumerate(image_prompts[:3]): # Generate up to 3 images
            img_path = os.path.join(image_save_path, f"image_dalle_{i+1}.png") # DALL-E often produces PNGs
            try:
                self.logger.info(f"Generating image for prompt: \"{prompt}\"")
                response = self.openai_client.images.generate(
                    model=os.getenv("DALLE_MODEL", "dall-e-2"), # Or "dall-e-3" if available and preferred
                    prompt=prompt,
                    n=1,
                    size=os.getenv("DALLE_IMAGE_SIZE", "1024x1024"), # e.g., "1024x1024", "1792x1024", "1024x1792" for DALL-E 3
                    response_format='url' # Get URL to download image
                )
                
                image_url = response.data[0].url
                self.logger.debug(f"Image URL: {image_url}")

                # Download the image
                image_response = requests.get(image_url, timeout=30)
                image_response.raise_for_status() # Raise an exception for bad status codes
                
                # Save the image
                with open(img_path, 'wb') as f:
                    f.write(image_response.content)
                
                # Verify the image
                if os.path.exists(img_path) and os.path.getsize(img_path) > 0:
                    if self._is_valid_image(img_path): # Reuse existing validation
                        image_files.append(img_path)
                        self.logger.info(f"Successfully generated and saved image: {img_path}")
                    else:
                        self.logger.error(f"DALL-E image saved but failed validation: {img_path}")
                        os.remove(img_path) # Clean up invalid image
                else:
                    self.logger.error(f"Failed to save DALL-E image or image is empty: {img_path}")

            except Exception as e:
                self.logger.error(f"Error generating image with DALL-E for prompt '{prompt}': {e}")
                # Fallback to simple PIL image if DALL-E fails
                self.logger.info(f"Falling back to PIL image generation for image {i+1}")
                try:
                    pil_img_path = os.path.join(image_save_path, f"image_pil_fallback_{i+1}.jpg")
                    width, height = 1280, 720
                    bg_color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
                    img = Image.new('RGB', (width, height), color=bg_color)
                    draw = ImageDraw.Draw(img)
                    try:
                        font_path = "C:\\Windows\\Fonts\\Arial.ttf" if os.name == 'nt' else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
                        if not os.path.exists(font_path): font_path = "/System/Library/Fonts/Helvetica.ttc"
                        font = ImageFont.truetype(font_path, 30) if os.path.exists(font_path) else ImageFont.load_default()
                    except:
                        font = ImageFont.load_default()
                    draw.text((width//2, height//2), f"Fallback Image {i+1}\n{prompt[:50]}...", fill=(255,255,255), font=font, anchor="mm")
                    img.save(pil_img_path, format="JPEG")
                    if self._is_valid_image(pil_img_path):
                        image_files.append(pil_img_path)
                        self.logger.info(f"Successfully generated fallback PIL image: {pil_img_path}")
                    else:
                        self.logger.error(f"Fallback PIL image failed validation: {pil_img_path}")
                except Exception as pil_e:
                    self.logger.error(f"Error generating fallback PIL image: {pil_e}")
        
        if not image_files:
            self.logger.warning("No images were generated successfully. Proceeding without images might cause issues.")
            # Create at least one dummy image if all generations failed, to prevent downstream errors
            try:
                dummy_img_path = os.path.join(image_save_path, "dummy_image.jpg")
                img = Image.new('RGB', (1280, 720), color=(128, 128, 128))
                draw = ImageDraw.Draw(img)
                draw.text((640, 360), "IMAGE GENERATION FAILED", fill=(255,0,0), anchor="mm")
                img.save(dummy_img_path, format="JPEG")
                if self._is_valid_image(dummy_img_path):
                    image_files.append(dummy_img_path)
                    self.logger.info(f"Created a dummy placeholder image: {dummy_img_path}")
            except Exception as dummy_e:
                self.logger.error(f"Failed to create dummy placeholder image: {dummy_e}")

        self.logger.info(f"Generated {len(image_files)} images in total.")
        return image_files

    def _is_valid_image(self, image_path):
        """Check if the file is a valid image by attempting to open it with PIL"""
        try:
            from PIL import Image
            Image.open(image_path)
            return True
        except Exception as e:
            self.logger.error(f"Image validation error for {image_path}: {str(e)}")
            return False
            
    def _is_valid_audio(self, audio_path):
        """Check if the file is a valid audio file by attempting to analyze it with ffmpeg"""
        if not os.path.exists(audio_path):
            self.logger.error(f"Audio file does not exist: {audio_path}")
            return False
            
        # Basic size check - real audio files should be at least 1KB
        min_size = 1000  # bytes
        if os.path.getsize(audio_path) < min_size:
            self.logger.error(f"Audio file too small ({os.path.getsize(audio_path)} bytes): {audio_path}")
            return False
            
        # Extension check
        if not audio_path.lower().endswith(('.mp3', '.wav', '.aac', '.ogg')):
            self.logger.error(f"Audio file has invalid extension: {audio_path}")
            return False
        
        # Try to probe the file with ffmpeg to verify it's a valid audio file
        try:
            import ffmpeg
            probe = ffmpeg.probe(audio_path, v='error')
            # Check if there's at least one audio stream
            audio_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'audio']
            if not audio_streams:
                self.logger.error(f"No audio streams found in file: {audio_path}")
                return False
                
            self.logger.info(f"Validated audio file: {audio_path} - duration: {probe['format'].get('duration', 'unknown')}s")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate audio file {audio_path}: {str(e)}")
            
            # Try alternative validation with subprocess if ffmpeg.probe fails
            try:
                import subprocess
                result = subprocess.run(
                    ['ffmpeg', '-v', 'error', '-i', audio_path, '-f', 'null', '-'],
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    text=True
                )
                
                # If there's no error output, the file is likely valid
                if result.returncode == 0 and not result.stderr.strip():
                    self.logger.info(f"Audio file validated via subprocess: {audio_path}")
                    return True
                else:
                    self.logger.error(f"Audio validation failed (subprocess): {result.stderr}")
                    return False
                    
            except Exception as e2:
                self.logger.error(f"Failed to validate audio with subprocess: {str(e2)}")
                return False
                
    def generate_voice(self, script):
        """Generate voice narration based on the script using ElevenLabs"""
        self.logger.info("Generating voice narration...")
        
        # Extract narration text
        lines = script.strip().split('\n')
        narration_lines = [line for line in lines if not line.startswith('#') and line.strip()]
        narration_text = ' '.join(narration_lines)

        audio_save_path = os.getenv("AUDIO_SAVE_PATH", "generated_audio/")
        os.makedirs(audio_save_path, exist_ok=True)
        audio_path = os.path.join(audio_save_path, "narration.mp3")

        if self.elevenlabs_client:
            try:
                self.logger.info("Using ElevenLabs for voice generation.")
                # Ensure narration_text is not empty
                if not narration_text.strip():
                    self.logger.warning("Narration text is empty. Skipping ElevenLabs generation.")
                    raise ValueError("Narration text is empty")

                # Voice selection (can be configured via .env or hardcoded)
                voice_id = os.getenv("ELEVENLABS_VOICE_ID", "Rachel") # Default to a common voice
                
                # Check if voice_id is one of the standard names or a valid ID
                # This is a simplified check; a more robust solution would list available voices
                available_voices = [v.voice_id for v in self.elevenlabs_client.voices.get_all().voices]
                if voice_id not in available_voices and voice_id not in [v.name for v in self.elevenlabs_client.voices.get_all().voices]:
                    self.logger.warning(f"Voice '{voice_id}' not found. Falling back to first available voice.")
                    voice_id = available_voices[0] if available_voices else None
                
                if not voice_id:
                    self.logger.error("No ElevenLabs voices available. Cannot generate audio.")
                    raise Exception("No ElevenLabs voices available.")

                self.logger.info(f"Selected ElevenLabs voice: {voice_id}")

                audio_data = self.elevenlabs_client.generate(
                    text=narration_text,
                    voice=voice_id, # Can be Voice object, voice_id string, or voice name string
                    model=os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2") # Or other models like "eleven_mono_v1"
                )
                
                with open(audio_path, 'wb') as f:
                    for chunk in audio_data:
                        if chunk:
                            f.write(chunk)
                
                if os.path.exists(audio_path) and os.path.getsize(audio_path) > 1000 and self._is_valid_audio(audio_path):
                    self.logger.info(f"Successfully generated voice narration with ElevenLabs: {audio_path}")
                    return audio_path
                else:
                    self.logger.error(f"ElevenLabs audio generation failed or produced invalid file: {audio_path}")
                    if os.path.exists(audio_path): # Check if corrupted file exists
                        try:
                            os.remove(audio_path)
                            self.logger.info(f"Removed potentially corrupted ElevenLabs audio file: {audio_path}")
                        except OSError as e_remove:
                            self.logger.error(f"Error removing corrupted ElevenLabs audio file {audio_path}: {e_remove}")
                    raise Exception("ElevenLabs audio generation failed")

            except Exception as e:
                self.logger.error(f"Error generating voice with ElevenLabs: {e}")
                self.logger.info("Falling back to simulated (silent) audio generation.")
        else:
            self.logger.warning("ElevenLabs client not initialized. Falling back to simulated (silent) audio generation.")

        # Fallback to silent audio generation
        if os.path.exists(audio_path) and self._is_valid_audio(audio_path):
            self.logger.info(f"Using existing valid audio file (likely from previous fallback): {audio_path}")
            return audio_path
        
        success = False
        
        # Method 1: Try using ffmpeg-python (This part was mostly complete)
        try:
            duration = 10  # seconds
            self.logger.info(f"Generating silent audio using ffmpeg-python (fallback)...")
            (ffmpeg.input('anullsrc', format='lavfi', t=str(duration))
             .output(audio_path, acodec='libmp3lame', ar='44100')
             .overwrite_output().run(capture_stdout=True, capture_stderr=True, quiet=True))
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 1000 and self._is_valid_audio(audio_path):
                self.logger.info(f"Successfully generated silent audio file (fallback): {audio_path}")
                success = True
            else: self.logger.warning(f"Fallback audio file (ffmpeg-python) missing or invalid: {audio_path}")
        except Exception as e_ffmpeg_py:
            self.logger.error(f"Error generating fallback audio with ffmpeg-python: {str(e_ffmpeg_py)}")

        # Method 2: If Method 1 failed, try using subprocess with ffmpeg directly
        if not success:
            try:
                self.logger.warning("Trying direct ffmpeg command for fallback silent audio...")
                audio_dir = os.path.dirname(audio_path)
                os.makedirs(audio_dir, exist_ok=True)
                
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                
                duration = 10  # seconds
                
                if os.name == 'nt':  # Windows
                    result = subprocess.run(
                        f'ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t {duration} -q:a 2 -acodec libmp3lame "{audio_path}"',
                        shell=True, 
                        capture_output=True,
                        text=True
                    )
                else:  # Linux, macOS
                    result = subprocess.run([
                        'ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono', 
                        '-t', str(duration), '-q:a', '2', '-acodec', 'libmp3lame', 
                        audio_path
                    ], capture_output=True, text=True)
                
                if result.returncode == 0 and os.path.exists(audio_path) and os.path.getsize(audio_path) > 1000:
                    if self._is_valid_audio(audio_path):
                        self.logger.info(f"Successfully generated silent audio via subprocess (fallback): {audio_path}")
                        success = True
                    else:
                        self.logger.warning(f"Audio file created via subprocess (fallback) but may not be valid")
                else:
                    self.logger.error(f"Subprocess ffmpeg command failed for fallback: {result.stderr if result.stderr else 'Unknown error'}")
            except Exception as e_subprocess:
                self.logger.error(f"Error with fallback audio generation (subprocess): {str(e_subprocess)}")

        # Method 3: Last resort - copy a pre-packaged test audio file if it exists
        if not success:
            try:
                test_audio_src = os.path.join(os.getenv("AUDIO_SAVE_PATH", "generated_audio/"), "test_audio.mp3")
                if os.path.exists(test_audio_src) and os.path.getsize(test_audio_src) > 1000:
                    import shutil # Local import for shutils
                    shutil.copy(test_audio_src, audio_path)
                    self.logger.warning(f"Using backup test audio file for fallback: {test_audio_src}")
                    if self._is_valid_audio(audio_path):
                        success = True
                    else:
                        self.logger.error(f"Backup audio file exists but is not valid for fallback")
            except Exception as e_backup_copy:
                self.logger.error(f"Error copying backup audio file for fallback: {str(e_backup_copy)}")
        
        # Final check and error handling for silent audio generation
        if not success:
            self.logger.critical("CRITICAL: All audio generation methods (including fallback silent) failed!")
            try:
                with open(audio_path + ".error.txt", 'w') as f:
                    f.write(f"ERROR: Could not generate valid audio file. Check logs for details.")
                # Try to create a clearly labeled invalid MP3 that won't cause FFmpeg to crash
                with open(audio_path, 'wb') as f:
                    # Write MP3 file header to make it minimally recognizable as MP3
                    f.write(b'\xFF\xFB\x90\x44\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
                    f.write(b'\x54\x41\x47\x00' + b'ERROR AUDIO' + b'\x00' * 128)
            except Exception as ex_write_err:
                self.logger.error(f"Failed to write error placeholder for audio: {ex_write_err}")
                
        self.logger.info(f"Voice narration process completed: {audio_path} (success={success})")
        return audio_path

    def create_video_from_images_and_audio(self, image_files, audio_file):
        """Create a final video from images and an audio file using ffmpeg."""
        self.logger.info("Creating final video from images and audio using ffmpeg...")
        
        today = datetime.now().strftime("%Y-%m-%d")
        final_video_dir = os.getenv("FINAL_VIDEO_SAVE_PATH", "final_videos/")
        # Directory creation is handled at the script start
        final_video_path = os.path.join(
            final_video_dir,
            f"S{self.season}_D{self.day_number}_{today}.mp4"
        )

        if not image_files:
            self.logger.error("No images provided to create video.")
            # Create a dummy file with error to allow script to proceed for testing other parts if needed
            try:
                with open(final_video_path, 'w') as f: f.write("Error: No images provided for video creation.")
            except Exception as e:
                self.logger.error(f"Failed to write dummy error file: {e}")
            return final_video_path
        
        # Verify that all image files exist and are valid
        valid_image_files = []
        for img_path in image_files:
            if not os.path.exists(img_path):
                self.logger.error(f"Image file not found: {img_path}")
                continue
                
            if not self._is_valid_image(img_path):
                self.logger.error(f"Invalid image file: {img_path}")
                continue
                
            valid_image_files.append(img_path)
            
        if not valid_image_files:
            self.logger.error("No valid image files found.")
            try:
                with open(final_video_path, 'w') as f: f.write("Error: No valid image files found.")
            except Exception as e:
                self.logger.error(f"Failed to write dummy error file: {e}")
            return final_video_path
            
        # Use only valid images
        image_files = valid_image_files
            
        if not os.path.exists(audio_file):
            self.logger.error(f"Audio file not found: {audio_file}")
            try:
                with open(final_video_path, 'w') as f: f.write(f"Error: Audio file {audio_file} not found.")
            except Exception as e:
                self.logger.error(f"Failed to write dummy error file: {e}")
            return final_video_path
            
        # Verify that audio file is valid
        if not self._is_valid_audio(audio_file):
            self.logger.error(f"Invalid audio file: {audio_file}")
            try:
                with open(final_video_path, 'w') as f: f.write(f"Error: Invalid audio file: {audio_file}")
            except Exception as e:
                self.logger.error(f"Failed to write dummy error file: {e}")
            return final_video_path

        image_duration_per_image = 5  # seconds per image
        output_framerate = 25  # fps

        temp_concat_file_path = None
        silent_video_path = None

        try:
            # Create a temporary file list for ffmpeg's concat demuxer
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as tmpf:
                for img_path in image_files:
                    abs_img_path = os.path.abspath(img_path)
                    # FFmpeg on Windows prefers forward slashes or escaped backslashes.
                    # ffmpeg-python might handle this, but being explicit can help.
                    # For concat file, simple forward slashes are usually safer.
                    # However, direct path from abspath should work if ffmpeg-python handles it.
                    # Let's ensure paths are clean for the concat file.
                    # Replacing backslashes with forward slashes for ffmpeg file list.
                    clean_img_path = abs_img_path.replace('\\\\', '/').replace('\\', '/')
                    tmpf.write(f"file '{clean_img_path}'\n")
                    tmpf.write(f"duration {image_duration_per_image}\n")
                temp_concat_file_path = tmpf.name
            
            self.logger.debug(f"Using concat file: {temp_concat_file_path}")

            # Stage 1: Create silent video from images
            # Need a temporary path for the silent video
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_silent_video:
                silent_video_path = tmp_silent_video.name
                self.logger.info(f"Creating silent video at: {silent_video_path}")
            
            # Stage 1: Create silent video from images
            try:
                (
                    ffmpeg
                    .input(temp_concat_file_path, format='concat', safe=0)
                    .output(silent_video_path, vcodec='libx264', pix_fmt='yuv420p', r=str(output_framerate), loglevel="error")
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True)
                )
                self.logger.info(f"Silent video created: {silent_video_path}")
                
                # Verify that silent video was created
                if not os.path.exists(silent_video_path) or os.path.getsize(silent_video_path) < 1000:
                    self.logger.error(f"Silent video was not created properly: {silent_video_path}")
                    raise Exception("Failed to create valid silent video")
                
                # Stage 2: Combine silent video with audio
                self.logger.info(f"Adding audio {audio_file} to {silent_video_path}")
                
                # Create input streams
                video_stream = ffmpeg.input(silent_video_path)
                audio_stream = ffmpeg.input(audio_file)
                
                # First attempt with standard approach
                try:
                    (
                        ffmpeg
                        .output(video_stream, audio_stream, final_video_path, 
                                vcodec='copy', 
                                acodec='aac', 
                                shortest=None,
                                loglevel="error" 
                               )
                        .overwrite_output()
                        .run(capture_stdout=True, capture_stderr=True)
                    )
                except Exception as e:
                    self.logger.warning(f"First attempt at adding audio failed: {str(e)}")
                    # Fallback to alternative approach if first one fails
                    self.logger.info("Trying alternative FFmpeg approach")
                    (
                        ffmpeg.concat(video_stream, audio_stream, v=1, a=1)
                        .output(final_video_path, vcodec='copy', acodec='aac')
                        .overwrite_output()
                        .run(capture_stdout=True, capture_stderr=True)
                    )
                
                self.logger.info(f"Final video with audio created: {final_video_path}")
                return final_video_path
                
            except Exception as e_inner:
                self.logger.error(f"Error in video processing: {str(e_inner)}")
                raise  # Re-raise for outer exception handler
                
        except ffmpeg.Error as e:
            self.logger.error("ffmpeg error during video creation:")
            # Decode stdout/stderr if they are bytes, handling potential decoding errors
            stdout_msg = e.stdout.decode('utf-8', errors='replace') if e.stdout else "N/A"
            stderr_msg = e.stderr.decode('utf-8', errors='replace') if e.stderr else "N/A"
            self.logger.error(f"FFmpeg command: {' '.join(e.cmd) if hasattr(e, 'cmd') and e.cmd else 'N/A'}")
            self.logger.error(f"FFmpeg stdout: {stdout_msg}")
            self.logger.error(f"FFmpeg stderr: {stderr_msg}")
            if not os.path.exists(final_video_path) or os.path.getsize(final_video_path) == 0:
                try:
                    with open(final_video_path, 'w') as f: f.write(f"Error: ffmpeg failed. Stderr: {stderr_msg[:500]}")
                except Exception as ex_write:
                     self.logger.error(f"Failed to write dummy error file after ffmpeg error: {ex_write}")
            return final_video_path 
        except Exception as e_gen:
            self.logger.error(f"General error in create_video_from_images_and_audio: {str(e_gen)}", exc_info=True)
            if not os.path.exists(final_video_path) or os.path.getsize(final_video_path) == 0:
                try:
                    with open(final_video_path, 'w') as f: f.write(f"Error: General error during video creation. Error: {str(e_gen)[:500]}")
                except Exception as ex_write:
                    self.logger.error(f"Failed to write dummy error file after general error: {ex_write}")
            return final_video_path
        finally:
            if temp_concat_file_path and os.path.exists(temp_concat_file_path):
                try:
                    os.remove(temp_concat_file_path)
                    self.logger.debug(f"Removed temporary concat file: {temp_concat_file_path}")
                except Exception as e_remove:
                    self.logger.warning(f"Could not remove temp concat file {temp_concat_file_path}: {e_remove}")
            if silent_video_path and os.path.exists(silent_video_path):
                try:
                    os.remove(silent_video_path)
                    self.logger.debug(f"Removed temporary silent video: {silent_video_path}")
                except Exception as e_remove:
                    self.logger.warning(f"Could not remove temp silent video {silent_video_path}: {e_remove}")

    def upload_to_youtube(self, video_path, title, description):
        """Upload the video to YouTube"""
        if not self.youtube_upload_enabled or not self.youtube_client:
            self.logger.warning("YouTube client not initialized or upload disabled. Simulating upload.")
            self.logger.info(f"[SIMULATED] Would upload {video_path} to YouTube with title: {title}")
            return True # Simulate success for pipeline to continue if desired

        self.logger.info(f"Attempting to upload to YouTube: {title}")

        if not os.path.exists(video_path):
            self.logger.error(f"Video file not found: {video_path}. Cannot upload.")
            return False
        if os.path.getsize(video_path) == 0:
            self.logger.error(f"Video file is empty: {video_path}. Cannot upload.")
            return False

        try:
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': os.getenv("YOUTUBE_VIDEO_TAGS", "automagic,python,ai,generated").split(','),
                    'categoryId': os.getenv("YOUTUBE_VIDEO_CATEGORY_ID", "28") # Default: Science & Technology
                },
                'status': {
                    'privacyStatus': os.getenv("YOUTUBE_VIDEO_PRIVACY", "private") # private, public, unlisted
                }
            }

            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

            request = self.youtube_client.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media
            )

            response = None
            retries = 0
            max_retries = 3
            while response is None and retries < max_retries:
                try:
                    self.logger.info(f"Uploading chunk (attempt {retries + 1})...")
                    status, response = request.next_chunk()
                    if status:
                        self.logger.info(f"Uploaded {int(status.progress() * 100)}%")
                except HttpError as e:
                    if e.resp.status in [500, 502, 503, 504]: # Retry on server errors
                        self.logger.warning(f"YouTube API server error: {e}. Retrying in {5 * (retries + 1)} seconds...")
                        time.sleep(5 * (retries + 1))
                        retries += 1
                    else:
                        self.logger.error(f"YouTube API HttpError: {e}")
                        raise
                except Exception as e_chunk:
                    self.logger.error(f"Error during chunk upload: {e_chunk}. Retrying in {5 * (retries + 1)} seconds...")
                    time.sleep(5 * (retries + 1))
                    retries += 1
            
            if response is not None:
                video_id = response.get('id')
                self.logger.info(f"Video uploaded successfully! Video ID: {video_id}")
                self.logger.info(f"Watch it here: https://www.youtube.com/watch?v={video_id}")
                return True
            else:
                self.logger.error("Failed to upload video after multiple retries.")
                return False

        except HttpError as e:
            self.logger.error(f"An HTTP error {e.resp.status} occurred during YouTube upload: {e.content}")
            return False
        except Exception as e:
            self.logger.error(f"An error occurred during YouTube upload: {e}", exc_info=True)
            return False

    def run_daily_production(self):
        """Run the full daily production pipeline"""
        self.logger.info(f"Starting daily production for Season {self.season}, Day {self.day_number}")
        
        final_video_path_for_check = None  # Initialize to ensure it's always defined for logging
        try:
            # Step 1: Generate content idea
            topic = self.generate_content_idea()
            self.logger.info(f"Content idea: {topic}")
            
            # Step 2: Generate script
            script = self.generate_script(topic)
            
            # Step 3: Generate images
            image_files = self.generate_images(script)
            
            # Step 4: Generate voice
            audio_file = self.generate_voice(script)
            
            # Step 5: Create final video from images and audio
            final_video = self.create_video_from_images_and_audio(image_files, audio_file)
            final_video_path_for_check = final_video  # Store for logging outside exception block if needed

            # Check if video creation actually succeeded and produced a valid file
            if not final_video or not os.path.exists(final_video) or os.path.getsize(final_video) == 0:
                self.logger.error("Video creation failed or produced an empty/invalid file. Aborting this production cycle.")
                # Check if it's a dummy error file and log its content
                if final_video and os.path.exists(final_video):
                    try:
                        with open(final_video, 'r', encoding='utf-8', errors='replace') as f_check:
                            content = f_check.read(500)  # Read more content for better error diagnosis
                            if "Error:" in content:
                                 self.logger.error(f"Video file content indicates error: {content}")
                            else:
                                 self.logger.info(f"Video file {final_video} exists but might be empty or invalid. Size: {os.path.getsize(final_video)} bytes.")
                    except Exception as e_read:
                        self.logger.error(f"Could not read content of video file {final_video}: {e_read}")
                return  # Stop this run

            # Step 6: Upload to YouTube
            title = f"S{self.season} D{self.day_number}: {topic}"
            description = f"AutoMagic generated video on {topic}\n\nSeason {self.season}, Day {self.day_number}"
            
            success = self.upload_to_youtube(final_video, title, description)
            if success:
                self.logger.info("Daily production completed successfully!")
                # Increment day number for next run
                self.day_number += 1
                # Update .env file with new day number
                self._update_env_variable("DAY_NUMBER", str(self.day_number))
            else:
                self.logger.warning("Daily production completed but upload failed")
                
        except Exception as e:
            self.logger.error(f"Error in daily production: {str(e)}", exc_info=True)
            if final_video_path_for_check:
                 self.logger.error(f"The video file involved was: {final_video_path_for_check}")
    
    def _update_env_variable(self, variable, value):
        """Update a variable in the .env file"""
        env_path = ".env"
        
        if os.path.exists(env_path):
            with open(env_path, 'r') as file:
                lines = file.readlines()
            
            with open(env_path, 'w') as file:
                for line in lines:
                    if line.startswith(f"{variable}="):
                        file.write(f"{variable}={value}\n")
                    else:
                        file.write(line)
            
            self.logger.info(f"Updated {variable} to {value} in .env file")

def main():
    """Main entrypoint for automation script"""
    logger.info("Starting AutoMagic automation script")
    
    # Create video production instance
    production = VideoProduction()
    
    # Get scheduled run time from .env
    run_time = os.getenv("DAILY_RUN_TIME", "09:00")
    logger.info(f"Scheduled to run daily at {run_time}")
    
    # Schedule daily run
    schedule.every().day.at(run_time).do(production.run_daily_production)
    
    # Also provide a way to run it immediately for testing
    if len(sys.argv) > 1 and sys.argv[1] == "--now":
        logger.info("Running production now as requested")
        production.run_daily_production()
    else:
        logger.info(f"Waiting for scheduled time ({run_time})...")
        logger.info("(Run with --now flag to execute immediately)")
        
        # Run continuously to check schedule
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
