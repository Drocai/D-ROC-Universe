# Group Groove - Local Testing Setup

## Current Status: Ready for Local Testing

### Backend (Cloudflare Workers - Local)
- ✅ Wrangler CLI installed
- ⏳ Spotify credentials needed
- Ready to run with: `wrangler dev`

### Web App
- ✅ Single HTML file ready
- Will run on local server
- Access at: `http://localhost:8000`

### Mobile App
- ✅ Dependencies installed
- ✅ Expo ready
- Will run with: `npm start`

## Quick Start (Local Testing)

### 1. Get Spotify Credentials
1. Go to: https://developer.spotify.com/dashboard
2. Create new app: "Group Groove"
3. Copy Client ID and Client Secret
4. Update `backend/.dev.vars` with your credentials

### 2. Start Backend (Terminal 1)
```bash
cd C:\Users\djmc1\group-groove-production\backend
wrangler dev
```
Backend will run at: `http://localhost:8787`

### 3. Start Web App (Terminal 2)
```bash
cd C:\Users\djmc1\group-groove-production\web
npx http-server -p 8000
```
Web app at: `http://localhost:8000`

### 4. Start Mobile App (Terminal 3)
```bash
cd C:\Users\djmc1\group-groove-production\mobile
npm start
```
Scan QR code with Expo Go app

## API Configuration

### For Local Testing:
- Backend: `http://localhost:8787`
- Web app will use: `http://localhost:8787`
- Mobile app will use: Your computer's IP address (e.g., `http://192.168.1.100:8787`)

## Next Steps After Local Testing:
1. Deploy backend to Cloudflare Workers (free tier)
2. Deploy web to Cloudflare Pages (free)
3. Update mobile app with production API URL
4. Build mobile apps with EAS

---
*Making Music Great Again* 🎵
