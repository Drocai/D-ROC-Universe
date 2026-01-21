/**
 * GROUP GROOVE - CLOUDFLARE WORKERS BACKEND v3.0
 * Complete API with auth, rooms, voting, friends, DMs, groups, freemium
 * 
 * Deploy: wrangler deploy
 * Database: Cloudflare D1
 */

// ============================================
// CONFIGURATION & CONSTANTS
// ============================================
const JWT_SECRET = 'group-groove-jwt-secret-change-in-production';
const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

const TIER_LIMITS = {
  free: {
    requestsPerDay: 5,
    maxRoomSize: 8,
    canCreateGroups: false,
    canDirectMessage: true,
    maxFriends: 20,
    priorityVoting: false,
    skipVoteWeight: 1,
  },
  premium: {
    requestsPerDay: 50,
    maxRoomSize: 50,
    canCreateGroups: true,
    canDirectMessage: true,
    maxFriends: 200,
    priorityVoting: true,
    skipVoteWeight: 2,
  },
  dj_pro: {
    requestsPerDay: -1, // Unlimited
    maxRoomSize: 200,
    canCreateGroups: true,
    canDirectMessage: true,
    maxFriends: -1,
    priorityVoting: true,
    skipVoteWeight: 3,
    djControls: true,
    analytics: true,
  },
  venue: {
    requestsPerDay: -1,
    maxRoomSize: 500,
    canCreateGroups: true,
    canDirectMessage: true,
    maxFriends: -1,
    priorityVoting: true,
    skipVoteWeight: 5,
    djControls: true,
    analytics: true,
    multiRoom: true,
    branding: true,
  }
};

// ============================================
// UTILITY FUNCTIONS
// ============================================
function generateId() {
  return crypto.randomUUID().replace(/-/g, '').slice(0, 16);
}

function generateRoomCode() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  let code = '';
  for (let i = 0; i < 6; i++) {
    code += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return code;
}

function generateGroupInvite() {
  return 'GRP' + generateId().slice(0, 8).toUpperCase();
}

async function hashPassword(password) {
  const encoder = new TextEncoder();
  const data = encoder.encode(password + JWT_SECRET);
  const hash = await crypto.subtle.digest('SHA-256', data);
  return btoa(String.fromCharCode(...new Uint8Array(hash)));
}

async function createJWT(payload) {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const body = btoa(JSON.stringify({ ...payload, exp: Date.now() + 7 * 24 * 60 * 60 * 1000 }));
  const signature = await hashPassword(header + '.' + body);
  return `${header}.${body}.${signature}`;
}

async function verifyJWT(token) {
  try {
    const [header, body, signature] = token.split('.');
    const expectedSig = await hashPassword(header + '.' + body);
    if (signature !== expectedSig) return null;
    const payload = JSON.parse(atob(body));
    if (payload.exp < Date.now()) return null;
    return payload;
  } catch { return null; }
}

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json', ...CORS_HEADERS }
  });
}

function errorResponse(message, status = 400) {
  return jsonResponse({ error: message }, status);
}

async function authenticate(request, env) {
  const authHeader = request.headers.get('Authorization');
  if (!authHeader?.startsWith('Bearer ')) return null;
  
  const payload = await verifyJWT(authHeader.slice(7));
  if (!payload) return null;
  
  const user = await env.DB.prepare('SELECT * FROM users WHERE id = ?').bind(payload.userId).first();
  if (user) {
    await env.DB.prepare('UPDATE users SET last_seen_at = ? WHERE id = ?')
      .bind(new Date().toISOString(), user.id).run();
  }
  return user;
}

