# core/generation/audio_generator.py - Generates voiceovers and selects music
import os
import random
import time
from pathlib import Path
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

load_dotenv()

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
AUDIO_OUTPUT_DIR = Path("generated_assets/audio")
AUDIO_OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

def generate_voiceover(brief: dict) -> Path | None:
    """Generates a voiceover using the ElevenLabs API."""
    print("🎤 Generating voiceover...")
    text = brief.get("affirmation_text", "This is a test voiceover.")
    voice_id = brief.get("voice_profile", "pNInz6obpgDQGcFmaJgB")  # Default voice ID

    try:
        audio = client.generate(text=text, voice=voice_id, model="eleven_multilingual_v2")
        output_path = AUDIO_OUTPUT_DIR / f"voiceover_{int(time.time())}.mp3"
        
        # Write audio to file
        with open(output_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)
                
        print(f"✅ Voiceover saved: {output_path}")
        return output_path
    except Exception as e:
        print(f"❌ ElevenLabs voice generation failed: {e}")
        return None

def select_music(brief: dict) -> Path | None:
    """Selects a music track from the library based on the brief's mood."""
    print("🎵 Selecting music track...")
    music_library_path = Path(os.getenv("MUSIC_LIBRARY_PATH", "music_library"))
    mood = brief.get("mood", "").lower()

    if not music_library_path.exists():
        print(f"⚠️ Music library not found at '{music_library_path}'. Skipping music.")
        return None

    possible_tracks = [p for p in music_library_path.glob("*.mp3") if p.name.lower().startswith(mood)]
    
    if not possible_tracks:
        print(f"⚠️ No music found for mood '{mood}'. Selecting a random track.")
        all_tracks = list(music_library_path.glob("*.mp3"))
        if not all_tracks:
            print("⚠️ No music found in the library at all.")
            return None
        return random.choice(all_tracks)
    
    return random.choice(possible_tracks)

def select_music(brief: dict) -> Path | None:
    """Selects appropriate background music based on the brief."""
    print("🎵 Selecting background music...")
    
    music_library_path = Path(os.getenv("MUSIC_LIBRARY_PATH", "generated_assets/audio"))
    music_library_path.mkdir(exist_ok=True, parents=True)
    
    # Extract mood from brief or use default
    mood = brief.get("mood", "calm").lower()
    
    # Try to find music that matches the mood
    possible_tracks = [p for p in music_library_path.glob("*.mp3") if p.name.lower().startswith(mood)]
    
    if not possible_tracks:
        print(f"⚠️ No music found for mood '{mood}'. Using default music.")
        # Create a simple silence track as fallback
        return None
    
    selected = random.choice(possible_tracks)
    print(f"✅ Selected music: {selected.name}")
    return selected
