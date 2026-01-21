# core/strategy/brief_synthesizer.py - Creates a creative brief from trends
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def synthesize_brief_from_trends(trends: dict) -> dict | None:
    """Uses an LLM to synthesize a CreativeBrief from raw trend data."""
    print("🧠 Synthesizing creative brief...")
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f'''
        You are OTTO, an AI Creative Director with multiple personalities. Analyze the following trend data.
        First, choose a personality to adopt for this video (e.g., 'The Scholar', 'The Satirist', 'The Mystic').
        Then, based on that personality, create a single, surreal, profound video concept that taps into the zeitgeist of the data.

        **Trend Data:** {json.dumps(trends)}

        **Your Task:** Output a single, valid JSON object and nothing else.
        The JSON must contain these exact keys: "theme", "personality", "affirmation_text", "positive_prompt", "negative_prompt", "mood", "style", "composition", "audio_mood", "voice_profile".
        The "positive_prompt" must be highly detailed for DALL-E 3.
        The "voice_profile" should be an ElevenLabs voice ID that matches the chosen personality.
        '''
        response = model.generate_content(prompt)
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        brief = json.loads(json_text)
        
        # Basic validation
        required_keys = ["theme", "personality", "affirmation_text", "positive_prompt"]
        if not all(key in brief for key in required_keys):
            raise ValueError("Synthesized brief is missing required keys.")
        
        print(f"✨ Brief synthesized with personality: {brief['personality']}")
        return brief
    except Exception as e:
        print(f"❌ Brief synthesis failed: {e}")
        return None