// ============================================
// DATABASE SCHEMA
// ============================================
const SCHEMA = `
-- Users table
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  name TEXT NOT NULL,
  avatar_url TEXT,
  tier TEXT DEFAULT 'free',
  stripe_customer_id TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  last_seen_at TEXT DEFAULT CURRENT_TIMESTAMP,
  settings TEXT DEFAULT '{}'
);

-- Rooms table
CREATE TABLE IF NOT EXISTS rooms (
  id TEXT PRIMARY KEY,
  code TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  host_id TEXT NOT NULL,
  is_active INTEGER DEFAULT 1,
  settings TEXT DEFAULT '{}',
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (host_id) REFERENCES users(id)
);

-- Room members
CREATE TABLE IF NOT EXISTS room_members (
  room_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
  is_dj INTEGER DEFAULT 0,
  PRIMARY KEY (room_id, user_id),
  FOREIGN KEY (room_id) REFERENCES rooms(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Queue items
CREATE TABLE IF NOT EXISTS queue_items (
  id TEXT PRIMARY KEY,
  room_id TEXT NOT NULL,
  added_by TEXT NOT NULL,
  spotify_id TEXT,
  title TEXT NOT NULL,
  artist TEXT NOT NULL,
  album TEXT,
  artwork_url TEXT,
  preview_url TEXT,
  duration_ms INTEGER,
  position INTEGER,
  played_at TEXT,
  skip_votes INTEGER DEFAULT 0,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (room_id) REFERENCES rooms(id),
  FOREIGN KEY (added_by) REFERENCES users(id)
);

-- Votes
CREATE TABLE IF NOT EXISTS votes (
  id TEXT PRIMARY KEY,
  queue_item_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  vote_type TEXT NOT NULL,
  weight INTEGER DEFAULT 1,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(queue_item_id, user_id),
  FOREIGN KEY (queue_item_id) REFERENCES queue_items(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Skip votes
CREATE TABLE IF NOT EXISTS skip_votes (
  room_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  queue_item_id TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (room_id, user_id, queue_item_id),
  FOREIGN KEY (room_id) REFERENCES rooms(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Messages
CREATE TABLE IF NOT EXISTS messages (
  id TEXT PRIMARY KEY,
  room_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (room_id) REFERENCES rooms(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Friends
CREATE TABLE IF NOT EXISTS friends (
  user_id TEXT NOT NULL,
  friend_id TEXT NOT NULL,
  status TEXT DEFAULT 'pending',
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, friend_id),
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (friend_id) REFERENCES users(id)
);

-- Direct messages
CREATE TABLE IF NOT EXISTS direct_messages (
  id TEXT PRIMARY KEY,
  from_user TEXT NOT NULL,
  to_user TEXT NOT NULL,
  content TEXT NOT NULL,
  read_at TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (from_user) REFERENCES users(id),
  FOREIGN KEY (to_user) REFERENCES users(id)
);

-- Groups (async playlists)
CREATE TABLE IF NOT EXISTS groups (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  created_by TEXT NOT NULL,
  invite_code TEXT UNIQUE NOT NULL,
  is_private INTEGER DEFAULT 0,
  artwork_url TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Group members
CREATE TABLE IF NOT EXISTS group_members (
  group_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  role TEXT DEFAULT 'member',
  joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (group_id, user_id),
  FOREIGN KEY (group_id) REFERENCES groups(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Group songs
CREATE TABLE IF NOT EXISTS group_songs (
  id TEXT PRIMARY KEY,
  group_id TEXT NOT NULL,
  added_by TEXT NOT NULL,
  spotify_id TEXT,
  title TEXT NOT NULL,
  artist TEXT NOT NULL,
  album TEXT,
  artwork_url TEXT,
  duration_ms INTEGER,
  votes INTEGER DEFAULT 0,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (group_id) REFERENCES groups(id),
  FOREIGN KEY (added_by) REFERENCES users(id)
);

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  type TEXT NOT NULL,
  title TEXT NOT NULL,
  body TEXT,
  data TEXT,
  read_at TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Usage tracking
CREATE TABLE IF NOT EXISTS usage_tracking (
  user_id TEXT NOT NULL,
  date TEXT NOT NULL,
  song_requests INTEGER DEFAULT 0,
  votes_cast INTEGER DEFAULT 0,
  rooms_created INTEGER DEFAULT 0,
  PRIMARY KEY (user_id, date),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Tips
CREATE TABLE IF NOT EXISTS tips (
  id TEXT PRIMARY KEY,
  from_user TEXT NOT NULL,
  to_user TEXT NOT NULL,
  room_id TEXT,
  queue_item_id TEXT,
  amount_cents INTEGER NOT NULL,
  stripe_payment_id TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (from_user) REFERENCES users(id),
  FOREIGN KEY (to_user) REFERENCES users(id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_rooms_code ON rooms(code);
CREATE INDEX IF NOT EXISTS idx_rooms_host ON rooms(host_id);
CREATE INDEX IF NOT EXISTS idx_queue_room ON queue_items(room_id);
CREATE INDEX IF NOT EXISTS idx_votes_item ON votes(queue_item_id);
CREATE INDEX IF NOT EXISTS idx_messages_room ON messages(room_id);
CREATE INDEX IF NOT EXISTS idx_friends_user ON friends(user_id);
CREATE INDEX IF NOT EXISTS idx_dm_users ON direct_messages(from_user, to_user);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
`;

// ============================================
// AUTH HANDLERS
// ============================================
async function handleSignup(request, env) {
  try {
    const { email, username, password, name } = await request.json();
    
    if (!email || !username || !password || !name) {
      return errorResponse('All fields required');
    }
    
    if (password.length < 6) {
      return errorResponse('Password must be at least 6 characters');
    }
    
    const existing = await env.DB.prepare(
      'SELECT id FROM users WHERE email = ? OR username = ?'
    ).bind(email.toLowerCase(), username.toLowerCase()).first();
    
    if (existing) {
      return errorResponse('Email or username already exists');
    }
    
    const id = generateId();
    const passwordHash = await hashPassword(password);
    
    await env.DB.prepare(`
      INSERT INTO users (id, email, username, password_hash, name)
      VALUES (?, ?, ?, ?, ?)
    `).bind(id, email.toLowerCase(), username.toLowerCase(), passwordHash, name).run();
    
    const token = await createJWT({ userId: id });
    
    return jsonResponse({
      user: { id, email: email.toLowerCase(), username: username.toLowerCase(), name, tier: 'free' },
      token
    }, 201);
  } catch (error) {
    return errorResponse('Signup failed: ' + error.message, 500);
  }
}

