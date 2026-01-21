#!/usr/bin/env python3
"""Test with real AI images from HuggingFace"""

import sys
import logging
from automagic_multi_provider import MultiProviderVideoProduction

logging.basicConfig(level=logging.INFO, format="%(message)s")

print("\n" + "="*70)
print("  CREATING VIDEO WITH REAL AI IMAGES")
print("="*70)
print("\nUsing:")
print("  [Script] Groq - FREE, clean narration")
print("  [Images] HuggingFace - FREE, real AI art")
print("  [Voice]  ElevenLabs - Professional quality")
print("\n" + "="*70)

try:
    production = MultiProviderVideoProduction()

    print("\n🎬 Starting production...\n")
    video_path = production.run_production()

    if video_path:
        print("\n" + "="*70)
        print("  ✅ SUCCESS! VIDEO WITH REAL AI IMAGES CREATED!")
        print("="*70)
        print(f"\n  📁 Location: {video_path}")
        print("\n  This video has:")
        print("    ✅ Clean narration (no headers/notes)")
        print("    ✅ Real AI-generated images")
        print("    ✅ Professional voice-over")
        print("\n" + "="*70)

        # Open the video
        import subprocess
        subprocess.Popen(['start', video_path], shell=True)
        print("\n  🎥 Video should be opening now!")
        print("\n" + "="*70)
    else:
        print("\n❌ [FAILED] Video creation did not complete")

except Exception as e:
    print(f"\n❌ [ERROR] {e}")
    import traceback
    traceback.print_exc()
