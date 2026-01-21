# FREQUENCY FACTORY - FIRESTORE DATABASE SCHEMA
## Complete Data Structure Design

**Last Updated:** October 24, 2025  
**Status:** Production-Ready Architecture

---

## 🗄️ COLLECTIONS OVERVIEW

```
frequency-factory/
├── users/                    # User profiles & stats
├── tracks/                   # Submitted music tracks
├── ratings/                  # Individual track ratings
├── sessions/                 # Active rating sessions
├── leaderboards/            # Rankings & top performers
├── transactions/            # Token economy transactions
├── achievements/            # Unlockable badges & milestones
├── notifications/           # User notifications
├── otto-logs/              # OTTO automation activity
└── platform-config/        # System settings
```

---

## 📊 DETAILED COLLECTION SCHEMAS

### **1. USERS COLLECTION**
**Path:** `/users/{userId}`

```javascript
{
  // Identity
  userId: "string",              // Firebase Auth UID
  username: "string",            // Display name (unique)
  email: "string",               // User email
  avatar: "url",                 // Profile image
  
  // Stats
  tokens: 0,                     // Current token balance
  totalTokensEarned: 0,         // Lifetime tokens earned
  totalTokensSpent: 0,          // Lifetime tokens spent
  
  // Activity
  tracksRated: 0,               // Total tracks rated
  ratingsGiven: 0,              // Total ratings submitted
  streak: 0,                     // Current daily streak
  longestStreak: 0,             // Best streak achieved
  lastActive: timestamp,         // Last activity timestamp
  lastLogin: timestamp,          // Last login
  
  // Reputation
  reputation: 0,                 // Reputation score (0-100)
  level: 1,                      // User level (1-50)
  rank: "Novice",               // Rank title
  badges: [],                    // Array of badge IDs
  
  // Preferences
  genres: [],                    // Preferred genres
  notifications: {
    email: true,
    push: true,
    newTracks: true,
    achievements: true
  },
  
  // Timestamps
  createdAt: timestamp,
  updatedAt: timestamp,
  
  // Role
  role: "user",                  // user | artist | moderator | admin
  verified: false                // Artist verification status
}
```

---

### **2. TRACKS COLLECTION**
**Path:** `/tracks/{trackId}`

```javascript
{
  // Identity
  trackId: "string",             // Auto-generated ID
  title: "string",               // Track title
  artist: "string",              // Artist name
  artistId: "string",            // User ID of submitter
  
  // Media
  audioUrl: "url",               // Streaming URL
  coverArt: "url",               // Album art URL
  duration: 180,                 // Length in seconds
  
  // Metadata
  genre: "string",               // Primary genre
  subgenres: [],                 // Additional genres
  bpm: 120,                      // Beats per minute
  key: "A minor",                // Musical key
  
  // Status
  status: "pending",             // pending | active | certified | archived
  submissionDate: timestamp,
  activationDate: timestamp,
  
  // Ratings
  averageRating: 0,              // 0-100 scale
  totalRatings: 0,               // Count of ratings
  ratingDistribution: {          // Rating breakdown
    "0-20": 0,
    "21-40": 0,
    "41-60": 0,
    "61-80": 0,
    "81-100": 0
  },
  
  // Engagement
  plays: 0,                      // Play count
  shares: 0,                     // Share count
  likes: 0,                      // Like count
  comments: 0,                   // Comment count
  
  // Certification
  certified: false,              // 90+ rating
  certifiedAt: timestamp,
  certificationLevel: "",        // bronze | silver | gold | platinum
  
  // Platform Integration
  spotifyUrl: "url",
  appleMusicUrl: "url",
  soundcloudUrl: "url",
  
  // Submission Details
  submissionCost: 100,           // Tokens paid
  featured: false,               // Featured track flag
  
  // Timestamps
  createdAt: timestamp,
  updatedAt: timestamp
}
```

---

### **3. RATINGS COLLECTION**
**Path:** `/ratings/{ratingId}`

