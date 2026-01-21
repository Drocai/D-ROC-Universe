/**
 * GROUP GROOVE - REACT NATIVE APP (Complete)
 * Main entry point with navigation and global state
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { NavigationContainer, DefaultTheme } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import {
  SafeAreaView, View, Text, TextInput, TouchableOpacity, StyleSheet,
  ActivityIndicator, Alert, ScrollView, FlatList, RefreshControl,
  KeyboardAvoidingView, Platform, Share, Clipboard, StatusBar,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

// ============================================
// CONFIGURATION
// ============================================
const API_URL = 'http://172.20.10.2:8787'; // Local development - replace with production URL when deploying
const POLL_INTERVAL = 3000;

// ============================================
// API SERVICE (Inline for simplicity)
// ============================================
class GroupGrooveAPI {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
    this.token = null;
  }

  async request(endpoint, options = {}) {
    const headers = { 'Content-Type': 'application/json', ...options.headers };
    if (this.token) headers['Authorization'] = `Bearer ${this.token}`;

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Request failed');
    return data;
  }

  get = (endpoint) => this.request(endpoint, { method: 'GET' });
  post = (endpoint, body) => this.request(endpoint, { method: 'POST', body });
  put = (endpoint, body) => this.request(endpoint, { method: 'PUT', body });
  delete = (endpoint) => this.request(endpoint, { method: 'DELETE' });
}

const api = new GroupGrooveAPI(API_URL);

// ============================================
// THEME
// ============================================
const theme = {
  colors: {
    primary: '#8A2BE2',
    secondary: '#FFD700',
    background: '#1a1a1a',
    card: '#2a2a2a',
    text: '#ffffff',
    textSecondary: '#888888',
    border: '#333333',
    success: '#4CAF50',
    error: '#FF4444',
  },
};

const navTheme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: theme.colors.primary,
    background: theme.colors.background,
    card: theme.colors.card,
    text: theme.colors.text,
    border: theme.colors.border,
  },
};

// ============================================
// CONTEXT
// ============================================
const AppContext = createContext(null);
const useApp = () => useContext(AppContext);

function AppProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const saved = await AsyncStorage.getItem('groupgroove_auth');
        if (saved) {
          const { token } = JSON.parse(saved);
          api.token = token;
          const data = await api.get('/api/auth/profile');
          setUser(data.user);
        }
      } catch (e) {
        console.log('Session restore failed');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const signin = async (email, password) => {
    const data = await api.post('/api/auth/signin', { email, password });
    api.token = data.token;
    await AsyncStorage.setItem('groupgroove_auth', JSON.stringify({ token: data.token }));
    setUser(data.user);
    return data;
  };

  const signup = async (email, username, password, name) => {
    const data = await api.post('/api/auth/signup', { email, username, password, name });
    api.token = data.token;
    await AsyncStorage.setItem('groupgroove_auth', JSON.stringify({ token: data.token }));
    setUser(data.user);
    return data;
  };

  const signout = async () => {
    api.token = null;
    await AsyncStorage.removeItem('groupgroove_auth');
    setUser(null);
  };

  return (
    <AppContext.Provider value={{ user, loading, signin, signup, signout }}>
      {children}
    </AppContext.Provider>
  );
}

// ============================================
// COMPONENTS
// ============================================
const Button = ({ title, onPress, loading, variant = 'primary', style, disabled }) => (
  <TouchableOpacity
    style={[
      styles.button,
      variant === 'secondary' && styles.buttonSecondary,
      disabled && styles.buttonDisabled,
      style,
    ]}
    onPress={onPress}
    disabled={loading || disabled}
  >
    {loading ? (
      <ActivityIndicator color="#fff" />
    ) : (
      <Text style={styles.buttonText}>{title}</Text>
    )}
  </TouchableOpacity>
);

const Input = ({ style, ...props }) => (
  <TextInput
    style={[styles.input, style]}
    placeholderTextColor={theme.colors.textSecondary}
    {...props}
  />
);

const Card = ({ children, style }) => (
  <View style={[styles.card, style]}>{children}</View>
);

const NowPlayingCard = ({ song, skipVoteCount, skipThreshold, onSkipVote, isHost, onPlayNext }) => {
  if (!song) {
    return (
      <Card style={styles.nowPlayingCard}>
        <Text style={styles.nowPlayingLabel}>NOW PLAYING</Text>
        <Text style={styles.nowPlayingTitle}>No song playing</Text>
        {isHost && <Button title="▶️ Play Next" onPress={onPlayNext} style={{ marginTop: 12 }} />}
      </Card>
    );
  }

  const skipProgress = skipThreshold > 0 ? (skipVoteCount / skipThreshold) * 100 : 0;

  return (
    <Card style={styles.nowPlayingCard}>
      <Text style={styles.nowPlayingLabel}>NOW PLAYING</Text>
      <Text style={styles.nowPlayingTitle}>{song.title}</Text>
      <Text style={styles.nowPlayingArtist}>{song.artist}</Text>
      
      <View style={styles.skipSection}>
        <TouchableOpacity style={styles.skipButton} onPress={onSkipVote}>
          <Text style={styles.skipButtonText}>⏭️ Vote Skip ({skipVoteCount}/{skipThreshold})</Text>
        </TouchableOpacity>
        <View style={styles.skipProgressBar}>
          <View style={[styles.skipProgress, { width: `${Math.min(skipProgress, 100)}%` }]} />
        </View>
      </View>
      
      {isHost && (
        <View style={styles.hostControls}>
          <Button title="⏭️ Skip" onPress={onPlayNext} style={{ flex: 1, marginRight: 8 }} />
          <Button title="▶️ Next" onPress={onPlayNext} style={{ flex: 1 }} />
        </View>
      )}
    </Card>
  );
};

const QueueItem = ({ song, position, onVote, userVote }) => {
  const voteScore = song.vote_score || 0;
  
  return (
    <View style={styles.queueItem}>
      <Text style={styles.queuePosition}>#{position}</Text>
      
      <View style={styles.queueInfo}>
        <Text style={styles.queueTitle} numberOfLines={1}>{song.title}</Text>
        <Text style={styles.queueArtist} numberOfLines={1}>{song.artist}</Text>
        <Text style={styles.addedBy}>Added by {song.added_by_name}</Text>
      </View>
      
      <View style={styles.voteControls}>
        <TouchableOpacity
          style={[styles.voteBtn, userVote === 'up' && styles.voteBtnActive]}
          onPress={() => onVote('up')}
        >
          <Text style={styles.voteIcon}>👍</Text>
        </TouchableOpacity>
        
        <Text style={styles.voteScore}>{voteScore}</Text>
        
        <TouchableOpacity
          style={[styles.voteBtn, userVote === 'down' && styles.voteBtnActive]}
          onPress={() => onVote('down')}
        >
          <Text style={styles.voteIcon}>👎</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const TierBadge = ({ tier }) => {
  const badges = {
    free: { emoji: '🆓', label: 'Free', color: '#888' },
    premium: { emoji: '⭐', label: 'Premium', color: '#FFD700' },
    dj_pro: { emoji: '🎧', label: 'DJ Pro', color: '#8A2BE2' },
    venue: { emoji: '🏢', label: 'Venue', color: '#FF6B6B' },
  };
  const badge = badges[tier] || badges.free;

  return (
    <View style={[styles.tierBadge, { borderColor: badge.color }]}>
      <Text style={styles.tierEmoji}>{badge.emoji}</Text>
      <Text style={[styles.tierLabel, { color: badge.color }]}>{badge.label}</Text>
    </View>
  );
};

// ============================================
// SCREENS
// ============================================
const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

// Welcome Screen
function WelcomeScreen({ navigation }) {
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      <View style={styles.welcomeContent}>
        <Text style={styles.logo}>🎵</Text>
        <Text style={styles.title}>Group Groove</Text>
        <Text style={styles.subtitle}>Making Music Great Again</Text>
        <Text style={styles.tagline}>Democracy • Discovery • Dollars</Text>
        
        <View style={styles.welcomeButtons}>
          <Button title="Sign In" onPress={() => navigation.navigate('SignIn')} />
          <Button title="Create Account" onPress={() => navigation.navigate('SignUp')} variant="secondary" style={{ marginTop: 12 }} />
        </View>
      </View>
    </SafeAreaView>
  );
}

// Sign In Screen
function SignInScreen({ navigation }) {
  const { signin } = useApp();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSignIn = async () => {
    if (!email || !password) return Alert.alert('Error', 'Please fill in all fields');
    setLoading(true);
    try {
      await signin(email, password);
    } catch (e) {
      Alert.alert('Error', e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.formContainer}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
        
        <Text style={styles.formTitle}>Welcome Back</Text>
        <Input placeholder="Email or Username" value={email} onChangeText={setEmail} autoCapitalize="none" keyboardType="email-address" />
        <Input placeholder="Password" value={password} onChangeText={setPassword} secureTextEntry />
        <Button title="Sign In" onPress={handleSignIn} loading={loading} />
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

// Sign Up Screen
function SignUpScreen({ navigation }) {
  const { signup } = useApp();
  const [name, setName] = useState('');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSignUp = async () => {
    if (!name || !username || !email || !password) return Alert.alert('Error', 'Please fill in all fields');
    setLoading(true);
    try {
      await signup(email, username, password, name);
    } catch (e) {
      Alert.alert('Error', e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.formContainer}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
        
        <Text style={styles.formTitle}>Create Account</Text>
        <Input placeholder="Your Name" value={name} onChangeText={setName} />
        <Input placeholder="Username" value={username} onChangeText={setUsername} autoCapitalize="none" />
        <Input placeholder="Email" value={email} onChangeText={setEmail} autoCapitalize="none" keyboardType="email-address" />
        <Input placeholder="Password (6+ characters)" value={password} onChangeText={setPassword} secureTextEntry />
        <Button title="Create Account" onPress={handleSignUp} loading={loading} />
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

// Home Screen
function HomeScreen({ navigation }) {
  const { user } = useApp();
  const [roomCode, setRoomCode] = useState('');
  const [loading, setLoading] = useState(false);

  const createRoom = async () => {
    setLoading(true);
    try {
      const { room } = await api.post('/api/rooms', { name: `${user.name}'s Room` });
      navigation.navigate('Room', { roomId: room.id, roomCode: room.code });
    } catch (e) {
      Alert.alert('Error', e.message);
    } finally {
      setLoading(false);
    }
  };

  const joinRoom = async () => {
    if (!roomCode.trim()) return Alert.alert('Error', 'Enter a room code');
    setLoading(true);
    try {
      const { room } = await api.post('/api/rooms/join', { code: roomCode.trim() });
      navigation.navigate('Room', { roomId: room.id, roomCode: room.code });
    } catch (e) {
      Alert.alert('Error', e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.homeContent}>
        <Text style={styles.greeting}>Hey, {user?.name}! 👋</Text>
        <TierBadge tier={user?.tier} />
        
        <Card style={styles.homeCard}>
          <Text style={styles.cardTitle}>🎉 Create a Room</Text>
          <Text style={styles.cardDesc}>Start a listening session and invite friends</Text>
          <Button title="Create Room" onPress={createRoom} loading={loading} />
        </Card>
        
        <Card style={styles.homeCard}>
          <Text style={styles.cardTitle}>🚀 Join a Room</Text>
          <Text style={styles.cardDesc}>Enter a room code to join the party</Text>
          <Input
            placeholder="Room Code (e.g., PARTY1)"
            value={roomCode}
            onChangeText={t => setRoomCode(t.toUpperCase())}
            autoCapitalize="characters"
            maxLength={6}
          />
          <Button title="Join Room" onPress={joinRoom} loading={loading} />
        </Card>

        {/* Premium Teaser */}
        <Card style={[styles.homeCard, styles.premiumCard]}>
          <Text style={styles.cardTitle}>⭐ Upgrade to Premium</Text>
          <Text style={styles.cardDesc}>• Unlimited song requests</Text>
          <Text style={styles.cardDesc}>• Priority voting</Text>
          <Text style={styles.cardDesc}>• Create groups</Text>
          <Text style={styles.cardDesc}>• Larger rooms (50 people)</Text>
          <Button title="🔒 Coming Soon" disabled variant="secondary" />
        </Card>
      </ScrollView>
    </SafeAreaView>
  );
}

