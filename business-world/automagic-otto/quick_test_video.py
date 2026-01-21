#!/usr/bin/env python3
"""Quick test - Generate a complete video"""

import sys
import logging
from automagic_multi_provider import MultiProviderVideoProduction

logging.basicConfig(level=logging.INFO, format="%(message)s")

print("\n" + "="*70)
print("  QUICK TEST: GENERATING COMPLETE VIDEO")
print("="*70)
print("\nThis will test:")
print("  [1/3] Script generation with Groq")
print("  [2/3] Image generation with Replicate")
print("  [3/3] Voice generation with ElevenLabs")
print("  [4/3] Video assembly with FFmpeg")
print("\n" + "="*70)

try:
    production = MultiProviderVideoProduction()
    video_path = production.run_production()

    if video_path:
        print("\n" + "="*70)
        print("  SUCCESS! Video created!")
        print("="*70)
        print(f"\n  Location: {video_path}")
        print("\n" + "="*70)
    else:
        print("\n[FAILED] Video creation did not complete")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
