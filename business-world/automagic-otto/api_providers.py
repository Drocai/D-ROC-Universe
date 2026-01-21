#!/usr/bin/env python3
"""
API Providers Module - Multi-provider system with automatic fallbacks
Supports multiple API providers for script generation, image generation, and voice synthesis
"""

import os
import logging
import traceback
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("AutoMagic.Providers")


# ============================================================================
# BASE PROVIDER CLASSES
# ============================================================================

class BaseProvider(ABC):
    """Base class for all API providers"""

    def __init__(self, name: str, priority: int = 0):
        self.name = name
        self.priority = priority
        self.logger = logger

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is configured and available"""
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the provider API is responding"""
        pass


class ScriptProvider(BaseProvider):
    """Base class for script generation providers"""

    @abstractmethod
    def generate_script(self, topic: str, **kwargs) -> str:
        """Generate a video script based on the topic"""
        pass


class ImageProvider(BaseProvider):
    """Base class for image generation providers"""

    @abstractmethod
    def generate_image(self, prompt: str, **kwargs) -> bytes:
        """Generate an image from a text prompt"""
        pass


class VoiceProvider(BaseProvider):
    """Base class for voice synthesis providers"""

    @abstractmethod
    def generate_voice(self, text: str, **kwargs) -> bytes:
        """Generate voice audio from text"""
        pass


# ============================================================================
# SCRIPT GENERATION PROVIDERS
# ============================================================================

class GroqScriptProvider(ScriptProvider):
    """Groq API provider for script generation (Fast, FREE tier)"""

    def __init__(self):
        super().__init__("Groq", priority=1)
        self.api_key = os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    def is_available(self) -> bool:
        return bool(self.api_key and not self.api_key.startswith("YOUR_"))

    def test_connection(self) -> bool:
        if not self.is_available():
            return False
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            response = requests.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Groq connection test failed: {e}")
            return False

    def generate_script(self, topic: str, **kwargs) -> str:
        """Generate script using Groq API"""
        self.logger.info(f"Generating script with Groq ({self.model})...")

        prompt = kwargs.get("prompt") or (
            f"Write a natural, conversational narration script for a YouTube video about '{topic}'. "
            "Write ONLY the words that should be spoken - no headers, no stage directions, no formatting. "
            "Structure: Start with a hook, cover 2-3 main points with interesting facts, "
            "end with a call to action. "
            "Keep it under 300 words, use simple language, and write as if you're talking to a friend. "
            "DO NOT include any markdown formatting, timestamps, or notes in parentheses."
        )

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get("max_tokens", 1000),
                "temperature": kwargs.get("temperature", 0.7)
            }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            script = result['choices'][0]['message']['content']
            self.logger.info(f"✅ Script generated with Groq ({len(script)} chars)")
            return script

        except Exception as e:
            self.logger.error(f"Groq script generation failed: {e}")
            raise


class GeminiScriptProvider(ScriptProvider):
    """Google Gemini API provider for script generation"""

    def __init__(self):
        super().__init__("Gemini", priority=2)
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    def is_available(self) -> bool:
        return bool(self.api_key and not self.api_key.startswith("YOUR_"))

    def test_connection(self) -> bool:
        if not self.is_available():
            return False
        try:
            response = requests.get(
                f"{self.base_url}/models?key={self.api_key}",
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Gemini connection test failed: {e}")
            return False

    def generate_script(self, topic: str, **kwargs) -> str:
        """Generate script using Google Gemini API"""
        self.logger.info(f"Generating script with Gemini ({self.model})...")

        prompt = kwargs.get("prompt") or (
            f"Write a concise, engaging video script for YouTube on the topic '{topic}'. "
            "Include an attention-grabbing introduction, three main points with interesting facts, "
            "and a strong conclusion that encourages viewers to like and subscribe. "
            "Keep it conversational and under 500 words. Format with clear sections."
        )

        try:
            url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"

            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "maxOutputTokens": kwargs.get("max_tokens", 1000),
                }
            }

            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            script = result['candidates'][0]['content']['parts'][0]['text']
            self.logger.info(f"✅ Script generated with Gemini ({len(script)} chars)")
            return script

        except Exception as e:
            self.logger.error(f"Gemini script generation failed: {e}")
            raise