// Room Screen
function RoomScreen({ route, navigation }) {
  const { roomId, roomCode } = route.params;
  const { user } = useApp();
  const [room, setRoom] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchRoom = useCallback(async () => {
    try {
      const data = await api.get(`/api/rooms/${roomId}`);
      setRoom(data);
    } catch (e) {
      Alert.alert('Error', e.message);
      navigation.goBack();
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [roomId]);

  useEffect(() => {
    fetchRoom();
    const interval = setInterval(fetchRoom, POLL_INTERVAL);
    return () => clearInterval(interval);
  }, [fetchRoom]);

  const handleVote = async (queueItemId, voteType) => {
    try {
      await api.post(`/api/rooms/${roomId}/vote`, { queueItemId, voteType });
      fetchRoom();
    } catch (e) {
      Alert.alert('Error', e.message);
    }
  };

  const handleSkipVote = async () => {
    if (!room?.nowPlaying) return;
    try {
      const result = await api.post(`/api/rooms/${roomId}/skip`, { queueItemId: room.nowPlaying.id });
      if (result.skipped) Alert.alert('Skipped!', 'Song skipped by popular vote');
      fetchRoom();
    } catch (e) {
      Alert.alert('Error', e.message);
    }
  };

  const handlePlayNext = async () => {
    try {
      await api.post(`/api/rooms/${roomId}/play-next`, {});
      fetchRoom();
    } catch (e) {
      Alert.alert('Error', e.message);
    }
  };

  const shareRoom = async () => {
    try {
      await Share.share({
        message: `Join my Group Groove room! Code: ${roomCode}\n\nDownload the app and enter code ${roomCode} to listen with me! 🎵`,
      });
    } catch (e) {
      // Copy to clipboard as fallback
      Clipboard.setString(roomCode);
      Alert.alert('Copied!', `Room code ${roomCode} copied to clipboard`);
    }
  };

  const leaveRoom = async () => {
    try {
      await api.delete(`/api/rooms/${roomId}`);
      navigation.goBack();
    } catch (e) {
      navigation.goBack();
    }
  };

  if (loading) {
    return (
      <SafeAreaView style={[styles.container, styles.centered]}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.roomHeader}>
        <TouchableOpacity onPress={leaveRoom}>
          <Text style={styles.backText}>← Leave</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={shareRoom} style={styles.roomCodeContainer}>
          <Text style={styles.roomCodeText}>{roomCode}</Text>
          <Text style={styles.memberCount}>👥 {room?.members?.length || 0}</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={() => navigation.navigate('Chat', { roomId })}>
          <Text style={{ fontSize: 24 }}>💬</Text>
        </TouchableOpacity>
      </View>

      {/* Now Playing */}
      <NowPlayingCard
        song={room?.nowPlaying}
        skipVoteCount={room?.skipVoteCount || 0}
        skipThreshold={room?.skipThreshold || 1}
        onSkipVote={handleSkipVote}
        isHost={room?.isHost}
        onPlayNext={handlePlayNext}
      />

      {/* Queue Header */}
      <View style={styles.queueHeader}>
        <Text style={styles.sectionTitle}>Up Next</Text>
        <TouchableOpacity
          style={styles.addSongBtn}
          onPress={() => navigation.navigate('Search', { roomId })}
        >
          <Text style={styles.addSongText}>+ Add Song</Text>
        </TouchableOpacity>
      </View>

      {/* Queue */}
      <FlatList
        data={room?.queue || []}
        keyExtractor={item => item.id}
        renderItem={({ item, index }) => (
          <QueueItem
            song={item}
            position={index + 1}
            onVote={type => handleVote(item.id, type)}
            userVote={item.user_vote}
          />
        )}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); fetchRoom(); }} />}
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Text style={styles.emptyText}>Queue is empty 🎵</Text>
            <Text style={styles.emptySubtext}>Tap "+ Add Song" to get started!</Text>
          </View>
        }
        contentContainerStyle={{ paddingBottom: 20 }}
      />
    </SafeAreaView>
  );
}

