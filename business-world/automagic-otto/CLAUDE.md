# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

 is an automated content creation system that generates daily YouTube videos using AI APIs. The system creates content ideas, scripts, images, voice narration, and final videos, then uploads them to YouTube on a schedule.

## Core Architecture

### Main Components

- **.py** - Legacy main script with comprehensive video production pipeline
- **automation_script.py** - Enhanced main automation script with better error handling and trending integration
- **run_.py** - Launcher script with environment validation and dependency checks
- **_setup.py** - Automated setup script for initial configuration

### Production Pipeline

1. **Content Generation** (`generate_content_idea()`)
   - Uses trending topics via `trend_integration.py` if available
   - Falls back to OpenAI for content ideas
   - Has hardcoded fallback topics as last resort

2. **Script Creation** (`generate_script()`)
   - OpenAI generates structured video scripts
   - Format: Introduction → 3 Main Points → Conclusion

3. **Image Generation** (`generate_images()`)
   - DALL-E 3/2 via OpenAI API for visual content
   - PIL fallback for error cases
   - Creates 3 images per video

4. **Voice Synthesis** (`generate_voice()`)
   - ElevenLabs API for narration
   - FFmpeg fallback for silent audio if API fails

5. **Video Assembly** (`create_video_from_images_and_audio()`)
   - FFmpeg-python for video composition
   - Combines images with audio using concat demuxer
   - 5 seconds per image, 25fps output

6. **YouTube Upload** (`upload_to_youtube()`)
   - Google YouTube Data API v3
   - OAuth2 authentication with token persistence
   - Retry logic for upload failures

### Configuration System

- **.env** - Main configuration file with API keys and settings
- **Season/Day tracking** - Automated daily increment system
- **Logging** - Comprehensive logging to `logs/.log`

## Common Development Commands

### Setup and Installation
```bash
# Initial setup
python _setup.py

# Install dependencies
pip install -r requirements.txt

# Verify installation
python test_setup.py
```

### Running the System
```bash
# Standard run (waits for scheduled time)
python automation_script.py

# Immediate run
python automation_script.py --now

# Debug mode with verbose logging
python automation_script.py --debug

# Run via launcher with environment checks
python run_.py

# Windows batch launcher
.bat
```

### Testing Individual Components
```bash
# Test image generation only
python automation_script.py --test image

# Test voice generation only
python automation_script.py --test voice

# Test video creation only
python automation_script.py --test video

# Test YouTube upload only
python automation_script.py --test upload

# List available ElevenLabs voices
python automation_script.py --list-voices
```

### Environment Management
```bash
# View current environment status
python verify_all.py

# Run comprehensive system check
python comprehensive_test.py
```

## Key Dependencies

- **openai** - DALL-E image generation and GPT for scripts
- **elevenlabs** - Voice synthesis
- **google-api-python-client** - YouTube uploads
- **ffmpeg-python** - Video processing (requires FFmpeg installed)
- **schedule** - Daily automation scheduling
- **python-dotenv** - Environment configuration

## File Structure

```
/
├── .py                 # Legacy main script
├── automation_script.py         # Enhanced main script
├── run_.py            # Launcher with checks
├── _setup.py          # Setup automation
├── .env                        # Configuration
├── requirements.txt            # Dependencies
├── generated_images/           # DALL-E outputs
├── generated_audio/            # ElevenLabs outputs
├── final_videos/              # Completed videos
├── logs/                      # Application logs
└── trend_integration.py       # Optional trending topics
```

## Important Configuration

- **FFmpeg** must be installed and in PATH for video processing
- **API keys** required: OpenAI, ElevenLabs, Google Cloud (YouTube)
- **YouTube OAuth** requires `client_secret_*.json` file from Google Console
- **Schedule** runs daily at time specified in `DAILY_RUN_TIME` (default 09:00)

## Debugging Tips

- Use `--debug` flag for verbose logging
- Check `logs/.log` for detailed error information
- Use individual `--test` flags to isolate component failures
- Verify FFmpeg installation with `ffmpeg -version`
- Use `verify_all.py` for comprehensive system check

## Development Notes

- The system has two main scripts: `.py` (legacy) and `automation_script.py` (enhanced)
- `automation_script.py` is the preferred main script with better error handling
- `VideoProduction` class encapsulates the entire pipeline
- Error handling includes fallback mechanisms for all API calls
- The system automatically increments day numbers and updates `.env`