```javascript
{
  // Identity
  ratingId: "string",            // Auto-generated ID
  trackId: "string",             // Track being rated
  userId: "string",              // User who rated
  
  // Rating Data
  score: 0,                      // 0-100 rating
  categories: {                  // Detailed breakdown
    production: 0,               // 0-10
    vocals: 0,                   // 0-10
    melody: 0,                   // 0-10
    lyrics: 0,                   // 0-10
    originality: 0,              // 0-10
    vibe: 0,                     // 0-10
    replay: 0,                   // 0-10
    commercial: 0,               // 0-10
    artistic: 0,                 // 0-10
    overall: 0                   // 0-10
  },
  
  // Feedback
  comment: "string",             // Optional text feedback
  tags: [],                      // Keywords (fire, mid, skip)
  
  // Validation
  listenTime: 0,                 // Seconds listened before rating
  completed: false,              // Did they finish the track?
  
  // Tokens
  tokensEarned: 10,              // Tokens received for rating
  bonusMultiplier: 1.0,          // Any bonus applied
  
  // Context
  sessionId: "string",           // Rating session ID
  device: "web",                 // web | ios | android
  
  // Timestamps
  createdAt: timestamp
}
```

---

### **4. SESSIONS COLLECTION**
**Path:** `/sessions/{sessionId}`

```javascript
{
  // Identity
  sessionId: "string",           // Auto-generated ID
  userId: "string",              // User in session
  
  // Session Data
  tracksRated: 0,                // Tracks rated in session
  tokensEarned: 0,               // Tokens earned in session
  duration: 0,                   // Session length (seconds)
  
  // Activity
  startTime: timestamp,
  endTime: timestamp,
  lastActivity: timestamp,
  
  // Status
  active: true,                  // Is session ongoing?
  completed: false               // Did user finish properly?
}
```

---

### **5. LEADERBOARDS COLLECTION**
**Path:** `/leaderboards/{period}`

```javascript
{
  // Identity
  period: "string",              // daily | weekly | monthly | alltime
  
  // Rankings
  rankings: [
    {
      userId: "string",
      username: "string",
      avatar: "url",
      score: 0,                  // Points for this period
      rank: 1,
      change: 0,                 // Position change
      tracksRated: 0,
      tokensEarned: 0
    }
  ],
  
  // Metadata
  startDate: timestamp,
  endDate: timestamp,
  totalParticipants: 0,
  
  // Timestamps
  lastUpdated: timestamp
}
```

---

### **6. TRANSACTIONS COLLECTION**
**Path:** `/transactions/{transactionId}`

```javascript
{
  // Identity
  transactionId: "string",       // Auto-generated ID
  userId: "string",              // User involved
  
  // Transaction Details
  type: "string",                // earned | spent | bonus | penalty
  amount: 0,                     // Token amount (positive or negative)
  balance: 0,                    // Balance after transaction
  
  // Source
  source: "string",              // rating | submission | achievement | purchase
  sourceId: "string",            // ID of related entity
  
  // Description
  description: "string",         // Human-readable description
  metadata: {},                  // Additional context
  
  // Timestamps
  createdAt: timestamp
}
```

---

### **7. ACHIEVEMENTS COLLECTION**
**Path:** `/achievements/{achievementId}`

```javascript
{
  // Identity
  achievementId: "string",       // Unique achievement ID
  
  // Details
  title: "string",               // Achievement name
  description: "string",         // What it's for
  category: "string",            // rating | submission | social | special
  
  // Requirements
  requirement: {
    type: "count",               // count | streak | score
    target: 100,                 // Target number
    metric: "tracksRated"        // What to measure
  },
  
  // Rewards
  tokenReward: 0,                // Tokens awarded
  badgeUrl: "url",               // Badge image
  
  // Rarity
  rarity: "common",              // common | rare | epic | legendary
  
  // Stats
  unlockedBy: 0,                 // How many users have this
  
  // Status
  active: true
}
```

---

### **8. NOTIFICATIONS COLLECTION**
**Path:** `/users/{userId}/notifications/{notificationId}`