// Search Screen
function SearchScreen({ route, navigation }) {
  const { roomId } = route.params;
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const search = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const { tracks } = await api.get(`/api/spotify/search?q=${encodeURIComponent(query)}`);
      setResults(tracks || []);
    } catch (e) {
      Alert.alert('Error', e.message);
    } finally {
      setLoading(false);
    }
  };

  const addSong = async (track) => {
    try {
      await api.post(`/api/rooms/${roomId}/queue`, {
        spotifyId: track.spotifyId,
        title: track.title,
        artist: track.artist,
        album: track.album,
        artworkUrl: track.artworkUrl,
        durationMs: track.durationMs,
      });
      Alert.alert('Added!', `${track.title} added to queue`);
      navigation.goBack();
    } catch (e) {
      Alert.alert('Error', e.message);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.searchHeader}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.searchTitle}>Add Song</Text>
      </View>

      <View style={styles.searchBar}>
        <Input
          placeholder="Search songs..."
          value={query}
          onChangeText={setQuery}
          onSubmitEditing={search}
          returnKeyType="search"
          style={{ flex: 1 }}
        />
        <Button title="🔍" onPress={search} loading={loading} style={{ marginLeft: 8, paddingHorizontal: 16 }} />
      </View>

      <FlatList
        data={results}
        keyExtractor={item => item.spotifyId}
        renderItem={({ item }) => (
          <TouchableOpacity style={styles.searchResult} onPress={() => addSong(item)}>
            <View style={{ flex: 1 }}>
              <Text style={styles.searchResultTitle} numberOfLines={1}>{item.title}</Text>
              <Text style={styles.searchResultArtist} numberOfLines={1}>{item.artist}</Text>
            </View>
            <Text style={styles.addIcon}>+</Text>
          </TouchableOpacity>
        )}
        ListEmptyComponent={
          query ? null : (
            <View style={styles.emptyState}>
              <Text style={styles.emptyText}>Search for songs 🎵</Text>
            </View>
          )
        }
      />
    </SafeAreaView>
  );
}

