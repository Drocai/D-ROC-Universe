# 🎵 GROUP GROOVE - Complete Platform

**Making Music Great Again** - Social music voting with democracy, discovery, and dollars.

## 📁 Project Structure

```
group-groove/
├── backend/                 # Cloudflare Workers API
│   ├── worker.js           # Complete API (auth, rooms, voting, friends, etc.)
│   └── wrangler.toml       # Cloudflare deployment config
├── mobile/                  # React Native App
│   ├── App.js              # Complete app with all screens
│   └── package.json        # Dependencies
├── web/                     # Web Jukebox
│   └── index.html          # Single-file web app
├── shared/                  # Shared code
│   └── api.js              # API service for both platforms
└── README.md
```

## 🚀 Quick Start

### 1. Deploy Backend (Cloudflare Workers)

```bash
cd backend

# Install Wrangler CLI
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Create D1 database
wrangler d1 create group-groove-db

# Copy the database_id from output and update wrangler.toml

# Deploy the worker
wrangler deploy

# Run database migrations
curl -X POST https://your-worker.workers.dev/api/migrate
```

**Your API is now live at:** `https://group-groove-api.YOUR_SUBDOMAIN.workers.dev`

### 2. Configure Spotify API

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Get your Client ID and Client Secret
4. Add them to Cloudflare Workers environment:

```bash
wrangler secret put SPOTIFY_CLIENT_ID
wrangler secret put SPOTIFY_CLIENT_SECRET
```

### 3. Deploy Web App

```bash
cd web

# Update API_URL in index.html
# Replace __API_URL__ with your worker URL

# Deploy to Netlify (drag & drop)
# Or use Cloudflare Pages:
npx wrangler pages deploy . --project-name=group-groove
```

**Web app live at:** `https://group-groove.pages.dev`

### 4. Run Mobile App

```bash
cd mobile

# Update API_URL in App.js
# Replace __API_URL__ with your worker URL

# Install dependencies
npm install

# Start Expo
npx expo start

# Scan QR code with Expo Go app
```

## 🔑 API Endpoints

### Auth
- `POST /api/auth/signup` - Create account
- `POST /api/auth/signin` - Sign in
- `GET /api/auth/profile` - Get profile
- `PUT /api/auth/profile` - Update profile

### Rooms
- `POST /api/rooms` - Create room
- `POST /api/rooms/join` - Join room
- `GET /api/rooms/:id` - Get room with queue, members, messages
- `DELETE /api/rooms/:id` - Leave room

### Queue & Voting
- `POST /api/rooms/:id/queue` - Add song to queue
- `POST /api/rooms/:id/vote` - Vote on song
- `POST /api/rooms/:id/skip` - Vote to skip
- `POST /api/rooms/:id/play-next` - Play next song (host only)

### Social
- `GET /api/friends` - Get friends list
- `POST /api/friends/request` - Send friend request
- `POST /api/friends/respond` - Accept/decline request
- `POST /api/messages` - Send DM
- `GET /api/messages/:friendId` - Get conversation

### Groups
- `GET /api/groups` - List groups
- `POST /api/groups` - Create group
- `POST /api/groups/join` - Join group

### Spotify
- `GET /api/spotify/search?q=query` - Search songs

## 💰 Freemium Tiers

| Feature | Free | Premium ($9.99/mo) | DJ Pro ($49.99/mo) |
|---------|------|--------------------|--------------------|
| Song Requests/Day | 5 | 50 | Unlimited |
| Max Room Size | 8 | 50 | 200 |
| Create Groups | ❌ | ✅ | ✅ |
| Priority Voting | ❌ | ✅ | ✅ |
| DJ Dashboard | ❌ | ❌ | ✅ |
| Analytics | ❌ | ❌ | ✅ |

## 🛠️ Environment Variables

Set these in Cloudflare dashboard or via `wrangler secret`:

```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
JWT_SECRET=your_super_secret_key
```

## 📱 Features

### Core
- ✅ User authentication (JWT)
- ✅ Room creation with 6-char codes
- ✅ Real-time song queue
- ✅ Democratic voting (up/down)
- ✅ Skip vote system (50% threshold)
- ✅ In-room chat

### Social
- ✅ Friends system
- ✅ Direct messages
- ✅ Groups (async playlists)
- ✅ Notifications

### Premium (Locked for Free users)
- 🔒 Unlimited requests
- 🔒 Create groups
- 🔒 Priority voting
- 🔒 Larger rooms
- 🔒 DJ dashboard
- 🔒 Analytics

## 🔄 Real-Time Updates

Currently using polling (3 second intervals). Both web and mobile apps poll the server for updates.

**Future:** WebSocket support via Cloudflare Durable Objects

## 🎯 For Grayson

This is **his inheritance**. Built with love, determination, and the belief that music should be social, democratic, and profitable.

**DDD Framework:**
- **Democracy** - Everyone votes on music
- **Discovery** - Social connection through music taste
- **Dollars** - Freemium monetization done right

---

## 📞 Support

Built by DaDDi at the Frequency Factory.

*Making Music Great Again* 🎵
