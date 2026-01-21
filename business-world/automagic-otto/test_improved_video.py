#!/usr/bin/env python3
"""Test improved script and voice generation"""

import sys
import logging
from automagic_multi_provider import MultiProviderVideoProduction

logging.basicConfig(level=logging.INFO, format="%(message)s")

print("\n" + "="*70)
print("  TESTING IMPROVED VIDEO GENERATION")
print("="*70)
print("\nImprovements:")
print("  [1] Cleaner script prompt - no formatting or stage directions")
print("  [2] Better script cleaning - removes all markdown and notes")
print("  [3] Enhanced placeholder images - gradients instead of flat colors")
print("\n" + "="*70)

try:
    production = MultiProviderVideoProduction()

    # Generate with a simple topic
    print("\nGenerating video...")
    video_path = production.run_production()

    if video_path:
        print("\n" + "="*70)
        print("  SUCCESS! Improved video created!")
        print("="*70)
        print(f"\n  Location: {video_path}")
        print("\n  Check the video - voice should be cleaner")
        print("  and images should have nice gradients!")
        print("\n" + "="*70)
    else:
        print("\n[FAILED] Video creation did not complete")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
