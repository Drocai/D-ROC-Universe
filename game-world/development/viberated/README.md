# Vibe Rated 🎯

**Rate the vibe of any space with 17-second frequency analysis.** Measure sound, light, and stability to find your perfect work/chill spot.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Drocai/Same-show-new-season-)

## ✨ Features

### Core Functionality
- **17-Second Measurements**: Scientifically-calibrated environmental analysis
- **Multi-Metric Scoring**: Sound (dB), Light (lux), and Stability detection
- **Real-Time Feedback**: Live readings during measurement process
- **Location Discovery**: Interactive map with vibe scores
- **Resonance Gamification**: Earn vibrations, climb ranks, collect badges

### Technical Highlights
- **Progressive Web App (PWA)**: Install as native app on iOS/Android
- **Mobile-First Design**: Optimized for touch and small screens
- **Offline Support**: Service worker caching for offline functionality
- **Real Sensor Integration**: Microphone, ambient light, and accelerometer support
- **Supabase Backend**: Authentication, real-time data, and PostgreSQL database
- **Tailwind CSS**: Modern, responsive styling system

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Supabase account (free tier works great)
- Modern web browser with sensor support

### Installation

```bash
# Clone the repository
git clone https://github.com/Drocai/Same-show-new-season-.git
cd Same-show-new-season-

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Edit .env with your Supabase credentials
```

### Environment Setup

Create a `.env` file:

```env
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_ENABLE_REAL_SENSORS=true
```

### Database Setup

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Go to SQL Editor
3. Copy and paste `supabase/schema.sql`
4. Run the query

### Development

```bash
npm run dev
# Open http://localhost:3000
```

### Production Build

```bash
npm run build
npm run preview
```

## 🎮 Resonance System

### Ranks
| Rank | Name | Vibrations | Icon |
|------|------|------------|------|
| 1 | Listener | 0+ | 👂 |
| 2 | Sensor | 100+ | 📡 |
| 3 | Resonator | 500+ | 🔊 |
| 4 | Harmonizer | 1,500+ | 🎵 |
| 5 | Frequency Master | 5,000+ | ⚡ |

### Earning Vibrations
- Base measurement: +10
- High score (80+): +5 bonus
- Perfect score (90+): +10 bonus
- First of day: +5
- New location: +15
- Streak multiplier: up to 2x

## 🏗️ Project Structure

```
vibe-rated/
├── src/
│   ├── components/       # React components
│   ├── lib/             # Core libraries
│   ├── hooks/           # Custom hooks
│   ├── contexts/        # React contexts
│   ├── utils/           # Utilities
│   ├── constants/       # Constants
│   └── styles/          # Global styles
├── supabase/
│   └── schema.sql       # Database schema
├── public/              # Static assets
└── package.json
```

## 🚢 Deployment

### Vercel (Recommended)

1. Click "Deploy with Vercel" button
2. Connect GitHub repository
3. Add environment variables
4. Deploy!

### Environment Variables
- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`

## 📱 PWA Installation

**iOS**: Safari > Share > Add to Home Screen  
**Android**: Chrome > Menu > Install App

## 🔌 Real Sensors

Enable real device sensors:

```javascript
import { vibeAnalyzer } from './lib/vibeAnalyzer';

await vibeAnalyzer.initializeSensors();
const result = await vibeAnalyzer.startMeasurement({ useSensors: true });
```

## 📊 Performance

- Lighthouse Score: 90+
- First Contentful Paint: < 1.5s
- Bundle Size: ~275KB (gzipped)

## 🛠️ Development

```bash
npm run dev      # Start dev server
npm run build    # Build for production
npm run preview  # Preview build
npm run lint     # Run linter
npm run format   # Format code
```

## 📝 License


MIT

## 🙏 Acknowledgments

Built with Supabase, Vercel, React, Tailwind CSS, and Leaflet.

---

**Built with 💜 for the frequency-aware future.**