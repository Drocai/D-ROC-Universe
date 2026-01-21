# 🎵 GROUP GROOVE - START HERE

## ⚡ Quick Start Guide

### STEP 1: Get Spotify Credentials (One-Time Setup)

1. Go to: https://developer.spotify.com/dashboard
2. Log in with your Spotify account
3. Click "Create App"
4. Fill in:
   - App Name: `Group Groove`
   - App Description: `Democratic music voting app`
   - Redirect URI: `http://localhost:8787/callback`
   - Check "Web API"
5. Click "Save"
6. Copy your **Client ID** and **Client Secret**
7. Open `backend\.dev.vars` and replace:
   ```
   SPOTIFY_CLIENT_ID=your_spotify_client_id_here
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
   ```

### STEP 2: Start the Backend

**Option A: Double-click**
- Double-click `start-backend.bat`

**Option B: Command line**
```bash
cd C:\Users\djmc1\group-groove-production
start-backend.bat
```

✅ Backend running at: **http://localhost:8787**

### STEP 3: Start the Web App (New Terminal)

**Option A: Double-click**
- Double-click `start-web.bat`

**Option B: Command line**
```bash
cd C:\Users\djmc1\group-groove-production
start-web.bat
```

✅ Web app running at: **http://localhost:8000**

### STEP 4: Start the Mobile App (New Terminal)

**Option A: Double-click**
- Double-click `start-mobile.bat`

**Option B: Command line**
```bash
cd C:\Users\djmc1\group-groove-production
start-mobile.bat
```

✅ Mobile app: Scan QR code with **Expo Go** app

---

## 📱 Testing the Mobile App

1. Install **Expo Go** on your phone:
   - iOS: https://apps.apple.com/app/expo-go/id982107779
   - Android: https://play.google.com/store/apps/details?id=host.exp.exponent

2. Make sure your phone is on the **same WiFi network** as your computer

3. Open Expo Go and scan the QR code from the terminal

---

## 🧪 Testing the App

### Web App (http://localhost:8000)
1. Open browser to http://localhost:8000
2. Click "Sign Up"
3. Create an account (email: test@test.com, password: test123)
4. Create a room or join one
5. Search for songs (Spotify integration)
6. Add songs and vote!

### Mobile App
1. Open Expo Go and scan QR
2. Sign up/Sign in
3. Create or join a room
4. Test all features

---

## 🐛 Troubleshooting

### Backend won't start
- Make sure you updated Spotify credentials in `backend\.dev.vars`
- Check if port 8787 is already in use

### Web app won't connect to backend
- Make sure backend is running first
- Check console for errors

### Mobile app can't connect
- Make sure phone is on same WiFi
- Check that API_URL in `mobile\App.js` matches your computer's IP
- Your computer IP: **172.20.10.2**

### "Spotify search not working"
- Double-check Spotify credentials in `backend\.dev.vars`
- Make sure there are no extra spaces

---

## ✅ Current Configuration

- **Backend**: http://localhost:8787
- **Web App**: http://localhost:8000
- **Mobile API**: http://172.20.10.2:8787
- **Your Computer IP**: 172.20.10.2

---

## 🚀 Next Steps After Testing

1. **Deploy Backend** to Cloudflare Workers (free tier)
2. **Deploy Web App** to Cloudflare Pages (free)
3. **Build Mobile Apps** with EAS (iOS + Android)
4. **Add Payment Integration** (Stripe for premium tiers)

---

**Need help?** Check SETUP.md for more details

*Making Music Great Again* 🎵
