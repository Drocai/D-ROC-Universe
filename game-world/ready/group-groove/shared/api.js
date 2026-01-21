/**
 * GROUP GROOVE - SHARED API SERVICE
 * Works with both React Native and Web
 * 
 * Usage:
 *   import { createAPI } from './api';
 *   const api = createAPI('https://your-worker.workers.dev');
 *   const { user, token } = await api.auth.signup({ email, username, password, name });
 */

class GroupGrooveAPI {
  constructor(baseUrl) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.token = null;
    this.user = null;
    this.listeners = new Map();
    this.pollingInterval = null;
  }

  // ============================================
  // CORE HTTP METHODS
  // ============================================
  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        body: options.body ? JSON.stringify(options.body) : undefined,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new APIError(data.error || 'Request failed', response.status, data);
      }

      return data;
    } catch (error) {
      if (error instanceof APIError) throw error;
      throw new APIError(error.message || 'Network error', 0, null);
    }
  }

  get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }

  post(endpoint, body) {
    return this.request(endpoint, { method: 'POST', body });
  }

  put(endpoint, body) {
    return this.request(endpoint, { method: 'PUT', body });
  }

  delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }

  // ============================================
  // AUTH
  // ============================================
  auth = {
    signup: async ({ email, username, password, name }) => {
      const data = await this.post('/api/auth/signup', { email, username, password, name });
      this.token = data.token;
      this.user = data.user;
      this._saveAuth();
      return data;
    },

    signin: async ({ email, password }) => {
      const data = await this.post('/api/auth/signin', { email, password });
      this.token = data.token;
      this.user = data.user;
      this._saveAuth();
      return data;
    },

    signout: () => {
      this.token = null;
      this.user = null;
      this._clearAuth();
      this.stopPolling();
    },

    getProfile: async () => {
      const data = await this.get('/api/auth/profile');
      this.user = data.user;
      return data;
    },

    updateProfile: async ({ name, avatarUrl }) => {
      return this.put('/api/auth/profile', { name, avatarUrl });
    },

    isAuthenticated: () => !!this.token,

    getUser: () => this.user,

    getToken: () => this.token,

    restoreSession: async () => {
      const saved = this._loadAuth();
      if (saved?.token) {
        this.token = saved.token;
        try {
          const data = await this.auth.getProfile();
          return { authenticated: true, user: data.user };
        } catch {
          this.auth.signout();
          return { authenticated: false };
        }
      }
      return { authenticated: false };
    }
  };

  // ============================================
  // ROOMS
  // ============================================
  rooms = {
    create: async (name) => {
      return this.post('/api/rooms', { name });
    },

    join: async (code) => {
      return this.post('/api/rooms/join', { code });
    },

    get: async (roomId) => {
      return this.get(`/api/rooms/${roomId}`);
    },

    leave: async (roomId) => {
      return this.delete(`/api/rooms/${roomId}`);
    },

    addToQueue: async (roomId, song) => {
      return this.post(`/api/rooms/${roomId}/queue`, song);
    },

    vote: async (roomId, queueItemId, voteType) => {
      return this.post(`/api/rooms/${roomId}/vote`, { queueItemId, voteType });
    },

    skipVote: async (roomId, queueItemId) => {
      return this.post(`/api/rooms/${roomId}/skip`, { queueItemId });
    },

    playNext: async (roomId) => {
      return this.post(`/api/rooms/${roomId}/play-next`, {});
    },

    sendMessage: async (roomId, content) => {
      return this.post(`/api/rooms/${roomId}/messages`, { content });
    }
  };

  // ============================================
  // FRIENDS
  // ============================================
  friends = {
    list: async () => {
      return this.get('/api/friends');
    },

    sendRequest: async (username) => {
      return this.post('/api/friends/request', { username });
    },

    respond: async (friendId, accept) => {
      return this.post('/api/friends/respond', { friendId, accept });
    }
  };

  // ============================================
  // DIRECT MESSAGES
  // ============================================
  messages = {
    getConversations: async () => {
      return this.get('/api/messages/conversations');
    },

    getMessages: async (friendId) => {
      return this.get(`/api/messages/${friendId}`);
    },

    send: async (toUserId, content) => {
      return this.post('/api/messages', { toUserId, content });
    }
  };

  // ============================================
  // GROUPS
  // ============================================
  groups = {
    list: async () => {
      return this.get('/api/groups');
    },

    create: async ({ name, description, isPrivate }) => {
      return this.post('/api/groups', { name, description, isPrivate });
    },

    join: async (inviteCode) => {
      return this.post('/api/groups/join', { inviteCode });
    }
  };

  // ============================================
  // SPOTIFY
  // ============================================
  spotify = {
    search: async (query) => {
      return this.get(`/api/spotify/search?q=${encodeURIComponent(query)}`);
    }
  };

  // ============================================
  // NOTIFICATIONS
  // ============================================
  notifications = {
    list: async () => {
      return this.get('/api/notifications');
    },

    markRead: async () => {
      return this.post('/api/notifications/read', {});
    }
  };

  // ============================================
  // REAL-TIME POLLING
  // ============================================
  startPolling(roomId, callback, intervalMs = 3000) {
    this.stopPolling();
    
    const poll = async () => {
      try {
        const data = await this.rooms.get(roomId);
        callback(null, data);
      } catch (error) {
        callback(error, null);
      }
    };

    poll(); // Initial fetch
    this.pollingInterval = setInterval(poll, intervalMs);
  }

  stopPolling() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
  }

  // ============================================
  // EVENT EMITTER
  // ============================================
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
    return () => this.off(event, callback);
  }

  off(event, callback) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      const index = callbacks.indexOf(callback);
      if (index > -1) callbacks.splice(index, 1);
    }
  }

  emit(event, data) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach(cb => cb(data));
    }
  }

  // ============================================
  // STORAGE (Platform-agnostic)
  // ============================================
  _getStorage() {
    // React Native
    if (typeof global !== 'undefined' && global.AsyncStorage) {
      return global.AsyncStorage;
    }
    // Web
    if (typeof localStorage !== 'undefined') {
      return {
        getItem: (key) => Promise.resolve(localStorage.getItem(key)),
        setItem: (key, value) => Promise.resolve(localStorage.setItem(key, value)),
        removeItem: (key) => Promise.resolve(localStorage.removeItem(key)),
      };
    }
    // Fallback (in-memory)
    const memory = {};
    return {
      getItem: (key) => Promise.resolve(memory[key] || null),
      setItem: (key, value) => { memory[key] = value; return Promise.resolve(); },
      removeItem: (key) => { delete memory[key]; return Promise.resolve(); },
    };
  }

  _saveAuth() {
    const storage = this._getStorage();
    storage.setItem('groupgroove_auth', JSON.stringify({ token: this.token, user: this.user }));
  }

  _loadAuth() {
    const storage = this._getStorage();
    try {
      const saved = storage.getItem('groupgroove_auth');
      if (typeof saved === 'string') {
        return JSON.parse(saved);
      }
      // Handle async storage
      if (saved && typeof saved.then === 'function') {
        return null; // Will be handled by restoreSession
      }
    } catch {
      return null;
    }
    return null;
  }

  _clearAuth() {
    const storage = this._getStorage();
    storage.removeItem('groupgroove_auth');
  }
}

// Custom error class
class APIError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.data = data;
  }
}

// Factory function
export function createAPI(baseUrl) {
  return new GroupGrooveAPI(baseUrl);
}

// Default export for convenience
export default GroupGrooveAPI;

// Also export the error class
export { APIError };
