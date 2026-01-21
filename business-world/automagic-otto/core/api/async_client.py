#!/usr/bin/env python3
"""
Async API Client with Connection Pooling and Circuit Breaker
High-performance API client with retry logic, caching, and resource management
"""

import asyncio
import aiohttp
import time
import hashlib
import json
import logging
from typing import Dict, Any, Optional, List, Union, AsyncGenerator
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
from pathlib import Path
import openai
from elevenlabs.client import AsyncElevenLabs
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from ..config import get_config

logger = logging.getLogger("AutoMagic.API")

@dataclass
class CircuitBreaker:
    """Circuit breaker for API resilience"""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    half_open_max_calls: int = 3
    
    failures: int = field(default=0)
    last_failure_time: float = field(default=0)
    state: str = field(default="closed")  # closed, open, half_open
    
    def can_execute(self) -> bool:
        """Check if request can be executed based on circuit state"""
        if self.state == "closed":
            return True
        elif self.state == "open":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half_open"
                self.failures = 0
                return True
            return False
        elif self.state == "half_open":
            return self.failures < self.half_open_max_calls
        return False
    
    def on_success(self):
        """Record successful execution"""
        if self.state == "half_open":
            self.state = "closed"
        self.failures = 0
    
    def on_failure(self):
        """Record failed execution"""
        self.failures += 1
        self.last_failure_time = time.time()
        
        if self.failures >= self.failure_threshold:
            self.state = "open"