class OpenAIScriptProvider(ScriptProvider):
    """OpenAI GPT provider (fallback/legacy)"""

    def __init__(self):
        super().__init__("OpenAI", priority=3)
        self.api_key = os.getenv("OPENAI_API_KEY")

    def is_available(self) -> bool:
        return bool(self.api_key and not self.api_key.startswith("YOUR_"))

    def test_connection(self) -> bool:
        if not self.is_available():
            return False
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            # Simple test call
            return True
        except Exception as e:
            self.logger.error(f"OpenAI connection test failed: {e}")
            return False

    def generate_script(self, topic: str, **kwargs) -> str:
        """Generate script using OpenAI API"""
        self.logger.info("Generating script with OpenAI...")

        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)

            prompt = kwargs.get("prompt") or (
                f"Write a concise, engaging video script for YouTube on the topic '{topic}'. "
                "Include an introduction, three main points, and a conclusion in markdown format."
            )

            response = client.chat.completions.create(
                model=kwargs.get("model", "gpt-3.5-turbo"),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get("max_tokens", 500),
                temperature=kwargs.get("temperature", 0.7)
            )

            script = response.choices[0].message.content
            self.logger.info(f"✅ Script generated with OpenAI ({len(script)} chars)")
            return script

        except Exception as e:
            self.logger.error(f"OpenAI script generation failed: {e}")
            raise


# ============================================================================
# IMAGE GENERATION PROVIDERS
# ============================================================================

