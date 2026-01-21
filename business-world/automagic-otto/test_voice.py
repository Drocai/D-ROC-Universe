#!/usr/bin/env python3
"""
Test Voice Generation - Make sure we can create voice
"""

import os
from pathlib import Path

print("Testing voice generation methods...")

# Method 1: Windows SAPI (built-in)
def test_windows_sapi():
    print("\n1. Testing Windows SAPI (built-in)...")
    
    text = "Hello, this is a test of the AutoMagic voice system. If you can hear this, voice generation is working."
    
    try:
        import win32com.client
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        
        # Create file stream
        stream = win32com.client.Dispatch("SAPI.SpFileStream")
        stream.Open("test_sapi.wav", 3)
        speaker.AudioOutputStream = stream
        speaker.Speak(text)
        stream.Close()
        
        if os.path.exists("test_sapi.wav"):
            print("  [OK] Windows SAPI voice created: test_sapi.wav")
            return True
    except Exception as e:
        print(f"  [FAIL] Windows SAPI: {e}")
    
    return False

# Method 2: pyttsx3
def test_pyttsx3():
    print("\n2. Testing pyttsx3...")
    
    text = "Testing pyttsx3 voice generation for AutoMagic."
    
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.save_to_file(text, "test_pyttsx3.wav")
        engine.runAndWait()
        
        if os.path.exists("test_pyttsx3.wav"):
            print("  [OK] pyttsx3 voice created: test_pyttsx3.wav")
            return True
    except Exception as e:
        print(f"  [FAIL] pyttsx3: {e}")
    
    return False

# Method 3: PowerShell TTS
def test_powershell_tts():
    print("\n3. Testing PowerShell TTS...")
    
    text = "Testing PowerShell text to speech for AutoMagic videos."
    output_file = "test_powershell.wav"
    
    # PowerShell script to generate speech
    ps_script = f'''
Add-Type -AssemblyName System.Speech
$synthesizer = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synthesizer.SetOutputToWaveFile("{os.path.abspath(output_file)}")
$synthesizer.Speak("{text}")
$synthesizer.Dispose()
'''
    
    # Save script
    with open("tts_script.ps1", "w") as f:
        f.write(ps_script)
    
    try:
        import subprocess
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", "tts_script.ps1"],
            capture_output=True, text=True
        )
        
        if os.path.exists(output_file):
            print(f"  [OK] PowerShell TTS created: {output_file}")
            os.remove("tts_script.ps1")
            return True
        else:
            print(f"  [FAIL] PowerShell TTS: No file created")
            
    except Exception as e:
        print(f"  [FAIL] PowerShell TTS: {e}")
    
    return False

# Method 4: gTTS (Google)
def test_gtts():
    print("\n4. Testing Google TTS...")
    
    text = "Testing Google text to speech for AutoMagic video generation."
    
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang='en')
        tts.save("test_gtts.mp3")
        
        if os.path.exists("test_gtts.mp3"):
            print("  [OK] Google TTS created: test_gtts.mp3")
            return True
    except Exception as e:
        print(f"  [FAIL] Google TTS: {e}")
    
    return False

# Run all tests
print("=" * 50)
print("VOICE GENERATION TEST")
print("=" * 50)

working_methods = []

if test_windows_sapi():
    working_methods.append("Windows SAPI")

if test_pyttsx3():
    working_methods.append("pyttsx3")
    
if test_powershell_tts():
    working_methods.append("PowerShell TTS")
    
if test_gtts():
    working_methods.append("Google TTS")

print("\n" + "=" * 50)
print("RESULTS:")
print("=" * 50)

if working_methods:
    print(f"[SUCCESS] Working voice methods: {', '.join(working_methods)}")
    print("\nVoice files created:")
    for f in Path(".").glob("test_*.wav"):
        print(f"  - {f}")
    for f in Path(".").glob("test_*.mp3"):
        print(f"  - {f}")
else:
    print("[PROBLEM] No voice generation methods working!")
    print("This explains why videos have no sound.")

print("\nNext step: Use working method in video generator")