async function handleSignin(request, env) {
  try {
    const { email, password } = await request.json();
    
    if (!email || !password) {
      return errorResponse('Email and password required');
    }
    
    const user = await env.DB.prepare(
      'SELECT * FROM users WHERE email = ? OR username = ?'
    ).bind(email.toLowerCase(), email.toLowerCase()).first();
    
    if (!user) {
      return errorResponse('Invalid credentials', 401);
    }
    
    const passwordHash = await hashPassword(password);
    if (user.password_hash !== passwordHash) {
      return errorResponse('Invalid credentials', 401);
    }
    
    const token = await createJWT({ userId: user.id });
    
    return jsonResponse({
      user: {
        id: user.id,
        email: user.email,
        username: user.username,
        name: user.name,
        tier: user.tier,
        avatarUrl: user.avatar_url
      },
      token
    });
  } catch (error) {
    return errorResponse('Signin failed: ' + error.message, 500);
  }
}

async function handleGetProfile(request, env) {
  const user = await authenticate(request, env);
  if (!user) return errorResponse('Unauthorized', 401);
  
  const limits = TIER_LIMITS[user.tier] || TIER_LIMITS.free;
  const today = new Date().toISOString().split('T')[0];
  
  const usage = await env.DB.prepare(
    'SELECT * FROM usage_tracking WHERE user_id = ? AND date = ?'
  ).bind(user.id, today).first();
  
  return jsonResponse({
    user: {
      id: user.id,
      email: user.email,
      username: user.username,
      name: user.name,
      tier: user.tier,
      avatarUrl: user.avatar_url,
      createdAt: user.created_at
    },
    limits,
    usage: usage || { song_requests: 0, votes_cast: 0, rooms_created: 0 }
  });
}

async function handleUpdateProfile(request, env) {
  const user = await authenticate(request, env);
  if (!user) return errorResponse('Unauthorized', 401);
  
  const { name, avatarUrl } = await request.json();
  
  await env.DB.prepare(
    'UPDATE users SET name = COALESCE(?, name), avatar_url = COALESCE(?, avatar_url) WHERE id = ?'
  ).bind(name, avatarUrl, user.id).run();
  
  return jsonResponse({ success: true });
}

// ============================================
// ROOM HANDLERS
// ============================================
async function handleCreateRoom(request, env) {
  const user = await authenticate(request, env);
  if (!user) return errorResponse('Unauthorized', 401);
  
  const { name } = await request.json();
  if (!name?.trim()) return errorResponse('Room name required');
  
  const id = generateId();
  const code = generateRoomCode();
  
  await env.DB.prepare(`
    INSERT INTO rooms (id, code, name, host_id)
    VALUES (?, ?, ?, ?)
  `).bind(id, code, name.trim(), user.id).run();
  
  await env.DB.prepare(`
    INSERT INTO room_members (room_id, user_id, is_dj)
    VALUES (?, ?, 1)
  `).bind(id, user.id).run();
  
  // Track usage
  const today = new Date().toISOString().split('T')[0];
  await env.DB.prepare(`
    INSERT INTO usage_tracking (user_id, date, rooms_created)
    VALUES (?, ?, 1)
    ON CONFLICT(user_id, date) DO UPDATE SET rooms_created = rooms_created + 1
  `).bind(user.id, today).run();
  
  return jsonResponse({ room: { id, code, name: name.trim(), hostId: user.id } }, 201);
}

async function handleJoinRoom(request, env) {
  const user = await authenticate(request, env);
  if (!user) return errorResponse('Unauthorized', 401);
  
  const { code } = await request.json();
  if (!code?.trim()) return errorResponse('Room code required');
  
  const room = await env.DB.prepare(
    'SELECT * FROM rooms WHERE code = ? AND is_active = 1'
  ).bind(code.toUpperCase().trim()).first();
  
  if (!room) return errorResponse('Room not found', 404);
  
  // Check room size limits
  const limits = TIER_LIMITS[user.tier] || TIER_LIMITS.free;
  const memberCount = await env.DB.prepare(
    'SELECT COUNT(*) as count FROM room_members WHERE room_id = ?'
  ).bind(room.id).first();
  
  if (memberCount.count >= limits.maxRoomSize) {
    return errorResponse(`Room is full (max ${limits.maxRoomSize} for your tier)`, 403);
  }
  
  await env.DB.prepare(`
    INSERT OR IGNORE INTO room_members (room_id, user_id)
    VALUES (?, ?)
  `).bind(room.id, user.id).run();
  
  return jsonResponse({ room: { id: room.id, code: room.code, name: room.name, hostId: room.host_id } });
}

