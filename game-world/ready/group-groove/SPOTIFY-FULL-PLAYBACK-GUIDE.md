# 🎵 SPOTIFY FULL PLAYBACK - How To Guide

## ❓ WHY ONLY 30 SECONDS?

### Spotify API Limitation

**Current Setup**:
- Uses **Spotify Web API** (free tier)
- Only provides **30-second preview URLs** for tracks
- These are MP3 clips hosted by Spotify
- Not all songs have previews (older/regional content)

**This is a Spotify Policy**, not a technical limitation.

---

## 🎧 HOW TO GET FULL SONGS

To play full-length songs, you need **Spotify Web Playback SDK**. Here's what's required:

### Requirements:
1. **Spotify Premium Account** (users must have Premium)
2. **OAuth Authentication** (not anonymous login)
3. **Web Playback SDK Integration**
4. **Different Architecture**

---

## 🛠️ IMPLEMENTATION STEPS

### Step 1: Switch to Spotify OAuth

**Current**: Anonymous username-based auth
**Needed**: Spotify OAuth 2.0

```javascript
// Redirect users to Spotify login
const authUrl = 'https://accounts.spotify.com/authorize?' +
  `client_id=${SPOTIFY_CLIENT_ID}&` +
  `response_type=code&` +
  `redirect_uri=${REDIRECT_URI}&` +
  `scope=streaming user-read-email user-read-private`;

window.location = authUrl;
```

**Required Scopes**:
- `streaming` - Play music in the browser
- `user-read-email` - Get user info
- `user-read-private` - Access user account

### Step 2: Update Spotify App Settings

In [Spotify Developer Dashboard](https://developer.spotify.com/dashboard):

1. **Edit Settings** for your "Group Groove" app
2. **Add Redirect URIs**:
   - `http://localhost:8000/callback` (development)
   - `https://your-domain.com/callback` (production)
3. **Enable Web Playback SDK**

### Step 3: Initialize Spotify Web Playback SDK

Add to your web app:

```html
<script src="https://sdk.scdn.co/spotify-player.js"></script>
```

```javascript
window.onSpotifyWebPlaybackSDKReady = () => {
  const player = new Spotify.Player({
    name: 'Group Groove Player',
    getOAuthToken: cb => { cb(accessToken); }, // User's access token
    volume: 0.5
  });

  // Ready
  player.addListener('ready', ({ device_id }) => {
    console.log('Ready with Device ID', device_id);
    connectToDevice(device_id);
  });

  // Play
  player.addListener('player_state_changed', state => {
    if (!state) return;
    updateUI(state.track_window.current_track);
  });

  player.connect();
};
```

### Step 4: Play Tracks via Spotify API

```javascript
async function playSong(spotifyUri, deviceId) {
  await fetch(`https://api.spotify.com/v1/me/player/play?device_id=${deviceId}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      uris: [spotifyUri] // e.g., "spotify:track:4uLU6hMCjMI75M1A2tKUQC"
    })
  });
}
```

### Step 5: Update Database Schema

Store Spotify URIs instead of preview URLs:

```sql
ALTER TABLE queue_items ADD COLUMN spotify_uri TEXT;
```

Instead of:
```javascript
{ preview_url: 'https://...' }
```

Use:
```javascript
{ spotify_uri: 'spotify:track:4uLU6hMCjMI75M1A2tKUQC' }
```

---

## 🏗️ ARCHITECTURE CHANGES

### Current (Preview Only):
```
User → Web App → Spotify Web API → 30s MP3 → HTML5 Audio Player
```

### Full Playback:
```
User (Premium) → OAuth → Spotify Connect → Web Playback SDK → Full Song
```

---

## 📋 IMPLEMENTATION CHECKLIST

### Backend Changes:
- [ ] Add OAuth callback endpoint
- [ ] Store Spotify access tokens (encrypted)
- [ ] Refresh tokens when expired
- [ ] Check user Premium status
- [ ] Return Spotify URIs instead of preview URLs

### Frontend Changes:
- [ ] Add Spotify login button
- [ ] Handle OAuth callback
- [ ] Initialize Web Playback SDK
- [ ] Connect to Spotify device
- [ ] Control playback (play, pause, skip)
- [ ] Sync playback across all room members
- [ ] Show "Premium Required" for free users

### Database Changes:
- [ ] Store Spotify access tokens
- [ ] Store refresh tokens
- [ ] Store Spotify user IDs
- [ ] Add `spotify_uri` column to queue_items
- [ ] Add `is_premium` flag to users

---

## ⚠️ IMPORTANT LIMITATIONS

### Spotify Premium Required
- **All users in the room need Spotify Premium**
- Free Spotify users cannot use Web Playback SDK
- This is a Spotify policy, not changeable

### Playback Sync Challenges
- Each user plays on their own device
- Keeping everyone in sync is difficult
- Need to coordinate playback states
- Latency issues on slow connections

### Alternative: Host-Only Playback
**Better approach**:
- Only the **room host** needs Spotify Premium
- Host's Spotify account plays the music
- Others just see what's playing
- No sync issues
- Simpler implementation

---

## 🎯 RECOMMENDED APPROACH

For a democratic playlist app like Group Groove:

### Option 1: Hybrid Approach (Recommended)
1. **Keep 30-second previews** for everyone (current)
2. **Add optional Spotify Premium integration** for hosts only
3. Host can link their Premium account
4. When linked, full songs play on host's Spotify
5. Everyone else still sees queue/voting but hears previews

**Pros**:
- Works for all users
- Premium users get full experience
- No sync issues
- Simple to implement

### Option 2: Premium Only
1. Require all room members have Spotify Premium
2. Full Playback SDK integration
3. Sync playback across all devices

**Pros**:
- Full songs for everyone
- Professional experience

**Cons**:
- Excludes free Spotify users
- Complex sync logic
- More bugs/edge cases

### Option 3: Keep Previews (Current)
1. Stay with 30-second previews
2. Add disclaimer: "Preview mode - link Spotify Premium for full songs"
3. Focus on voting/queue features

**Pros**:
- Works for everyone
- No additional complexity
- Faster development

**Cons**:
- Only 30 seconds per song

---

## 💻 CODE EXAMPLE

Here's a minimal integration:

```javascript
// 1. User clicks "Connect Spotify Premium"
async function connectSpotify() {
  const scopes = 'streaming user-read-email user-read-private';
  const authUrl = `https://accounts.spotify.com/authorize?` +
    `client_id=${SPOTIFY_CLIENT_ID}&` +
    `response_type=code&` +
    `redirect_uri=${window.location.origin}/callback&` +
    `scope=${scopes}`;

  window.location = authUrl;
}