class APICache:
    """In-memory cache for API responses"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, float] = {}
    
    def _generate_key(self, method: str, params: Dict[str, Any]) -> str:
        """Generate cache key from method and parameters"""
        key_data = {"method": method, "params": params}
        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
    
    def get(self, method: str, params: Dict[str, Any]) -> Optional[Any]:
        """Get cached response"""
        key = self._generate_key(method, params)
        
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        if time.time() - entry["timestamp"] > self.ttl:
            self._evict(key)
            return None
        
        self._access_times[key] = time.time()
        return entry["data"]
    
    def set(self, method: str, params: Dict[str, Any], data: Any):
        """Cache response"""
        key = self._generate_key(method, params)
        
        # Evict old entries if cache is full
        if len(self._cache) >= self.max_size:
            self._evict_lru()
        
        self._cache[key] = {
            "data": data,
            "timestamp": time.time()
        }
        self._access_times[key] = time.time()
    
    def _evict(self, key: str):
        """Remove entry from cache"""
        self._cache.pop(key, None)
        self._access_times.pop(key, None)
    
    def _evict_lru(self):
        """Evict least recently used entry"""
        if not self._access_times:
            return
        
        lru_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        self._evict(lru_key)

class AsyncAPIClient:
    """High-performance async API client with connection pooling"""
    
    def __init__(self):
        self.config = get_config()
        self.session: Optional[aiohttp.ClientSession] = None
        self.openai_client: Optional[openai.AsyncOpenAI] = None
        self.elevenlabs_client: Optional[AsyncElevenLabs] = None
        
        # Performance features
        self.cache = APICache()
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.rate_limiters: Dict[str, List[float]] = {}
        
        # Connection settings
        self.connector = aiohttp.TCPConnector(
            limit=self.config.api.connection_pool_size,
            limit_per_host=5,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        self.timeout = aiohttp.ClientTimeout(total=self.config.api.timeout)
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def initialize(self):
        """Initialize all API clients"""
        # HTTP session
        self.session = aiohttp.ClientSession(
            connector=self.connector,
            timeout=self.timeout
        )
        
        # OpenAI client
        if self.config.api.openai_api_key:
            self.openai_client = openai.AsyncOpenAI(
                api_key=self.config.api.openai_api_key,
                max_retries=0  # We handle retries ourselves
            )
        
        # ElevenLabs client
        if self.config.api.elevenlabs_api_key:
            self.elevenlabs_client = AsyncElevenLabs(
                api_key=self.config.api.elevenlabs_api_key
            )
        
        logger.info("AsyncAPIClient initialized with connection pooling")
    
    async def close(self):
        """Close all connections"""
        if self.session:
            await self.session.close()
        
        if self.openai_client:
            await self.openai_client.close()
        
        logger.info("AsyncAPIClient closed")
    
    def _get_circuit_breaker(self, service: str) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        if service not in self.circuit_breakers:
            self.circuit_breakers[service] = CircuitBreaker()
        return self.circuit_breakers[service]
    
    def _check_rate_limit(self, service: str) -> bool:
        """Check if we're within rate limits"""
        now = time.time()
        
        if service not in self.rate_limiters:
            self.rate_limiters[service] = []
        
        # Remove old requests (older than 1 minute)
        self.rate_limiters[service] = [
            timestamp for timestamp in self.rate_limiters[service]
            if now - timestamp < 60
        ]
        
        # Check if under rate limit
        return len(self.rate_limiters[service]) < self.config.api.rate_limit_rpm
    
    def _record_request(self, service: str):
        """Record a new request for rate limiting"""
        if service not in self.rate_limiters:
            self.rate_limiters[service] = []
        
        self.rate_limiters[service].append(time.time())
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((openai.RateLimitError, openai.APITimeoutError, aiohttp.ClientError))
    )
    async def generate_content_idea(self, themes: Optional[List[str]] = None) -> str:
        """Generate content idea using OpenAI with caching and circuit breaker"""
        service = "openai_content"
        circuit_breaker = self._get_circuit_breaker(service)
        
        if not circuit_breaker.can_execute():
            raise Exception(f"Circuit breaker open for {service}")
        
        if not self._check_rate_limit(service):
            await asyncio.sleep(60 / self.config.api.rate_limit_rpm)
        
        # Check cache
        cache_params = {"themes": themes or []}
        cached = self.cache.get("content_idea", cache_params)
        if cached:
            logger.debug("Using cached content idea")
            return cached
        
        try:
            self._record_request(service)
            
            if not themes:
                themes = self.config.production.content_themes
            
            theme_list = ", ".join(themes)
            prompt = f"""Generate an engaging YouTube video topic related to: {theme_list}.
            The topic should be:
            1. Clickable and interesting
            2. Suitable for visual storytelling
            3. Trending or educational
            4. Under 10 words
            
            Return only the topic title, nothing else."""
            
            response = await self.openai_client.chat.completions.create(
                model=self.config.api.openai_model,
                messages=[
                    {"role": "system", "content": "You are a creative YouTube content strategist."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.8
            )
            
            topic = response.choices[0].message.content.strip().strip('"')
            
            # Cache the result
            self.cache.set("content_idea", cache_params, topic)
            circuit_breaker.on_success()
            
            logger.info(f"Generated content idea: {topic}")
            return topic
            
        except Exception as e:
            circuit_breaker.on_failure()
            logger.error(f"Failed to generate content idea: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate_script(self, topic: str) -> str:
        """Generate video script using OpenAI"""
        service = "openai_script"
        circuit_breaker = self._get_circuit_breaker(service)
        
        if not circuit_breaker.can_execute():
            raise Exception(f"Circuit breaker open for {service}")
        
        # Check cache
        cache_params = {"topic": topic}
        cached = self.cache.get("script", cache_params)
        if cached:
            logger.debug("Using cached script")
            return cached
        
        try:
            self._record_request(service)
            
            prompt = f"""Create a concise and engaging YouTube video script for: "{topic}"
            
Structure:
- **Hook** (2-3 sentences to grab attention)
- **Main Content** (3 key points, 2-3 sentences each)
- **Conclusion** (Call to action, 2-3 sentences)

Requirements:
- Conversational tone
- Under 200 words total
- Suitable for {self.config.video.duration} second video
- Include visual cues in [brackets]

Format as plain text with clear sections."""
            
            response = await self.openai_client.chat.completions.create(
                model=self.config.api.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert YouTube script writer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.7
            )
            
            script = response.choices[0].message.content.strip()
            
            # Cache the result
            self.cache.set("script", cache_params, script)
            circuit_breaker.on_success()
            
            logger.info(f"Generated script for topic: {topic}")
            return script
            
        except Exception as e:
            circuit_breaker.on_failure()
            logger.error(f"Failed to generate script: {e}")
            raise
    
    async def generate_images(self, script: str, count: int = 3) -> List[str]:
        """Generate images using DALL-E with parallel processing"""
        service = "openai_images"
        circuit_breaker = self._get_circuit_breaker(service)
        
        if not circuit_breaker.can_execute():
            raise Exception(f"Circuit breaker open for {service}")
        
        try:
            # Extract visual cues from script
            import re
            visual_cues = re.findall(r'\[([^\]]+)\]', script)
            
            if not visual_cues:
                # Generate generic prompts based on script content
                lines = [line.strip() for line in script.split('\n') if line.strip()]
                visual_cues = [f"Visual representation of: {line}" for line in lines[:count]]
            
            # Limit to requested count
            visual_cues = visual_cues[:count]
            
            # Generate images concurrently
            tasks = []
            for i, prompt in enumerate(visual_cues):
                task = self._generate_single_image(prompt, i + 1)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter successful results
            image_paths = []
            for result in results:
                if isinstance(result, str) and result:
                    image_paths.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"Image generation failed: {result}")
            
            circuit_breaker.on_success()
            logger.info(f"Generated {len(image_paths)} images")
            return image_paths
            
        except Exception as e:
            circuit_breaker.on_failure()
            logger.error(f"Failed to generate images: {e}")
            raise
    
    async def _generate_single_image(self, prompt: str, index: int) -> str:
        """Generate a single image"""
        try:
            self._record_request("openai_images")
            
            # Enhance prompt for better results
            enhanced_prompt = f"{prompt}, high quality, professional, clean background, 16:9 aspect ratio"
            
            response = await self.openai_client.images.generate(
                model=self.config.api.dalle_model,
                prompt=enhanced_prompt,
                n=1,
                size=self.config.api.dalle_image_size,
                response_format="url"
            )
            
            image_url = response.data[0].url
            
            # Download image
            async with self.session.get(image_url) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    
                    # Save image
                    image_path = self.config.paths.image_save_path / f"generated_image_{index}_{int(time.time())}.png"
                    
                    with open(image_path, 'wb') as f:
                        f.write(image_data)
                    
                    logger.debug(f"Saved image: {image_path}")
                    return str(image_path)
                else:
                    raise Exception(f"Failed to download image: HTTP {resp.status}")
                    
        except Exception as e:
            logger.error(f"Failed to generate image {index}: {e}")
            
            # Create fallback image
            return await self._create_fallback_image(prompt, index)
    
    async def _create_fallback_image(self, prompt: str, index: int) -> str:
        """Create a fallback image using PIL"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create image
            img = Image.new('RGB', (1280, 720), color=(64, 128, 255))
            draw = ImageDraw.Draw(img)
            
            # Add text
            try:
                font = ImageFont.truetype("arial.ttf", 36)
            except:
                font = ImageFont.load_default()
            
            # Wrap text
            words = prompt.split()
            lines = []
            current_line = []
            
            for word in words:
                current_line.append(word)
                if len(' '.join(current_line)) > 40:
                    lines.append(' '.join(current_line[:-1]))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Draw text
            y_offset = 300
            for line in lines[:4]:  # Max 4 lines
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (1280 - text_width) // 2
                draw.text((x, y_offset), line, fill=(255, 255, 255), font=font)
                y_offset += 50
            
            # Save fallback image
            fallback_path = self.config.paths.image_save_path / f"fallback_image_{index}_{int(time.time())}.png"
            img.save(fallback_path)
            
            logger.info(f"Created fallback image: {fallback_path}")
            return str(fallback_path)
            
        except Exception as e:
            logger.error(f"Failed to create fallback image: {e}")
            return ""
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate_voice(self, text: str) -> str:
        """Generate voice using ElevenLabs"""
        service = "elevenlabs"
        circuit_breaker = self._get_circuit_breaker(service)
        
        if not circuit_breaker.can_execute():
            raise Exception(f"Circuit breaker open for {service}")
        
        if not self.elevenlabs_client:
            raise Exception("ElevenLabs client not initialized")
        
        try:
            self._record_request(service)
            
            # Clean text for speech
            clean_text = self._clean_text_for_speech(text)
            
            # Generate audio
            audio_generator = await self.elevenlabs_client.generate(
                text=clean_text,
                voice=self.config.api.elevenlabs_voice_id or "Rachel",
                model=self.config.api.elevenlabs_model_id
            )
            
            # Save audio
            audio_path = self.config.paths.audio_save_path / f"voiceover_{int(time.time())}.mp3"
            
            with open(audio_path, 'wb') as f:
                async for chunk in audio_generator:
                    f.write(chunk)
            
            circuit_breaker.on_success()
            logger.info(f"Generated voice audio: {audio_path}")
            return str(audio_path)
            
        except Exception as e:
            circuit_breaker.on_failure()
            logger.error(f"Failed to generate voice: {e}")
            
            # Create fallback silent audio
            return await self._create_fallback_audio(text)
    
    def _clean_text_for_speech(self, text: str) -> str:
        """Clean text for better speech synthesis"""
        import re
        
        # Remove visual cues
        text = re.sub(r'\[([^\]]+)\]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove markdown formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Italic
        text = re.sub(r'#{1,6}\s*', '', text)           # Headers
        
        return text
    
    async def _create_fallback_audio(self, text: str) -> str:
        """Create fallback silent audio"""
        try:
            import subprocess
            
            duration = min(len(text.split()) * 0.5, self.config.video.duration)  # ~0.5 seconds per word
            audio_path = self.config.paths.audio_save_path / f"fallback_audio_{int(time.time())}.mp3"
            
            # Create silent audio with FFmpeg
            process = await asyncio.create_subprocess_exec(
                'ffmpeg', '-f', 'lavfi', '-i', f'anullsrc=r=44100:cl=mono',
                '-t', str(duration), '-q:a', '9', '-acodec', 'libmp3lame',
                str(audio_path), '-y',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"Created fallback audio: {audio_path}")
                return str(audio_path)
            else:
                logger.error("Failed to create fallback audio with FFmpeg")
                return ""
                
        except Exception as e:
            logger.error(f"Failed to create fallback audio: {e}")
            return ""

@asynccontextmanager
async def get_api_client():
    """Get async API client context manager"""
    client = AsyncAPIClient()
    try:
        await client.initialize()
        yield client
    finally:
        await client.close()