```javascript
{
  // Identity
  notificationId: "string",
  
  // Content
  type: "string",                // achievement | track | rating | system
  title: "string",
  message: "string",
  icon: "url",
  
  // Action
  actionUrl: "string",           // Where to go when clicked
  actionLabel: "string",         // Button text
  
  // Status
  read: false,
  dismissed: false,
  
  // Timestamps
  createdAt: timestamp,
  readAt: timestamp
}
```

---

### **9. OTTO-LOGS COLLECTION**
**Path:** `/otto-logs/{logId}`

```javascript
{
  // Identity
  logId: "string",
  
  // Agent
  agent: "Galaxy Girl",          // Which OTTO personality
  action: "string",              // Action taken
  
  // Content
  contentType: "string",         // announcement | video | social | email
  contentId: "string",           // ID of generated content
  platform: "string",            // Where it was posted
  
  // Results
  success: true,
  response: {},                  // API response
  
  // Timestamps
  createdAt: timestamp
}
```

---

### **10. PLATFORM-CONFIG COLLECTION**
**Path:** `/platform-config/settings`

```javascript
{
  // Token Economy
  tokenSettings: {
    ratingReward: 10,            // Base tokens per rating
    submissionCost: 100,         // Cost to submit track
    bonusMultipliers: {
      streak3: 1.2,
      streak7: 1.5,
      streak30: 2.0
    }
  },
  
  // Thresholds
  certificationThreshold: 90,    // Rating needed for certification
  minRatingsForCert: 50,        // Minimum ratings before certification
  
  // Features
  featuresEnabled: {
    comments: true,
    sharing: true,
    achievements: true,
    leaderboards: true
  },
  
  // Active Track Queue
  activeTrackCount: 0,           // Current tracks in rotation
  maxActiveTrackCount: 100,      // Maximum in queue
  
  // Timestamps
  lastUpdated: timestamp
}
```

---

## 🔐 SECURITY RULES STRUCTURE

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Users can read their own data
    match /users/{userId} {
      allow read: if request.auth != null;
      allow write: if request.auth.uid == userId;
    }
    
    // Tracks are publicly readable
    match /tracks/{trackId} {
      allow read: if true;
      allow create: if request.auth != null;
      allow update, delete: if request.auth.uid == resource.data.artistId;
    }
    
    // Ratings require authentication
    match /ratings/{ratingId} {
      allow read: if true;
      allow create: if request.auth != null 
                    && request.auth.uid == request.resource.data.userId;
      allow update, delete: if request.auth.uid == resource.data.userId;
    }
    
    // Leaderboards are public
    match /leaderboards/{period} {
      allow read: if true;
      allow write: if false; // Only backend can write
    }
    
    // Transactions are read-only for users
    match /transactions/{transactionId} {
      allow read: if request.auth.uid == resource.data.userId;
      allow write: if false; // Only backend can write
    }
  }
}
```

---

## 📈 INDEXES REQUIRED

```javascript
// Composite indexes for common queries

// Get user's recent ratings
ratings: [userId (ASC), createdAt (DESC)]

// Get track's ratings sorted by score
ratings: [trackId (ASC), score (DESC)]

// Get active tracks by rating
tracks: [status (ASC), averageRating (DESC)]

// Get certified tracks
tracks: [certified (ASC), certifiedAt (DESC)]

// Get leaderboard by score
leaderboards.rankings: [score (DESC)]

// Get user's transactions
transactions: [userId (ASC), createdAt (DESC)]
```

---

## 🔄 REALTIME LISTENERS

**What to listen to in real-time:**
- Current track queue (for live updates)
- User's token balance (for instant feedback)
- Leaderboard rankings (for live competition)
- Notifications (for instant alerts)
- Active session stats (for progress tracking)

---

## 💾 BACKUP STRATEGY

**Automated Backups:**
- Daily: All collections
- Weekly: Full database export
- Monthly: Long-term archive

**Critical Data:**
- User profiles
- Transaction history
- Rating history
- Certification records

---

**SCHEMA COMPLETE & PRODUCTION-READY** ✅

**Next: OTTO Integration Framework**