async function handleGetRoom(request, env, roomId) {
  const user = await authenticate(request, env);
  if (!user) return errorResponse('Unauthorized', 401);
  
  const room = await env.DB.prepare(
    'SELECT * FROM rooms WHERE id = ? OR code = ?'
  ).bind(roomId, roomId.toUpperCase()).first();
  
  if (!room) return errorResponse('Room not found', 404);
  
  // Get members
  const members = await env.DB.prepare(`
    SELECT u.id, u.name, u.username, u.avatar_url, rm.is_dj, rm.joined_at
    FROM room_members rm
    JOIN users u ON rm.user_id = u.id
    WHERE rm.room_id = ?
    ORDER BY rm.joined_at
  `).bind(room.id).all();
  
  // Get queue with votes
  const queue = await env.DB.prepare(`
    SELECT 
      qi.*,
      u.name as added_by_name,
      COALESCE(SUM(CASE WHEN v.vote_type = 'up' THEN v.weight ELSE 0 END), 0) -
      COALESCE(SUM(CASE WHEN v.vote_type = 'down' THEN v.weight ELSE 0 END), 0) as vote_score,
      (SELECT vote_type FROM votes WHERE queue_item_id = qi.id AND user_id = ?) as user_vote
    FROM queue_items qi
    LEFT JOIN votes v ON qi.id = v.queue_item_id
    LEFT JOIN users u ON qi.added_by = u.id
    WHERE qi.room_id = ? AND qi.played_at IS NULL
    GROUP BY qi.id
    ORDER BY vote_score DESC, qi.created_at ASC
  `).bind(user.id, room.id).all();
  
  // Get now playing
  const nowPlaying = await env.DB.prepare(`
    SELECT qi.*, u.name as added_by_name
    FROM queue_items qi
    LEFT JOIN users u ON qi.added_by = u.id
    WHERE qi.room_id = ? AND qi.played_at IS NOT NULL
    ORDER BY qi.played_at DESC
    LIMIT 1
  `).bind(room.id).first();
  
  // Get skip vote count for current song
  let skipVoteCount = 0;
  if (nowPlaying) {
    const skipVotes = await env.DB.prepare(
      'SELECT COUNT(*) as count FROM skip_votes WHERE room_id = ? AND queue_item_id = ?'
    ).bind(room.id, nowPlaying.id).first();
    skipVoteCount = skipVotes?.count || 0;
  }
  
  // Get recent messages
  const messages = await env.DB.prepare(`
    SELECT m.*, u.name as user_name, u.avatar_url
    FROM messages m
    JOIN users u ON m.user_id = u.id
    WHERE m.room_id = ?
    ORDER BY m.created_at DESC
    LIMIT 50
  `).bind(room.id).all();
  
  return jsonResponse({
    room: {
      id: room.id,
      code: room.code,
      name: room.name,
      hostId: room.host_id,
      isActive: room.is_active,
      settings: JSON.parse(room.settings || '{}')
    },
    members: members.results || [],
    queue: queue.results || [],
    nowPlaying,
    skipVoteCount,
    skipThreshold: Math.ceil((members.results?.length || 1) * 0.5),
    messages: (messages.results || []).reverse(),
    isHost: room.host_id === user.id
  });
}

async function handleLeaveRoom(request, env, roomId) {
  const user = await authenticate(request, env);
  if (!user) return errorResponse('Unauthorized', 401);
  
  await env.DB.prepare(
    'DELETE FROM room_members WHERE room_id = ? AND user_id = ?'
  ).bind(roomId, user.id).run();
  
  // If host leaves, close room
  const room = await env.DB.prepare('SELECT * FROM rooms WHERE id = ?').bind(roomId).first();
  if (room?.host_id === user.id) {
    await env.DB.prepare('UPDATE rooms SET is_active = 0 WHERE id = ?').bind(roomId).run();
  }
  
  return jsonResponse({ success: true });
}

