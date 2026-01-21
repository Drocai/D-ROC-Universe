# AutoMagic Multi-Provider System

## 🎯 Overview

This guide covers the new **Multi-Provider System** that replaces your OpenAI dependency with multiple API providers and automatic fallbacks. Now AutoMagic can use **FREE or very cheap alternatives** and automatically switch if one fails!

## ✨ What's New

### Before (Old System):
- ❌ Relied entirely on OpenAI (expensive + quota issues)
- ❌ Script generation failed when OpenAI quota exceeded
- ❌ DALL-E was the only image option
- ❌ No fallback options

### After (New System):
- ✅ Multiple providers for each component
- ✅ Automatic fallback if one fails
- ✅ FREE/cheap alternatives (Groq, Replicate, etc.)
- ✅ Priority-based provider selection
- ✅ Easy to add new providers

## 📦 New Files Created

1. **`api_providers.py`** - Core provider system with all integrations
2. **`automagic_multi_provider.py`** - Updated main script using providers
3. **`setup_providers.py`** - Setup and testing tool
4. **`.env.template`** - Configuration template for API keys
5. **`requirements_multi_provider.txt`** - Updated dependencies
6. **`MULTI_PROVIDER_GUIDE.md`** - This guide!

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd C:\Users\djmc1\Desktop\AutoMagic
python -m pip install -r requirements_multi_provider.txt
```

### Step 2: Configure API Keys

You need at least **ONE provider per category** (script, image, voice).

#### Recommended FREE/Cheap Setup:

**For Script Generation - Choose ONE:**
- **Groq** (Recommended - FREE, fast)
  - Get key: https://console.groq.com/
  - Add to `.env`: `GROQ_API_KEY=your_key_here`

- **Google Gemini** (FREE tier)
  - Get key: https://aistudio.google.com/app/apikey
  - Add to `.env`: `GEMINI_API_KEY=your_key_here`

**For Image Generation - Choose ONE:**
- **Replicate** (Recommended - Very cheap: ~$0.003/image)
  - Get key: https://replicate.com/account/api-tokens
  - Add to `.env`: `REPLICATE_API_KEY=your_key_here`

- **HuggingFace** (FREE with limits)
  - Get key: https://huggingface.co/settings/tokens
  - Add to `.env`: `HUGGINGFACE_API_KEY=your_key_here`

**For Voice - Keep Existing or Add:**
- Keep your **ElevenLabs** key (already configured), OR
- Add **Google TTS** (FREE tier)
  - Enable at: https://console.cloud.google.com/
  - Add to `.env`: `GOOGLE_TTS_API_KEY=your_key_here`

### Step 3: Run Setup Script

```bash
python setup_providers.py
```

This will:
- ✅ Install any missing dependencies
- ✅ Check your .env configuration
- ✅ Test all provider connections
- ✅ Show you what's working

### Step 4: Check Provider Status

```bash
python automagic_multi_provider.py --status
```

You should see something like:
```
PROVIDER STATUS
==============================================================

📝 Script Providers:
  ✅ Groq (Priority: 1)
  ❌ Gemini (Priority: 2)
  ❌ OpenAI (Priority: 3)

🎨 Image Providers:
  ✅ Replicate (Priority: 1)
  ❌ HuggingFace (Priority: 2)
  ❌ Stability (Priority: 3)

🎤 Voice Providers:
  ✅ ElevenLabs (Priority: 1)
  ❌ GoogleTTS (Priority: 2)
```

### Step 5: Run Production!

```bash
python automagic_multi_provider.py --now
```

## 🔄 How Fallbacks Work

The system tries providers in **priority order** and automatically falls back if one fails:

### Example: Script Generation

1. **Tries Groq first** (Priority 1)
   - ✅ If success → uses the script
   - ❌ If fails → logs error and tries next

2. **Tries Gemini** (Priority 2)
   - ✅ If success → uses the script
   - ❌ If fails → logs error and tries next

3. **Tries OpenAI** (Priority 3)
   - ✅ If success → uses the script
   - ❌ If all fail → uses fallback script template

### Example Log Output:
```
INFO - Attempting script generation with Groq...
INFO - ✅ Script generated with Groq (1234 chars)
```

Or if Groq fails:
```
INFO - Attempting script generation with Groq...
WARNING - Groq failed: Rate limit exceeded
INFO - Falling back to next provider...
INFO - Attempting script generation with Gemini...
INFO - ✅ Script generated with Gemini (1187 chars)
```

## 🎨 Supported Providers

### Script Generation (AI Text):
| Provider | Priority | Cost | Speed | Quality |
|----------|----------|------|-------|---------|
| **Groq** | 1 | FREE | ⚡ Ultra-fast | ⭐⭐⭐⭐ |
| **Gemini** | 2 | FREE | Fast | ⭐⭐⭐⭐⭐ |
| **OpenAI** | 3 | Paid | Fast | ⭐⭐⭐⭐⭐ |

### Image Generation:
| Provider | Priority | Cost | Speed | Quality |
|----------|----------|------|-------|---------|
| **Replicate** | 1 | ~$0.003/img | Fast | ⭐⭐⭐⭐⭐ |
| **HuggingFace** | 2 | FREE | Medium | ⭐⭐⭐⭐ |
| **Stability** | 3 | ~$0.01/img | Fast | ⭐⭐⭐⭐⭐ |

### Voice Synthesis:
| Provider | Priority | Cost | Speed | Quality |
|----------|----------|------|-------|---------|
| **ElevenLabs** | 1 | Paid | Fast | ⭐⭐⭐⭐⭐ |
| **Google TTS** | 2 | FREE tier | Fast | ⭐⭐⭐⭐ |

## 💰 Cost Comparison

### Old System (OpenAI only):
- GPT-3.5-turbo: ~$0.002 per 1k tokens (script ~$0.002)
- DALL-E 2: $0.02 per image × 3 = $0.06
- **Total per video: ~$0.062** (plus your ElevenLabs cost)

### New Recommended Setup (Groq + Replicate):
- Groq: FREE (14,400 requests/day)
- Replicate FLUX: ~$0.003 per image × 3 = $0.009
- **Total per video: ~$0.009** (plus your ElevenLabs cost)

**Savings: ~85% cheaper!** 🎉

## 🛠️ Advanced Configuration

### Change Provider Priority

Edit `api_providers.py` and change the `priority` values:

```python
class GroqScriptProvider(ScriptProvider):
    def __init__(self):
        super().__init__("Groq", priority=1)  # Lower = higher priority