// Chat Screen
function ChatScreen({ route, navigation }) {
  const { roomId } = route.params;
  const { user } = useApp();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchMessages = async () => {
      try {
        const data = await api.get(`/api/rooms/${roomId}`);
        setMessages(data.messages || []);
      } catch (e) {}
    };
    fetchMessages();
    const interval = setInterval(fetchMessages, 5000);
    return () => clearInterval(interval);
  }, [roomId]);

  const sendMessage = async () => {
    if (!newMessage.trim()) return;
    setLoading(true);
    try {
      await api.post(`/api/rooms/${roomId}/messages`, { content: newMessage });
      setNewMessage('');
    } catch (e) {
      Alert.alert('Error', e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.chatHeader}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.chatTitle}>Room Chat</Text>
      </View>

      <FlatList
        data={messages}
        keyExtractor={item => item.id}
        renderItem={({ item }) => (
          <View style={[styles.messageItem, item.user_id === user?.id && styles.ownMessage]}>
            <Text style={styles.messageSender}>{item.user_name}</Text>
            <Text style={styles.messageContent}>{item.content}</Text>
          </View>
        )}
        contentContainerStyle={{ padding: 16 }}
      />

      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <View style={styles.chatInputContainer}>
          <Input
            placeholder="Type a message..."
            value={newMessage}
            onChangeText={setNewMessage}
            style={{ flex: 1 }}
          />
          <Button title="Send" onPress={sendMessage} loading={loading} style={{ marginLeft: 8 }} />
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

// Friends Screen
function FriendsScreen() {
  const [friends, setFriends] = useState([]);
  const [pending, setPending] = useState([]);
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchFriends(); }, []);

  const fetchFriends = async () => {
    try {
      const data = await api.get('/api/friends');
      setFriends(data.friends || []);
      setPending(data.pendingRequests || []);
    } catch (e) {} finally { setLoading(false); }
  };

  const sendRequest = async () => {
    if (!username.trim()) return;
    try {
      await api.post('/api/friends/request', { username });
      Alert.alert('Sent!', 'Friend request sent');
      setUsername('');
    } catch (e) {
      Alert.alert('Error', e.message);
    }
  };

  const respond = async (friendId, accept) => {
    try {
      await api.post('/api/friends/respond', { friendId, accept });
      fetchFriends();
    } catch (e) {
      Alert.alert('Error', e.message);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        <Text style={styles.screenTitle}>Friends</Text>

        <Card>
          <Input placeholder="Add by username" value={username} onChangeText={setUsername} autoCapitalize="none" />
          <Button title="Send Request" onPress={sendRequest} />
        </Card>

        {pending.length > 0 && (
          <View style={{ marginTop: 20 }}>
            <Text style={styles.sectionTitle}>Pending Requests</Text>
            {pending.map(req => (
              <View key={req.id} style={styles.friendItem}>
                <Text style={styles.friendName}>{req.name}</Text>
                <View style={{ flexDirection: 'row' }}>
                  <Button title="✓" onPress={() => respond(req.id, true)} style={{ marginRight: 8, paddingHorizontal: 16 }} />
                  <Button title="✗" onPress={() => respond(req.id, false)} variant="secondary" style={{ paddingHorizontal: 16 }} />
                </View>
              </View>
            ))}
          </View>
        )}

        <Text style={[styles.sectionTitle, { marginTop: 20 }]}>Your Friends ({friends.length})</Text>
        {friends.length === 0 ? (
          <Text style={styles.emptySubtext}>No friends yet. Add some!</Text>
        ) : (
          friends.map(friend => (
            <View key={friend.id} style={styles.friendItem}>
              <View>
                <Text style={styles.friendName}>{friend.name}</Text>
                <Text style={styles.friendUsername}>@{friend.username}</Text>
              </View>
            </View>
          ))
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

// Groups Screen
function GroupsScreen() {
  const { user } = useApp();
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchGroups(); }, []);

  const fetchGroups = async () => {
    try {
      const data = await api.get('/api/groups');
      setGroups(data.groups || []);
    } catch (e) {} finally { setLoading(false); }
  };

  const isPremium = user?.tier !== 'free';

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        <Text style={styles.screenTitle}>Groups</Text>
        <Text style={styles.screenSubtitle}>Async playlists with friends</Text>

        {!isPremium ? (
          <Card style={styles.premiumCard}>
            <Text style={styles.cardTitle}>🔒 Premium Feature</Text>
            <Text style={styles.cardDesc}>Upgrade to create and join groups - collaborative playlists that sync across time zones!</Text>
            <Button title="Upgrade to Premium" disabled />
          </Card>
        ) : (
          <>
            <Button title="+ Create Group" onPress={() => Alert.alert('Coming Soon')} />
            {groups.map(group => (
              <Card key={group.id} style={{ marginTop: 12 }}>
                <Text style={styles.cardTitle}>{group.name}</Text>
                <Text style={styles.cardDesc}>{group.member_count} members • {group.song_count} songs</Text>
              </Card>
            ))}
          </>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

// Profile Screen
function ProfileScreen() {
  const { user, signout } = useApp();

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        <Text style={styles.screenTitle}>Profile</Text>
        
        <Card>
          <Text style={styles.profileName}>{user?.name}</Text>
          <Text style={styles.profileUsername}>@{user?.username}</Text>
          <Text style={styles.profileEmail}>{user?.email}</Text>
          <TierBadge tier={user?.tier} />
        </Card>

        <Card style={{ marginTop: 16 }}>
          <Text style={styles.cardTitle}>Daily Usage</Text>
          <Text style={styles.cardDesc}>
            {user?.tier === 'free' ? '5 song requests per day' : 'Unlimited requests'}
          </Text>
        </Card>

        <Button title="Sign Out" onPress={signout} variant="secondary" style={{ marginTop: 24 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

// ============================================
// NAVIGATION
// ============================================
function AuthStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Welcome" component={WelcomeScreen} />
      <Stack.Screen name="SignIn" component={SignInScreen} />
      <Stack.Screen name="SignUp" component={SignUpScreen} />
    </Stack.Navigator>
  );
}

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarStyle: { backgroundColor: theme.colors.card, borderTopColor: theme.colors.border },
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: theme.colors.textSecondary,
      }}
    >
      <Tab.Screen name="Home" component={HomeScreen} options={{ tabBarIcon: ({ color }) => <Text style={{ fontSize: 20, color }}>🏠</Text> }} />
      <Tab.Screen name="Friends" component={FriendsScreen} options={{ tabBarIcon: ({ color }) => <Text style={{ fontSize: 20, color }}>👥</Text> }} />
      <Tab.Screen name="Groups" component={GroupsScreen} options={{ tabBarIcon: ({ color }) => <Text style={{ fontSize: 20, color }}>🎵</Text> }} />
      <Tab.Screen name="Profile" component={ProfileScreen} options={{ tabBarIcon: ({ color }) => <Text style={{ fontSize: 20, color }}>👤</Text> }} />
    </Tab.Navigator>
  );
}

function MainStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="MainTabs" component={MainTabs} />
      <Stack.Screen name="Room" component={RoomScreen} />
      <Stack.Screen name="Search" component={SearchScreen} />
      <Stack.Screen name="Chat" component={ChatScreen} />
    </Stack.Navigator>
  );
}