// ============================================
// QUEUE HANDLERS
// ============================================
async function handleAddToQueue(request, env, roomId) {
  const user = await authenticate(request, env);
  if (!user) return errorResponse('Unauthorized', 401);
  
  // Check daily limit
  const limits = TIER_LIMITS[user.tier] || TIER_LIMITS.free;
  const today = new Date().toISOString().split('T')[0];
  
  if (limits.requestsPerDay !== -1) {
    const usage = await env.DB.prepare(
      'SELECT song_requests FROM usage_tracking WHERE user_id = ? AND date = ?'
    ).bind(user.id, today).first();
    
    if (usage && usage.song_requests >= limits.requestsPerDay) {
      return errorResponse(`Daily limit reached (${limits.requestsPerDay} songs). Upgrade for more!`, 403);
    }
  }
  
  const { spotifyId, title, artist, album, artworkUrl, durationMs, previewUrl } = await request.json();

  if (!title || !artist) {
    return errorResponse('Title and artist required');
  }

  const room = await env.DB.prepare('SELECT * FROM rooms WHERE id = ? AND is_active = 1').bind(roomId).first();
  if (!room) return errorResponse('Room not found', 404);

  const id = generateId();

  // Insert with preview_url
  await env.DB.prepare(`
    INSERT INTO queue_items (id, room_id, added_by, spotify_id, title, artist, album, artwork_url, preview_url, duration_ms)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).bind(id, roomId, user.id, spotifyId, title, artist, album, artworkUrl, previewUrl, durationMs).run();
  
  // Track usage
  await env.DB.prepare(`
    INSERT INTO usage_tracking (user_id, date, song_requests)
    VALUES (?, ?, 1)
    ON CONFLICT(user_id, date) DO UPDATE SET song_requests = song_requests + 1
  `).bind(user.id, today).run();
  
  return jsonResponse({
    queueItem: { id, roomId, title, artist, album, artworkUrl, durationMs, spotifyId, addedBy: user.id }
  }, 201);
}

async function handleVote(request, env, roomId) {
  const user = await authenticate(request, env);
  if (!user) return errorResponse('Unauthorized', 401);

  const { queueItemId, voteType } = await request.json();

  if (!queueItemId || !['up', 'down'].includes(voteType)) {
    return errorResponse('Invalid vote');
  }

  const limits = TIER_LIMITS[user.tier] || TIER_LIMITS.free;
  const weight = limits.priorityVoting ? limits.skipVoteWeight : 1;

  // Remove existing vote
  await env.DB.prepare(
    'DELETE FROM votes WHERE queue_item_id = ? AND user_id = ?'
  ).bind(queueItemId, user.id).run();

  // Add new vote
  const id = generateId();
  await env.DB.prepare(`
    INSERT INTO votes (id, queue_item_id, user_id, vote_type, weight)
    VALUES (?, ?, ?, ?, ?)
  `).bind(id, queueItemId, user.id, voteType, weight).run();

  // Get updated vote counts and check for skip
  const voteStats = await env.DB.prepare(`
    SELECT
      COALESCE(SUM(CASE WHEN vote_type = 'up' THEN weight ELSE 0 END), 0) as upVotes,
      COALESCE(SUM(CASE WHEN vote_type = 'down' THEN weight ELSE 0 END), 0) as downVotes
    FROM votes WHERE queue_item_id = ?
  `).bind(queueItemId).first();

  const upVotes = voteStats?.upVotes || 0;
  const downVotes = voteStats?.downVotes || 0;
  const score = upVotes - downVotes;

  // Auto-skip if down votes > up votes
  let skipped = false;
  if (downVotes > upVotes && downVotes > 0) {
    await env.DB.prepare(
      'UPDATE queue_items SET played_at = ? WHERE id = ?'
    ).bind(new Date().toISOString(), queueItemId).run();

    // Clear votes for this item
    await env.DB.prepare(
      'DELETE FROM votes WHERE queue_item_id = ?'
    ).bind(queueItemId).run();

    skipped = true;
  }

  return jsonResponse({ voteScore: score, upVotes, downVotes, skipped });
}

async function handleSkipVote(request, env, roomId) {
  const user = await authenticate(request, env);
  if (!user) return errorResponse('Unauthorized', 401);
  
  const { queueItemId } = await request.json();
  
  // Add skip vote
  await env.DB.prepare(`
    INSERT OR IGNORE INTO skip_votes (room_id, user_id, queue_item_id)
    VALUES (?, ?, ?)
  `).bind(roomId, user.id, queueItemId).run();
  
  // Check if threshold met
  const memberCount = await env.DB.prepare(
    'SELECT COUNT(*) as count FROM room_members WHERE room_id = ?'
  ).bind(roomId).first();
  
  const skipCount = await env.DB.prepare(
    'SELECT COUNT(*) as count FROM skip_votes WHERE room_id = ? AND queue_item_id = ?'
  ).bind(roomId, queueItemId).first();
  
  const threshold = Math.ceil((memberCount?.count || 1) * 0.5);
  const shouldSkip = (skipCount?.count || 0) >= threshold;
  
  if (shouldSkip) {
    // Mark song as played (skipped)
    await env.DB.prepare(
      'UPDATE queue_items SET played_at = ? WHERE id = ?'
    ).bind(new Date().toISOString(), queueItemId).run();
    
    // Clear skip votes
    await env.DB.prepare(
      'DELETE FROM skip_votes WHERE room_id = ? AND queue_item_id = ?'
    ).bind(roomId, queueItemId).run();
  }
  
  return jsonResponse({
    skipCount: skipCount?.count || 0,
    threshold,
    skipped: shouldSkip
  });
}

async function handlePlayNext(request, env, roomId) {
  const user = await authenticate(request, env);
  if (!user) return errorResponse('Unauthorized', 401);
  
  // Only host can do this
  const room = await env.DB.prepare('SELECT * FROM rooms WHERE id = ?').bind(roomId).first();
  if (room?.host_id !== user.id) {
    return errorResponse('Only host can control playback', 403);
  }
  
  // Get next song (highest voted)
  const next = await env.DB.prepare(`
    SELECT qi.*,
      COALESCE(SUM(CASE WHEN v.vote_type = 'up' THEN v.weight ELSE 0 END), 0) -
      COALESCE(SUM(CASE WHEN v.vote_type = 'down' THEN v.weight ELSE 0 END), 0) as vote_score
    FROM queue_items qi
    LEFT JOIN votes v ON qi.id = v.queue_item_id
    WHERE qi.room_id = ? AND qi.played_at IS NULL
    GROUP BY qi.id
    ORDER BY vote_score DESC, qi.created_at ASC
    LIMIT 1
  `).bind(roomId).first();
  
  if (!next) {
    return jsonResponse({ nowPlaying: null, message: 'Queue is empty' });
  }
  
  // Mark as playing
  await env.DB.prepare(
    'UPDATE queue_items SET played_at = ? WHERE id = ?'
  ).bind(new Date().toISOString(), next.id).run();
  
  // Clear skip votes
  await env.DB.prepare('DELETE FROM skip_votes WHERE room_id = ?').bind(roomId).run();
  
  return jsonResponse({ nowPlaying: next });
}

// ============================================
// CHAT HANDLERS
// ============================================
async function handleSendMessage(request, env, roomId) {
  const user = await authenticate(request, env);
  if (!user) return errorResponse('Unauthorized', 401);
  
  const { content } = await request.json();
  if (!content?.trim()) return errorResponse('Message content required');
  
  const id = generateId();
  
  await env.DB.prepare(`
    INSERT INTO messages (id, room_id, user_id, content)
    VALUES (?, ?, ?, ?)
  `).bind(id, roomId, user.id, content.trim().slice(0, 500)).run();
  
  return jsonResponse({
    message: {
      id,
      roomId,
      userId: user.id,
      userName: user.name,
      content: content.trim().slice(0, 500),
      createdAt: new Date().toISOString()
    }
  }, 201);
}

// ============================================
// FRIENDS HANDLERS
// ============================================
async function handleGetFriends(request, env) {
  const user = await authenticate(request, env);
  if (!user) return errorResponse('Unauthorized', 401);
  
  const friends = await env.DB.prepare(`
    SELECT u.id, u.name, u.username, u.avatar_url, u.last_seen_at, f.status, f.created_at
    FROM friends f
    JOIN users u ON (
      CASE WHEN f.user_id = ? THEN f.friend_id ELSE f.user_id END
    ) = u.id
    WHERE (f.user_id = ? OR f.friend_id = ?) AND f.status = 'accepted'
  `).bind(user.id, user.id, user.id).all();
  
  const pending = await env.DB.prepare(`
    SELECT u.id, u.name, u.username, u.avatar_url, f.created_at
    FROM friends f
    JOIN users u ON f.user_id = u.id
    WHERE f.friend_id = ? AND f.status = 'pending'
  `).bind(user.id).all();
  
  return jsonResponse({
    friends: friends.results || [],
    pendingRequests: pending.results || []
  });
}

async function handleSendFriendRequest(request, env) {
  const user = await authenticate(request, env);
  if (!user) return errorResponse('Unauthorized', 401);
  
  const { username } = await request.json();
  if (!username?.trim()) return errorResponse('Username required');
  
  const friend = await env.DB.prepare(
    'SELECT * FROM users WHERE username = ?'
  ).bind(username.toLowerCase().trim()).first();
  
  if (!friend) return errorResponse('User not found', 404);
  if (friend.id === user.id) return errorResponse('Cannot add yourself');
  
  // Check limit
  const limits = TIER_LIMITS[user.tier] || TIER_LIMITS.free;
  if (limits.maxFriends !== -1) {
    const friendCount = await env.DB.prepare(
      'SELECT COUNT(*) as count FROM friends WHERE (user_id = ? OR friend_id = ?) AND status = ?'
    ).bind(user.id, user.id, 'accepted').first();
    
    if (friendCount?.count >= limits.maxFriends) {
      return errorResponse(`Friend limit reached (${limits.maxFriends}). Upgrade for more!`, 403);
    }
  }
  
  await env.DB.prepare(`
    INSERT OR REPLACE INTO friends (user_id, friend_id, status)
    VALUES (?, ?, 'pending')
  `).bind(user.id, friend.id).run();
  
  // Create notification
  const notifId = generateId();
  await env.DB.prepare(`
    INSERT INTO notifications (id, user_id, type, title, body, data)
    VALUES (?, ?, 'friend_request', 'Friend Request', ?, ?)
  `).bind(notifId, friend.id, `${user.name} sent you a friend request`, JSON.stringify({ fromUserId: user.id })).run();
  
  return jsonResponse({ success: true }, 201);
}

async function handleRespondFriendRequest(request, env) {
  const user = await authenticate(request, env);
  if (!user) return errorResponse('Unauthorized', 401);
  
  const { friendId, accept } = await request.json();
  
  if (accept) {
    await env.DB.prepare(
      'UPDATE friends SET status = ? WHERE user_id = ? AND friend_id = ?'
    ).bind('accepted', friendId, user.id).run();
  } else {
    await env.DB.prepare(
      'DELETE FROM friends WHERE user_id = ? AND friend_id = ?'
    ).bind(friendId, user.id).run();
  }
  
  return jsonResponse({ success: true });
}

// ============================================
// DIRECT MESSAGE HANDLERS
// ============================================
async function handleSendDM(request, env) {
  const user = await authenticate(request, env);
  if (!user) return errorResponse('Unauthorized', 401);
  
  const { toUserId, content } = await request.json();
  if (!toUserId || !content?.trim()) return errorResponse('Recipient and content required');
  
  const id = generateId();
  
  await env.DB.prepare(`
    INSERT INTO direct_messages (id, from_user, to_user, content)
    VALUES (?, ?, ?, ?)
  `).bind(id, user.id, toUserId, content.trim().slice(0, 1000)).run();
  
  // Create notification
  const notifId = generateId();
  await env.DB.prepare(`
    INSERT INTO notifications (id, user_id, type, title, body, data)
    VALUES (?, ?, 'dm', 'New Message', ?, ?)
  `).bind(notifId, toUserId, `${user.name}: ${content.slice(0, 50)}...`, JSON.stringify({ fromUserId: user.id })).run();
  
  return jsonResponse({
    message: { id, fromUser: user.id, toUser: toUserId, content: content.trim(), createdAt: new Date().toISOString() }
  }, 201);
}

async function handleGetDMs(request, env, friendId) {
  const user = await authenticate(request, env);
  if (!user) return errorResponse('Unauthorized', 401);
  
  const messages = await env.DB.prepare(`
    SELECT dm.*, fu.name as from_name, tu.name as to_name
    FROM direct_messages dm
    JOIN users fu ON dm.from_user = fu.id
    JOIN users tu ON dm.to_user = tu.id
    WHERE (dm.from_user = ? AND dm.to_user = ?) OR (dm.from_user = ? AND dm.to_user = ?)
    ORDER BY dm.created_at ASC
    LIMIT 100
  `).bind(user.id, friendId, friendId, user.id).all();
  
  // Mark as read
  await env.DB.prepare(
    'UPDATE direct_messages SET read_at = ? WHERE to_user = ? AND from_user = ? AND read_at IS NULL'
  ).bind(new Date().toISOString(), user.id, friendId).run();
  
  return jsonResponse({ messages: messages.results || [] });
}

async function handleGetConversations(request, env) {
  const user = await authenticate(request, env);
  if (!user) return errorResponse('Unauthorized', 401);
  
  const conversations = await env.DB.prepare(`
    SELECT 
      CASE WHEN dm.from_user = ? THEN dm.to_user ELSE dm.from_user END as friend_id,
      u.name as friend_name,
      u.username as friend_username,
      u.avatar_url as friend_avatar,
      dm.content as last_message,
      dm.created_at as last_message_at,
      (SELECT COUNT(*) FROM direct_messages WHERE to_user = ? AND from_user = u.id AND read_at IS NULL) as unread_count
    FROM direct_messages dm
    JOIN users u ON (CASE WHEN dm.from_user = ? THEN dm.to_user ELSE dm.from_user END) = u.id
    WHERE dm.from_user = ? OR dm.to_user = ?
    GROUP BY friend_id
    ORDER BY dm.created_at DESC
  `).bind(user.id, user.id, user.id, user.id, user.id).all();
  
  return jsonResponse({ conversations: conversations.results || [] });
}

// ============================================
// GROUP HANDLERS
// ============================================
async function handleCreateGroup(request, env) {
  const user = await authenticate(request, env);
  if (!user) return errorResponse('Unauthorized', 401);
  
  const limits = TIER_LIMITS[user.tier] || TIER_LIMITS.free;
  if (!limits.canCreateGroups) {
    return errorResponse('Upgrade to Premium to create groups', 403);
  }
  
  const { name, description, isPrivate } = await request.json();
  if (!name?.trim()) return errorResponse('Group name required');
  
  const id = generateId();
  const inviteCode = generateGroupInvite();
  
  await env.DB.prepare(`
    INSERT INTO groups (id, name, description, created_by, invite_code, is_private)
    VALUES (?, ?, ?, ?, ?, ?)
  `).bind(id, name.trim(), description?.trim(), user.id, inviteCode, isPrivate ? 1 : 0).run();
  
  await env.DB.prepare(`
    INSERT INTO group_members (group_id, user_id, role)
    VALUES (?, ?, 'admin')
  `).bind(id, user.id).run();
  
  return jsonResponse({
    group: { id, name: name.trim(), description, inviteCode, isPrivate, createdBy: user.id }
  }, 201);
}

async function handleJoinGroup(request, env) {
  const user = await authenticate(request, env);
  if (!user) return errorResponse('Unauthorized', 401);
  
  const { inviteCode } = await request.json();
  
  const group = await env.DB.prepare(
    'SELECT * FROM groups WHERE invite_code = ?'
  ).bind(inviteCode?.toUpperCase()).first();
  
  if (!group) return errorResponse('Invalid invite code', 404);
  
  await env.DB.prepare(`
    INSERT OR IGNORE INTO group_members (group_id, user_id)
    VALUES (?, ?)
  `).bind(group.id, user.id).run();
  
  return jsonResponse({ group });
}

async function handleGetGroups(request, env) {
  const user = await authenticate(request, env);
  if (!user) return errorResponse('Unauthorized', 401);
  
  const groups = await env.DB.prepare(`
    SELECT g.*, gm.role,
      (SELECT COUNT(*) FROM group_members WHERE group_id = g.id) as member_count,
      (SELECT COUNT(*) FROM group_songs WHERE group_id = g.id) as song_count
    FROM groups g
    JOIN group_members gm ON g.id = gm.group_id
    WHERE gm.user_id = ?
    ORDER BY g.created_at DESC
  `).bind(user.id).all();
  
  return jsonResponse({ groups: groups.results || [] });
}

// ============================================
// SPOTIFY HANDLERS
// ============================================
async function handleSpotifySearch(request, env) {
  const user = await authenticate(request, env);
  if (!user) return errorResponse('Unauthorized', 401);
  
  const url = new URL(request.url);
  const query = url.searchParams.get('q');
  
  if (!query?.trim()) return errorResponse('Search query required');
  
  // Get Spotify token (you'd cache this in KV in production)
  const tokenResponse = await fetch('https://accounts.spotify.com/api/token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Authorization': 'Basic ' + btoa(`${env.SPOTIFY_CLIENT_ID}:${env.SPOTIFY_CLIENT_SECRET}`)
    },
    body: 'grant_type=client_credentials'
  });
  
  if (!tokenResponse.ok) {
    return errorResponse('Failed to authenticate with Spotify', 500);
  }
  
  const { access_token } = await tokenResponse.json();
  
  // Search Spotify
  const searchResponse = await fetch(
    `https://api.spotify.com/v1/search?q=${encodeURIComponent(query)}&type=track&limit=20`,
    { headers: { 'Authorization': `Bearer ${access_token}` } }
  );
  
  if (!searchResponse.ok) {
    return errorResponse('Spotify search failed', 500);
  }
  
  const data = await searchResponse.json();
  
  const tracks = data.tracks?.items?.map(track => ({
    spotifyId: track.id,
    title: track.name,
    artist: track.artists.map(a => a.name).join(', '),
    album: track.album.name,
    artworkUrl: track.album.images[0]?.url,
    durationMs: track.duration_ms,
    previewUrl: track.preview_url,
    uri: track.uri
  })) || [];
  
  return jsonResponse({ tracks });
}