```

### Add More Providers

The system is designed to be extensible. To add a new provider:

1. Create a new class inheriting from the appropriate base class
2. Implement required methods: `is_available()`, `test_connection()`, `generate_*()`
3. Add it to the ProviderManager's list

Example:
```python
class MyNewScriptProvider(ScriptProvider):
    def __init__(self):
        super().__init__("MyProvider", priority=4)
        self.api_key = os.getenv("MYNEW_API_KEY")

    def is_available(self) -> bool:
        return bool(self.api_key)

    def test_connection(self) -> bool:
        # Test the API
        return True

    def generate_script(self, topic: str, **kwargs) -> str:
        # Generate script using your API
        return script
```

### Configure Models

Change which models are used via environment variables:

```bash
# .env
GROQ_MODEL=llama-3.1-70b-versatile
GEMINI_MODEL=gemini-1.5-flash
REPLICATE_MODEL=black-forest-labs/flux-schnell
HUGGINGFACE_MODEL=black-forest-labs/FLUX.1-schnell
```

## 🧪 Testing

### Test Individual Components

Test just script generation:
```python
from api_providers import ProviderManager

manager = ProviderManager()
script = manager.generate_script_with_fallback("AI and the future")
print(script)
```

Test just image generation:
```python
from api_providers import ProviderManager

manager = ProviderManager()
image_data = manager.generate_image_with_fallback("A futuristic city")
with open("test.jpg", "wb") as f:
    f.write(image_data)
```

### Run Provider Status Check

```bash
python api_providers.py
```

This standalone test shows which providers are configured and working.

## 🔧 Troubleshooting

### "No providers available" error

**Problem:** No API keys configured for that category

**Solution:** Add at least one API key to `.env`:
```bash
# For scripts, add ONE of:
GROQ_API_KEY=your_key
# or
GEMINI_API_KEY=your_key
```

### "All providers failed" error

**Problem:** All configured providers returned errors

**Solution:**
1. Check your API keys are correct
2. Check your account has credits/quota
3. Test connection: `python setup_providers.py`
4. Check logs for specific errors

### Import errors

**Problem:** Missing dependencies

**Solution:**
```bash
python -m pip install -r requirements_multi_provider.txt
```

### Provider shows "⚠️" (available but not connected)

**Problem:** API key is set but connection test failed

**Possible causes:**
- Wrong API key
- No internet connection
- Service is down
- Account not activated

**Solution:**
1. Verify the API key in your provider dashboard
2. Check if you need to activate the service
3. Try the connection test again

## 📊 Monitoring

### Check Logs

```bash
tail -f logs/automagic_multi.log
```

### View Provider Usage

The logs show which provider was used for each generation:

```
INFO - Attempting script generation with Groq...
INFO - ✅ Script generated with Groq (1234 chars)
INFO - Attempting image generation with Replicate...
INFO - ✅ Image generated with Replicate (245678 bytes)
INFO - Attempting voice generation with ElevenLabs...
INFO - ✅ Voice generated with ElevenLabs (1456789 bytes)
```

## 🎯 Next Steps

### Option 1: Keep Using Original Script

Your original `automagic.py` still works! To upgrade it to use the new providers:

1. Import the provider manager: `from api_providers import ProviderManager`
2. Replace OpenAI calls with provider manager calls
3. See `automagic_multi_provider.py` for examples

### Option 2: Use the New Multi-Provider Script

The new `automagic_multi_provider.py` is a cleaner implementation:

```bash
# Run immediately
python automagic_multi_provider.py --now

# Check status
python automagic_multi_provider.py --status
```

### Option 3: Add Video Generation

Want to add AI video generation (Kling, Runway, Luma)?

Let me know and I can add providers for:
- **Kling AI** - Chinese service, good pricing
- **Runway Gen-2/Gen-3** - Professional quality
- **Luma AI Dream Machine** - Good free tier

## 📝 Summary

You now have a **robust, cost-effective video production system** with:

✅ Multiple API providers
✅ Automatic fallbacks
✅ 85% cost reduction (with recommended setup)
✅ No more quota issues
✅ Easy to extend

**Recommended Next Action:**

1. Get a Groq API key (FREE): https://console.groq.com/
2. Get a Replicate API key (cheap): https://replicate.com/
3. Run `python setup_providers.py`
4. Run `python automagic_multi_provider.py --now`

Enjoy your upgraded AutoMagic! 🎬✨