// 2. Handle callback
async function handleCallback() {
  const code = new URLSearchParams(window.location.search).get('code');

  // Exchange code for access token
  const response = await fetch('/api/spotify/callback', {
    method: 'POST',
    body: JSON.stringify({ code })
  });

  const { access_token } = await response.json();
  localStorage.setItem('spotify_token', access_token);

  initializePlayer(access_token);
}

// 3. Initialize player
function initializePlayer(token) {
  window.onSpotifyWebPlaybackSDKReady = () => {
    const player = new Spotify.Player({
      name: 'Group Groove',
      getOAuthToken: cb => cb(token)
    });

    player.connect();
  };
}

// 4. Play current queue item
async function playFromQueue(spotifyUri, token, deviceId) {
  await fetch(`https://api.spotify.com/v1/me/player/play?device_id=${deviceId}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ uris: [spotifyUri] })
  });
}
```

---

## 🎪 DEMO EXPERIENCE

For testing/demos without Premium, you can:

1. **Use preview URLs** (current setup)
2. Show "Premium Required" banner
3. Add upgrade prompt
4. Demonstrate queue/voting features

Most users will understand 30-second previews for testing.

---

## 📊 COST COMPARISON

### Current (Previews):
- **Cost**: $0
- **User Requirements**: None
- **API Calls**: Free Spotify Web API

### Full Playback:
- **Cost**: $0 (Spotify SDK is free)
- **User Requirements**: Spotify Premium ($9.99/mo per user)
- **API Calls**: Free, but needs OAuth

---

## 🚀 QUICK START (FULL PLAYBACK)

If you want to implement full playback today:

1. Update Spotify app redirect URIs
2. Add OAuth flow to backend
3. Add Spotify login button to frontend
4. Include Web Playback SDK script
5. Initialize player with user's token
6. Use `spotify:track:XXX` URIs instead of preview URLs

**Estimated Time**: 4-6 hours for basic implementation

---

## 🤔 SHOULD YOU DO IT?

**For MVP/Testing**: No, keep previews
**For Production**: Depends on target audience
**For Premium Users**: Yes, great feature
**For Demo**: No, previews are fine

---

**Bottom Line**: The 30-second preview limitation is a Spotify policy. Full songs require Spotify Premium + Web Playback SDK integration, which is doable but requires OAuth and changes to your authentication flow.

Would you like me to implement full Spotify playback with OAuth? It'll take about 30-45 minutes to set up.
