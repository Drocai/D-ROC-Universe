#!/usr/bin/env python3
"""Quick test of Groq script generation"""

from api_providers import ProviderManager

print("\nTesting Groq script generation...")
print("="*60)

manager = ProviderManager()

try:
    script = manager.generate_script_with_fallback(
        "The future of artificial intelligence",
        max_tokens=300
    )

    print("\n[SUCCESS] Script generated!\n")
    print(script)
    print("\n" + "="*60)
    print(f"Generated {len(script)} characters using Groq")
    print("="*60)

except Exception as e:
    print(f"\n[FAILED] {e}")