class ReplicateImageProvider(ImageProvider):
    """Replicate API provider for image generation (FLUX, SDXL, etc.)"""

    def __init__(self):
        super().__init__("Replicate", priority=1)
        self.api_key = os.getenv("REPLICATE_API_KEY")
        self.model = os.getenv("REPLICATE_MODEL", "black-forest-labs/flux-schnell")

    def is_available(self) -> bool:
        return bool(self.api_key and not self.api_key.startswith("YOUR_"))

    def test_connection(self) -> bool:
        if not self.is_available():
            return False
        try:
            headers = {"Authorization": f"Token {self.api_key}"}
            response = requests.get(
                "https://api.replicate.com/v1/models",
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Replicate connection test failed: {e}")
            return False

    def generate_image(self, prompt: str, **kwargs) -> bytes:
        """Generate image using Replicate API"""
        self.logger.info(f"Generating image with Replicate ({self.model})...")

        try:
            import replicate

            # Initialize client
            os.environ["REPLICATE_API_TOKEN"] = self.api_key

            # Run the model
            output = replicate.run(
                self.model,
                input={
                    "prompt": prompt,
                    "num_outputs": 1,
                    "aspect_ratio": kwargs.get("aspect_ratio", "16:9"),
                    "output_format": kwargs.get("output_format", "jpg"),
                    "output_quality": kwargs.get("output_quality", 90)
                }
            )

            # Get the image URL
            image_url = output[0] if isinstance(output, list) else output

            # Download the image
            img_response = requests.get(image_url, timeout=30)
            img_response.raise_for_status()

            self.logger.info(f"✅ Image generated with Replicate ({len(img_response.content)} bytes)")
            return img_response.content

        except Exception as e:
            self.logger.error(f"Replicate image generation failed: {e}")
            raise


class HuggingFaceImageProvider(ImageProvider):
    """Hugging Face Inference API provider"""

    def __init__(self):
        super().__init__("HuggingFace", priority=2)
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        # Use a more reliable model for free tier (SD-XL is faster and more stable)
        self.model = os.getenv("HUGGINGFACE_MODEL", "stabilityai/stable-diffusion-xl-base-1.0")
        self.base_url = "https://api-inference.huggingface.co/models"

    def is_available(self) -> bool:
        return bool(self.api_key and not self.api_key.startswith("YOUR_"))

    def test_connection(self) -> bool:
        if not self.is_available():
            return False
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(
                "https://huggingface.co/api/whoami-v2",
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"HuggingFace connection test failed: {e}")
            return False

    def generate_image(self, prompt: str, **kwargs) -> bytes:
        """Generate image using HuggingFace API"""
        self.logger.info(f"Generating image with HuggingFace ({self.model})...")

        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}

            payload = {"inputs": prompt}

            response = requests.post(
                f"{self.base_url}/{self.model}",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()

            self.logger.info(f"✅ Image generated with HuggingFace ({len(response.content)} bytes)")
            return response.content

        except Exception as e:
            self.logger.error(f"HuggingFace image generation failed: {e}")
            raise


class StabilityImageProvider(ImageProvider):
    """Stability AI provider for image generation"""

    def __init__(self):
        super().__init__("Stability", priority=3)
        self.api_key = os.getenv("STABILITY_API_KEY")
        self.base_url = "https://api.stability.ai/v2beta/stable-image/generate"

    def is_available(self) -> bool:
        return bool(self.api_key and not self.api_key.startswith("YOUR_"))

    def test_connection(self) -> bool:
        if not self.is_available():
            return False
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(
                "https://api.stability.ai/v1/user/account",
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Stability connection test failed: {e}")
            return False

    def generate_image(self, prompt: str, **kwargs) -> bytes:
        """Generate image using Stability AI"""
        self.logger.info("Generating image with Stability AI...")

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "image/*"
            }

            files = {"none": ''}
            data = {
                "prompt": prompt,
                "output_format": kwargs.get("output_format", "jpeg"),
                "aspect_ratio": kwargs.get("aspect_ratio", "16:9")
            }

            response = requests.post(
                f"{self.base_url}/sd3",
                headers=headers,
                files=files,
                data=data,
                timeout=60
            )
            response.raise_for_status()

            self.logger.info(f"✅ Image generated with Stability ({len(response.content)} bytes)")
            return response.content

        except Exception as e:
            self.logger.error(f"Stability image generation failed: {e}")
            raise


# ============================================================================
# VOICE GENERATION PROVIDERS
# ============================================================================

class ElevenLabsVoiceProvider(VoiceProvider):
    """ElevenLabs API provider (primary voice service)"""

    def __init__(self):
        super().__init__("ElevenLabs", priority=1)
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID")

    def is_available(self) -> bool:
        return bool(self.api_key and not self.api_key.startswith("YOUR_"))

    def test_connection(self) -> bool:
        if not self.is_available():
            return False
        try:
            from elevenlabs.client import ElevenLabs
            client = ElevenLabs(api_key=self.api_key)
            voices = client.voices.get_all()
            return bool(voices.voices)
        except Exception as e:
            self.logger.error(f"ElevenLabs connection test failed: {e}")
            return False

    def generate_voice(self, text: str, **kwargs) -> bytes:
        """Generate voice using ElevenLabs"""
        self.logger.info("Generating voice with ElevenLabs...")

        try:
            from elevenlabs.client import ElevenLabs

            client = ElevenLabs(api_key=self.api_key)
            voice_id = kwargs.get("voice_id", self.voice_id)

            if not voice_id:
                voices = client.voices.get_all()
                if voices.voices:
                    voice_id = voices.voices[0].voice_id
                    self.logger.info(f"Using first available voice: {voices.voices[0].name}")

            audio_generator = client.generate(
                text=text,
                voice=voice_id,
                model=kwargs.get("model", "eleven_multilingual_v2")
            )

            # Collect audio data
            audio_data = b""
            for chunk in audio_generator:
                audio_data += chunk

            self.logger.info(f"✅ Voice generated with ElevenLabs ({len(audio_data)} bytes)")
            return audio_data

        except Exception as e:
            self.logger.error(f"ElevenLabs voice generation failed: {e}")
            raise


class GoogleTTSVoiceProvider(VoiceProvider):
    """Google Cloud Text-to-Speech provider"""

    def __init__(self):
        super().__init__("GoogleTTS", priority=2)
        self.api_key = os.getenv("GOOGLE_TTS_API_KEY") or os.getenv("GOOGLE_API_KEY")

    def is_available(self) -> bool:
        return bool(self.api_key and not self.api_key.startswith("YOUR_"))

    def test_connection(self) -> bool:
        if not self.is_available():
            return False
        try:
            response = requests.get(
                f"https://texttospeech.googleapis.com/v1/voices?key={self.api_key}",
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Google TTS connection test failed: {e}")
            return False

    def generate_voice(self, text: str, **kwargs) -> bytes:
        """Generate voice using Google Cloud TTS"""
        self.logger.info("Generating voice with Google TTS...")

        try:
            url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={self.api_key}"

            payload = {
                "input": {"text": text},
                "voice": {
                    "languageCode": kwargs.get("language_code", "en-US"),
                    "name": kwargs.get("voice_name", "en-US-Neural2-J"),
                    "ssmlGender": kwargs.get("gender", "MALE")
                },
                "audioConfig": {
                    "audioEncoding": "MP3",
                    "speakingRate": kwargs.get("speaking_rate", 1.0),
                    "pitch": kwargs.get("pitch", 0.0)
                }
            }

            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            import base64
            audio_data = base64.b64decode(result['audioContent'])

            self.logger.info(f"✅ Voice generated with Google TTS ({len(audio_data)} bytes)")
            return audio_data

        except Exception as e:
            self.logger.error(f"Google TTS voice generation failed: {e}")
            raise


# ============================================================================
# PROVIDER MANAGER - Handles fallbacks automatically
# ============================================================================

class ProviderManager:
    """Manages multiple providers with automatic fallback"""

    def __init__(self):
        self.logger = logger

        # Initialize all providers
        self.script_providers: List[ScriptProvider] = [
            GroqScriptProvider(),
            GeminiScriptProvider(),
            OpenAIScriptProvider()
        ]

        self.image_providers: List[ImageProvider] = [
            ReplicateImageProvider(),
            HuggingFaceImageProvider(),
            StabilityImageProvider()
        ]

        self.voice_providers: List[VoiceProvider] = [
            ElevenLabsVoiceProvider(),
            GoogleTTSVoiceProvider()
        ]

        # Sort by priority
        self.script_providers.sort(key=lambda p: p.priority)
        self.image_providers.sort(key=lambda p: p.priority)
        self.voice_providers.sort(key=lambda p: p.priority)

    def get_available_providers(self, provider_list: List[BaseProvider]) -> List[BaseProvider]:
        """Get list of available providers from a list"""
        available = [p for p in provider_list if p.is_available()]
        if available:
            self.logger.info(f"Available providers: {[p.name for p in available]}")
        return available

    def generate_script_with_fallback(self, topic: str, **kwargs) -> str:
        """Try to generate script using available providers in priority order"""
        providers = self.get_available_providers(self.script_providers)

        if not providers:
            raise Exception("No script providers available. Please configure at least one API key.")

        for provider in providers:
            try:
                self.logger.info(f"Attempting script generation with {provider.name}...")
                return provider.generate_script(topic, **kwargs)
            except Exception as e:
                self.logger.warning(f"{provider.name} failed: {str(e)[:100]}")
                if provider == providers[-1]:  # Last provider
                    raise Exception(f"All script providers failed. Last error: {e}")
                self.logger.info(f"Falling back to next provider...")

        raise Exception("Script generation failed with all providers")

    def generate_image_with_fallback(self, prompt: str, **kwargs) -> bytes:
        """Try to generate image using available providers in priority order"""
        providers = self.get_available_providers(self.image_providers)

        if not providers:
            raise Exception("No image providers available. Please configure at least one API key.")

        for provider in providers:
            try:
                self.logger.info(f"Attempting image generation with {provider.name}...")
                return provider.generate_image(prompt, **kwargs)
            except Exception as e:
                self.logger.warning(f"{provider.name} failed: {str(e)[:100]}")
                if provider == providers[-1]:  # Last provider
                    raise Exception(f"All image providers failed. Last error: {e}")
                self.logger.info(f"Falling back to next provider...")

        raise Exception("Image generation failed with all providers")

    def generate_voice_with_fallback(self, text: str, **kwargs) -> bytes:
        """Try to generate voice using available providers in priority order"""
        providers = self.get_available_providers(self.voice_providers)

        if not providers:
            raise Exception("No voice providers available. Please configure at least one API key.")

        for provider in providers:
            try:
                self.logger.info(f"Attempting voice generation with {provider.name}...")
                return provider.generate_voice(text, **kwargs)
            except Exception as e:
                self.logger.warning(f"{provider.name} failed: {str(e)[:100]}")
                if provider == providers[-1]:  # Last provider
                    raise Exception(f"All voice providers failed. Last error: {e}")
                self.logger.info(f"Falling back to next provider...")

        raise Exception("Voice generation failed with all providers")

    def get_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        status = {
            "script_providers": [],
            "image_providers": [],
            "voice_providers": []
        }

        for provider in self.script_providers:
            status["script_providers"].append({
                "name": provider.name,
                "priority": provider.priority,
                "available": provider.is_available(),
                "connected": provider.test_connection() if provider.is_available() else False
            })

        for provider in self.image_providers:
            status["image_providers"].append({
                "name": provider.name,
                "priority": provider.priority,
                "available": provider.is_available(),
                "connected": provider.test_connection() if provider.is_available() else False
            })

        for provider in self.voice_providers:
            status["voice_providers"].append({
                "name": provider.name,
                "priority": provider.priority,
                "available": provider.is_available(),
                "connected": provider.test_connection() if provider.is_available() else False
            })

        return status


if __name__ == "__main__":
    # Test the provider system
    logging.basicConfig(level=logging.INFO)

    manager = ProviderManager()
    status = manager.get_status()

    print("\n" + "="*60)
    print("PROVIDER STATUS")
    print("="*60)

    print("\nScript Providers:")
    for p in status["script_providers"]:
        if p["connected"]:
            symbol = "[OK]"
        elif p["available"]:
            symbol = "[WARN]"
        else:
            symbol = "[FAIL]"
        print(f"  {symbol} {p['name']} (Priority: {p['priority']})")

    print("\nImage Providers:")
    for p in status["image_providers"]:
        if p["connected"]:
            symbol = "[OK]"
        elif p["available"]:
            symbol = "[WARN]"
        else:
            symbol = "[FAIL]"
        print(f"  {symbol} {p['name']} (Priority: {p['priority']})")

    print("\nVoice Providers:")
    for p in status["voice_providers"]:
        if p["connected"]:
            symbol = "[OK]"
        elif p["available"]:
            symbol = "[WARN]"
        else:
            symbol = "[FAIL]"
        print(f"  {symbol} {p['name']} (Priority: {p['priority']})")

    print("\n" + "="*60)