// ============================================
// NOTIFICATION HANDLERS
// ============================================
async function handleGetNotifications(request, env) {
  const user = await authenticate(request, env);
  if (!user) return errorResponse('Unauthorized', 401);
  
  const notifications = await env.DB.prepare(`
    SELECT * FROM notifications
    WHERE user_id = ?
    ORDER BY created_at DESC
    LIMIT 50
  `).bind(user.id).all();
  
  return jsonResponse({ notifications: notifications.results || [] });
}

async function handleMarkNotificationsRead(request, env) {
  const user = await authenticate(request, env);
  if (!user) return errorResponse('Unauthorized', 401);
  
  await env.DB.prepare(
    'UPDATE notifications SET read_at = ? WHERE user_id = ? AND read_at IS NULL'
  ).bind(new Date().toISOString(), user.id).run();
  
  return jsonResponse({ success: true });
}

// ============================================
// MAIN ROUTER
// ============================================
export default {
  async fetch(request, env, ctx) {
    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS_HEADERS });
    }
    
    const url = new URL(request.url);
    const path = url.pathname;
    const method = request.method;
    
    try {
      // Database migration endpoint
      if (path === '/api/migrate' && method === 'POST') {
        const statements = SCHEMA.split(';').filter(s => s.trim());
        for (const statement of statements) {
          if (statement.trim()) {
            await env.DB.prepare(statement).run();
          }
        }
        return jsonResponse({ success: true, message: 'Migration complete' });
      }
      
      // Health check
      if (path === '/api/health') {
        return jsonResponse({ 
          status: 'ok', 
          version: '3.0.0', 
          timestamp: new Date().toISOString(),
          features: ['auth', 'rooms', 'voting', 'friends', 'dms', 'groups', 'spotify']
        });
      }
      
      // AUTH
      if (path === '/api/auth/signup' && method === 'POST') return handleSignup(request, env);
      if (path === '/api/auth/signin' && method === 'POST') return handleSignin(request, env);
      if (path === '/api/auth/profile' && method === 'GET') return handleGetProfile(request, env);
      if (path === '/api/auth/profile' && method === 'PUT') return handleUpdateProfile(request, env);
      
      // ROOMS
      if (path === '/api/rooms' && method === 'POST') return handleCreateRoom(request, env);
      if (path === '/api/rooms/join' && method === 'POST') return handleJoinRoom(request, env);
      
      const roomMatch = path.match(/^\/api\/rooms\/([^/]+)$/);
      if (roomMatch) {
        if (method === 'GET') return handleGetRoom(request, env, roomMatch[1]);
        if (method === 'DELETE') return handleLeaveRoom(request, env, roomMatch[1]);
      }
      
      // QUEUE
      const queueMatch = path.match(/^\/api\/rooms\/([^/]+)\/queue$/);
      if (queueMatch && method === 'POST') return handleAddToQueue(request, env, queueMatch[1]);
      
      const voteMatch = path.match(/^\/api\/rooms\/([^/]+)\/vote$/);
      if (voteMatch && method === 'POST') return handleVote(request, env, voteMatch[1]);
      
      const skipMatch = path.match(/^\/api\/rooms\/([^/]+)\/skip$/);
      if (skipMatch && method === 'POST') return handleSkipVote(request, env, skipMatch[1]);
      
      const playNextMatch = path.match(/^\/api\/rooms\/([^/]+)\/play-next$/);
      if (playNextMatch && method === 'POST') return handlePlayNext(request, env, playNextMatch[1]);
      
      // CHAT
      const chatMatch = path.match(/^\/api\/rooms\/([^/]+)\/messages$/);
      if (chatMatch && method === 'POST') return handleSendMessage(request, env, chatMatch[1]);
      
      // FRIENDS
      if (path === '/api/friends' && method === 'GET') return handleGetFriends(request, env);
      if (path === '/api/friends/request' && method === 'POST') return handleSendFriendRequest(request, env);
      if (path === '/api/friends/respond' && method === 'POST') return handleRespondFriendRequest(request, env);
      
      // DMs
      if (path === '/api/messages' && method === 'POST') return handleSendDM(request, env);
      if (path === '/api/messages/conversations' && method === 'GET') return handleGetConversations(request, env);
      
      const dmMatch = path.match(/^\/api\/messages\/([^/]+)$/);
      if (dmMatch && method === 'GET') return handleGetDMs(request, env, dmMatch[1]);
      
      // GROUPS
      if (path === '/api/groups' && method === 'GET') return handleGetGroups(request, env);
      if (path === '/api/groups' && method === 'POST') return handleCreateGroup(request, env);
      if (path === '/api/groups/join' && method === 'POST') return handleJoinGroup(request, env);
      
      // SPOTIFY
      if (path === '/api/spotify/search' && method === 'GET') return handleSpotifySearch(request, env);
      
      // NOTIFICATIONS
      if (path === '/api/notifications' && method === 'GET') return handleGetNotifications(request, env);
      if (path === '/api/notifications/read' && method === 'POST') return handleMarkNotificationsRead(request, env);
      
      return errorResponse('Not found', 404);
      
    } catch (error) {
      console.error('Error:', error);
      return errorResponse('Internal server error: ' + error.message, 500);
    }
  }
};
