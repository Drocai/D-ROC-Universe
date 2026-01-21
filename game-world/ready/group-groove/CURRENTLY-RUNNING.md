# 🎵 GROUP GROOVE - Currently Running Services

## ✅ What's Running Right Now

### 1. Backend API (Cloudflare Workers)
- **Status**: ✅ RUNNING
- **URL**: http://localhost:8787
- **Features**:
  - User authentication (JWT)
  - Room creation/joining
  - Spotify music search
  - Voting system
  - Friends & messaging
  - Freemium tier system

### 2. Web App
- **Status**: ✅ RUNNING
- **URL**: http://localhost:8000
- **Access**: Open in your browser
- **Also available at**: http://172.20.10.2:8000

### 3. Mobile App (Expo)
- **Status**: 🔄 STARTING (Metro bundler loading)
- **Access**: Will show QR code when ready
- **App**: Install "Expo Go" on your phone to scan QR code

---

## 🧪 How to Test

### Web App Testing
1. Go to: **http://localhost:8000**
2. Click "Sign Up"
3. Create account:
   - Email: `test@test.com`
   - Password: `test123`
   - Name: Your name
   - Username: `testuser`
4. Create a room or join one
5. Search for songs using Spotify
6. Add songs and vote!

### Mobile App Testing
1. Install **Expo Go** on your phone:
   - iOS: App Store - "Expo Go"
   - Android: Play Store - "Expo Go"
2. Make sure phone is on **same WiFi** as computer
3. Look for QR code in the terminal (may take a minute to load)
4. Scan QR code with Expo Go app
5. Test all features!

---

## 🎯 Features to Test

### Core Features
- ✅ User signup/signin
- ✅ Create room (generates 6-character code)
- ✅ Join room with code
- ✅ Search songs (Spotify API)
- ✅ Add songs to queue
- ✅ Vote to skip songs
- ✅ Real-time updates (polls every 3 seconds)

### Social Features
- ✅ Friends system (add, accept, decline)
- ✅ Direct messages between friends
- ✅ Groups (persistent playlists)
- ✅ Room chat

### Premium Features (Locked for Free Users)
- 🔒 Unlimited song requests (free: 5/day)
- 🔒 Create groups
- 🔒 Priority voting (2x weight for Premium)
- 🔒 Larger rooms (free: 8 users max)

---

## 🛠️ Troubleshooting

### Backend Issues
- Check terminal for errors
- Make sure Spotify credentials are correct
- Restart: Kill terminal and run `start-backend.bat`

### Web App Issues
- Clear browser cache
- Check browser console (F12)
- Make sure backend is running first

### Mobile App Issues
- If QR code doesn't appear, wait 1-2 minutes for Metro bundler
- If still loading, check terminal for errors
- Make sure phone is on same WiFi network
- API URL in App.js should be: `http://172.20.10.2:8787`

---

## 📊 Current Configuration

- **Backend**: http://localhost:8787
- **Web**: http://localhost:8000
- **Mobile API**: http://172.20.10.2:8787
- **Computer IP**: 172.20.10.2
- **Spotify**: ✅ Configured

---

## 🔄 To Restart Services

If you need to restart any service:

### Stop Current Services:
Press `Ctrl+C` in each terminal

### Restart:
1. **Backend**: Run `start-backend.bat`
2. **Web**: Run `start-web.bat`
3. **Mobile**: Run `start-mobile.bat`

Or just double-click the .bat files!

---

## 📱 Next Steps

1. **Test on Web** - Sign up and create a room
2. **Test on Mobile** - Join the same room from phone
3. **Test Features** - Add songs, vote, chat
4. **Deploy** - When ready, deploy to Cloudflare Workers

---

*Making Music Great Again* 🎵

**Questions?** Check START-HERE.md for more details