// ============================================
// APP ROOT
// ============================================
export default function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}

function AppContent() {
  const { user, loading } = useApp();

  if (loading) {
    return (
      <SafeAreaView style={[styles.container, styles.centered]}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </SafeAreaView>
    );
  }

  return (
    <NavigationContainer theme={navTheme}>
      {user ? <MainStack /> : <AuthStack />}
    </NavigationContainer>
  );
}

// ============================================
// STYLES
// ============================================
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.colors.background },
  centered: { justifyContent: 'center', alignItems: 'center' },
  
  // Welcome
  welcomeContent: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24 },
  logo: { fontSize: 80, marginBottom: 16 },
  title: { fontSize: 36, fontWeight: 'bold', color: theme.colors.primary, marginBottom: 8 },
  subtitle: { fontSize: 18, color: theme.colors.textSecondary, marginBottom: 8 },
  tagline: { fontSize: 14, color: theme.colors.secondary, marginBottom: 48 },
  welcomeButtons: { width: '100%', maxWidth: 300 },
  
  // Forms
  formContainer: { flex: 1, padding: 24, justifyContent: 'center' },
  formTitle: { fontSize: 28, fontWeight: 'bold', color: theme.colors.text, marginBottom: 24, textAlign: 'center' },
  backBtn: { marginBottom: 24 },
  backText: { color: theme.colors.primary, fontSize: 18 },
  
  // Components
  button: { backgroundColor: theme.colors.primary, padding: 16, borderRadius: 12, alignItems: 'center', marginTop: 12 },
  buttonSecondary: { backgroundColor: 'transparent', borderWidth: 2, borderColor: theme.colors.primary },
  buttonDisabled: { opacity: 0.5 },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
  
  input: { backgroundColor: theme.colors.card, padding: 16, borderRadius: 12, color: theme.colors.text, fontSize: 16, marginBottom: 12, borderWidth: 1, borderColor: theme.colors.border },
  
  card: { backgroundColor: theme.colors.card, padding: 20, borderRadius: 16, marginBottom: 16 },
  cardTitle: { fontSize: 20, fontWeight: 'bold', color: theme.colors.text, marginBottom: 8 },
  cardDesc: { fontSize: 14, color: theme.colors.textSecondary, marginBottom: 4 },
  
  // Home
  homeContent: { padding: 16 },
  greeting: { fontSize: 28, fontWeight: 'bold', color: theme.colors.text, marginBottom: 16 },
  homeCard: { marginBottom: 16 },
  premiumCard: { borderWidth: 2, borderColor: theme.colors.secondary, borderStyle: 'dashed' },
  
  // Tier Badge
  tierBadge: { flexDirection: 'row', alignItems: 'center', alignSelf: 'flex-start', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20, borderWidth: 1, marginBottom: 16 },
  tierEmoji: { fontSize: 16, marginRight: 6 },
  tierLabel: { fontSize: 14, fontWeight: '600' },
  
  // Room
  roomHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, borderBottomWidth: 1, borderBottomColor: theme.colors.border },
  roomCodeContainer: { alignItems: 'center' },
  roomCodeText: { fontSize: 18, fontWeight: 'bold', color: theme.colors.primary },
  memberCount: { fontSize: 14, color: theme.colors.textSecondary },
  
  // Now Playing
  nowPlayingCard: { margin: 16, alignItems: 'center' },
  nowPlayingLabel: { fontSize: 12, color: theme.colors.primary, fontWeight: 'bold', marginBottom: 8 },
  nowPlayingTitle: { fontSize: 20, fontWeight: 'bold', color: theme.colors.text, textAlign: 'center' },
  nowPlayingArtist: { fontSize: 16, color: theme.colors.textSecondary, marginBottom: 16 },
  skipSection: { width: '100%', marginTop: 12 },
  skipButton: { backgroundColor: theme.colors.card, padding: 12, borderRadius: 8, alignItems: 'center' },
  skipButtonText: { color: theme.colors.text },
  skipProgressBar: { height: 4, backgroundColor: theme.colors.border, borderRadius: 2, marginTop: 8 },
  skipProgress: { height: '100%', backgroundColor: theme.colors.error, borderRadius: 2 },
  hostControls: { flexDirection: 'row', marginTop: 16 },
  
  // Queue
  queueHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: 16, marginBottom: 12 },
  sectionTitle: { fontSize: 18, fontWeight: 'bold', color: theme.colors.text },
  addSongBtn: { backgroundColor: theme.colors.primary, paddingHorizontal: 16, paddingVertical: 8, borderRadius: 20 },
  addSongText: { color: '#fff', fontWeight: 'bold' },
  
  queueItem: { flexDirection: 'row', alignItems: 'center', backgroundColor: theme.colors.card, marginHorizontal: 16, marginBottom: 8, padding: 12, borderRadius: 12 },
  queuePosition: { fontSize: 16, fontWeight: 'bold', color: theme.colors.primary, width: 32 },
  queueInfo: { flex: 1 },
  queueTitle: { fontSize: 16, fontWeight: '600', color: theme.colors.text },
  queueArtist: { fontSize: 14, color: theme.colors.textSecondary },
  addedBy: { fontSize: 12, color: theme.colors.textSecondary, marginTop: 2 },
  
  voteControls: { flexDirection: 'row', alignItems: 'center' },
  voteBtn: { width: 36, height: 36, borderRadius: 18, backgroundColor: theme.colors.background, justifyContent: 'center', alignItems: 'center' },
  voteBtnActive: { backgroundColor: theme.colors.primary },
  voteIcon: { fontSize: 16 },
  voteScore: { fontSize: 16, fontWeight: 'bold', color: theme.colors.text, marginHorizontal: 8, minWidth: 24, textAlign: 'center' },
  
  // Search
  searchHeader: { flexDirection: 'row', alignItems: 'center', padding: 16, borderBottomWidth: 1, borderBottomColor: theme.colors.border },
  searchTitle: { fontSize: 20, fontWeight: 'bold', color: theme.colors.text, marginLeft: 16 },
  searchBar: { flexDirection: 'row', padding: 16, alignItems: 'center' },
  searchResult: { flexDirection: 'row', alignItems: 'center', padding: 16, borderBottomWidth: 1, borderBottomColor: theme.colors.border },
  searchResultTitle: { fontSize: 16, color: theme.colors.text },
  searchResultArtist: { fontSize: 14, color: theme.colors.textSecondary },
  addIcon: { fontSize: 28, color: theme.colors.primary },
  
  // Chat
  chatHeader: { flexDirection: 'row', alignItems: 'center', padding: 16, borderBottomWidth: 1, borderBottomColor: theme.colors.border },
  chatTitle: { fontSize: 20, fontWeight: 'bold', color: theme.colors.text, marginLeft: 16 },
  chatInputContainer: { flexDirection: 'row', padding: 16, borderTopWidth: 1, borderTopColor: theme.colors.border },
  messageItem: { backgroundColor: theme.colors.card, padding: 12, borderRadius: 12, marginBottom: 8, maxWidth: '80%' },
  ownMessage: { alignSelf: 'flex-end', backgroundColor: theme.colors.primary },
  messageSender: { fontSize: 12, color: theme.colors.secondary, marginBottom: 4 },
  messageContent: { color: theme.colors.text },
  
  // Friends
  friendItem: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', backgroundColor: theme.colors.card, padding: 16, borderRadius: 12, marginBottom: 8 },
  friendName: { fontSize: 16, color: theme.colors.text, fontWeight: '600' },
  friendUsername: { fontSize: 14, color: theme.colors.textSecondary },
  
  // Profile
  profileName: { fontSize: 24, fontWeight: 'bold', color: theme.colors.text },
  profileUsername: { fontSize: 16, color: theme.colors.primary, marginBottom: 4 },
  profileEmail: { fontSize: 14, color: theme.colors.textSecondary, marginBottom: 16 },
  
  // Screens
  screenTitle: { fontSize: 28, fontWeight: 'bold', color: theme.colors.text, marginBottom: 8 },
  screenSubtitle: { fontSize: 16, color: theme.colors.textSecondary, marginBottom: 16 },
  
  // Empty States
  emptyState: { padding: 40, alignItems: 'center' },
  emptyText: { fontSize: 18, color: theme.colors.textSecondary },
  emptySubtext: { fontSize: 14, color: theme.colors.textSecondary, marginTop: 8 },
});
