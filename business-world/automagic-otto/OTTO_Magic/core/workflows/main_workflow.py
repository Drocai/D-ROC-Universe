# core/workflows/main_workflow.py - The main workflow orchestrating OTTO's tasks
import logging
from ..strategy import get_trending_topics, synthesize_brief_from_trends
from ..generation import generate_visuals, generate_voiceover, select_music
from ..validation import validate_asset_pack
from ..pipelines import assemble_video, upload_to_youtube

logger = logging.getLogger(__name__)

def get_trends_task(pillars: list[str]):
    """Get trending topics with retry logic."""
    for attempt in range(3):
        try:
            trends = get_trending_topics(pillars)
            if trends:
                return trends
            logger.warning(f"Failed to fetch trends, attempt {attempt + 1}/3")
        except Exception as e:
            logger.error(f"Error fetching trends: {e}")
            if attempt == 2:
                raise Exception("Failed to fetch trends after 3 attempts.")
    return None

def synthesize_brief_task(trends: dict):
    """Synthesize brief from trends with retry logic."""
    for attempt in range(3):
        try:
            brief = synthesize_brief_from_trends(trends)
            if brief:
                return brief
            logger.warning(f"Failed to synthesize brief, attempt {attempt + 1}/3")
        except Exception as e:
            logger.error(f"Error synthesizing brief: {e}")
            if attempt == 2:
                raise Exception("Failed to synthesize brief after 3 attempts.")
    return None

def generate_and_validate_visuals_task(brief: dict):
    """Generate and validate visuals with retry logic."""
    for attempt in range(3):
        try:
            print(f"Visual generation attempt {attempt + 1}/3...")
            visual_path = generate_visuals(brief)
            if visual_path and validate_asset_pack(visual_path, brief):
                return visual_path
            print("Visual generation or validation failed. Retrying...")
        except Exception as e:
            logger.error(f"Error generating visuals: {e}")
    raise Exception("Failed to generate a valid visual asset after 3 attempts.")
    
def generate_audio_task(brief: dict):
    """Generate audio with retry logic."""
    for attempt in range(3):
        try:
            voiceover_path = generate_voiceover(brief)
            if voiceover_path:
                return voiceover_path
            logger.warning(f"Failed to generate voiceover, attempt {attempt + 1}/3")
        except Exception as e:
            logger.error(f"Error generating voiceover: {e}")
            if attempt == 2:
                raise Exception("Failed to generate voiceover after 3 attempts.")
    return None
    
def select_music_task(brief: dict):
    """Select music for the video."""
    return select_music(brief)

def assemble_video_task(visual_path, voiceover_path, music_path, brief):
    """Assemble the final video."""
    video_path = assemble_video(visual_path, voiceover_path, music_path, brief)
    if not video_path: 
        raise Exception("Failed to assemble the final video.")
    return video_path

def upload_youtube_task(video_path, brief):
    """Upload video to YouTube."""
    title = f"{brief['personality']}: {brief['theme']}"
    tags = [brief['personality']] + brief['theme'].split() + ['AI', 'OTTO_Magic']
    description = f"An OTTO Magic generation.\n\nTheme: {brief['theme']}\nPersonality: {brief['personality']}\n\n{brief['affirmation_text']}\n\n#AI #Surreal #{brief['personality'].replace(' ','')}"
    
    try:
        success = upload_to_youtube(video_path, title, description, tags)
        if success:
            print(f"✅ Video uploaded to YouTube: {title}")
        else:
            print(f"⚠️ YouTube upload failed, but video created: {video_path}")
    except Exception as e:
        print(f"⚠️ YouTube upload error (video still created): {e}")
        # Don't raise exception - video creation was successful

def trend_to_video_flow(pillars: list[str]):
    """The main workflow orchestrating the entire daily production."""
    trends = get_trends_task(pillars)
    brief = synthesize_brief_task(trends)
    
    # Generate assets
    visual_path = generate_and_validate_visuals_task(brief)
    voiceover_path = generate_audio_task(brief)
    music_path = select_music_task(brief)
    
    # Final production and upload
    final_video_path = assemble_video_task(visual_path, voiceover_path, music_path, brief)
    upload_youtube_task(final_video_path, brief)

def video_creation_workflow(topic: str = None, custom_brief: str = None):
    """Entry point for video creation workflow."""
    logger.info(f"Starting video creation workflow for topic: {topic}")
    
    if custom_brief:
        # Use custom brief if provided
        brief = {
            "theme": topic or "Custom Topic", 
            "custom_brief": custom_brief,
            "visual_prompt": f"Create a visual representation of: {topic}",
            "affirmation_text": custom_brief,
            "personality": "innovative"
        }
        logger.info("Using custom brief")
        
        # Generate assets for custom brief
        visual_path = generate_and_validate_visuals_task(brief)
        voiceover_path = generate_audio_task(brief)
        music_path = select_music_task(brief)
        
        # Final production and upload
        final_video_path = assemble_video_task(visual_path, voiceover_path, music_path, brief)
        upload_youtube_task(final_video_path, brief)
    else:
        # Default pillars for trend analysis
        pillars = ["technology", "AI", "creativity", "innovation"]
        
        # Normal trend-based workflow
        logger.info("Starting trend-based workflow")
        trend_to_video_flow(pillars)
