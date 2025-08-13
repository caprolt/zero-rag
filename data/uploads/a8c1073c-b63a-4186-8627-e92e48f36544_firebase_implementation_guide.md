# Firebase Implementation Guide - Toothbrush App MVP

## 🎯 Project Context

**App**: React Native/Expo toothbrush timer app for kids (4-10 years)
**Goal**: 2-minute brushing timer with engaging stories and gamification
**Stack**: React Native + Expo + TypeScript + Firebase
**Target**: Cost-effective MVP with scalability for 0-10k users

## 🔥 Firebase Products Required

### Core Products for MVP
1. **Firestore Database** - User data, achievements, settings
2. **Firebase Storage** - Story audio files, images, assets
3. **Firebase Authentication** - Anonymous auth for kids

### Package Installation
```bash
npm install @react-native-firebase/app
npm install @react-native-firebase/firestore
npm install @react-native-firebase/storage
npm install @react-native-firebase/auth
npm install @react-native-firebase/analytics  # Optional for tracking
```

## 📊 Data Architecture

### Firestore Collections Structure

```typescript
// Main Collections
users/{userId}/
├── profile: UserProfile
├── settings: UserSettings  
├── achievements: UserAchievements
├── sessions: BrushingSession[]
└── favorites: string[] // Array of story IDs

stories/{storyId}/
├── metadata: StoryMetadata
└── stats: StoryStats

// Type Definitions
interface UserProfile {
  id: string;
  name: string; // "Little Brusher"
  avatar?: string; // Storage URL
  totalSessions: number; // 28
  currentStreak: number; // 7
  longestStreak: number;
  createdAt: Timestamp;
  lastActiveAt: Timestamp;
}

interface UserSettings {
  soundEnabled: boolean; // true
  nightMode: boolean; // false  
  notifications: boolean; // true
  preferredVolume: number; // 0.8
  autoPlayNext: boolean; // true
}

interface UserAchievements {
  firstBrush: boolean; // true
  weekWarrior: boolean; // true
  storyMaster: boolean; // false
  perfectMonth: boolean; // false
  // Add more achievements as needed
}

interface BrushingSession {
  id: string;
  date: Timestamp;
  duration: number; // seconds (goal: 120)
  completed: boolean;
  storyId?: string;
  quadrantsCompleted: number; // 0-4
}

interface StoryMetadata {
  id: string;
  title: string;
  description: string;
  duration: number; // seconds
  ageGroup: '4-6' | '7-10' | 'all';
  audioUrl: string; // Firebase Storage URL
  thumbnailUrl?: string;
  category: 'adventure' | 'educational' | 'magical' | 'funny';
  createdAt: Timestamp;
}

interface StoryStats {
  totalPlays: number;
  favorites: number;
  rating: number; // 1-5 average
}
```

## 🔐 Authentication Setup

### Anonymous Authentication (Kid-Friendly)
```typescript
// auth.ts
import auth from '@react-native-firebase/auth';

export const signInAnonymously = async (): Promise<string> => {
  try {
    const userCredential = await auth().signInAnonymously();
    return userCredential.user.uid;
  } catch (error) {
    console.error('Anonymous sign-in failed:', error);
    throw error;
  }
};

export const getCurrentUserId = (): string | null => {
  return auth().currentUser?.uid || null;
};

// Multiple Profiles (Siblings)
export const createUserProfile = async (name: string): Promise<UserProfile> => {
  const userId = getCurrentUserId();
  if (!userId) throw new Error('No authenticated user');

  const profile: UserProfile = {
    id: userId,
    name,
    totalSessions: 0,
    currentStreak: 0,
    longestStreak: 0,
    createdAt: firestore.Timestamp.now(),
    lastActiveAt: firestore.Timestamp.now(),
  };

  await firestore()
    .collection('users')
    .doc(userId)
    .collection('profile')
    .doc('data')
    .set(profile);

  return profile;
};
```

## 💾 Database Operations

### User Profile Management
```typescript
// userService.ts
import firestore from '@react-native-firebase/firestore';

export class UserService {
  private userId: string;

  constructor(userId: string) {
    this.userId = userId;
  }

  // Get user profile with real-time updates
  getProfile(callback: (profile: UserProfile | null) => void) {
    return firestore()
      .collection('users')
      .doc(this.userId)
      .collection('profile')
      .doc('data')
      .onSnapshot((doc) => {
        if (doc.exists) {
          callback(doc.data() as UserProfile);
        } else {
          callback(null);
        }
      });
  }

  // Update settings
  async updateSettings(settings: Partial<UserSettings>) {
    await firestore()
      .collection('users')
      .doc(this.userId)
      .collection('settings')
      .doc('data')
      .update(settings);
  }

  // Record brushing session
  async recordSession(session: Omit<BrushingSession, 'id'>) {
    const sessionData = {
      ...session,
      id: firestore().collection('temp').doc().id,
    };

    await firestore()
      .collection('users')
      .doc(this.userId)
      .collection('sessions')
      .doc(sessionData.id)
      .set(sessionData);

    // Update streak and total sessions
    await this.updateProfileStats(session.completed);
  }

  // Update achievement
  async unlockAchievement(achievementKey: keyof UserAchievements) {
    await firestore()
      .collection('users')
      .doc(this.userId)
      .collection('achievements')
      .doc('data')
      .update({
        [achievementKey]: true
      });
  }

  // Manage favorites
  async toggleFavorite(storyId: string) {
    const favoritesRef = firestore()
      .collection('users')
      .doc(this.userId)
      .collection('favorites')
      .doc('data');

    await firestore().runTransaction(async (transaction) => {
      const doc = await transaction.get(favoritesRef);
      const favorites = doc.data()?.stories || [];
      
      if (favorites.includes(storyId)) {
        // Remove from favorites
        transaction.update(favoritesRef, {
          stories: firestore.FieldValue.arrayRemove(storyId)
        });
      } else {
        // Add to favorites
        transaction.update(favoritesRef, {
          stories: firestore.FieldValue.arrayUnion(storyId)
        });
      }
    });
  }

  private async updateProfileStats(completed: boolean) {
    // Implementation for streak calculation
    // This would check last session date and update streaks accordingly
  }
}
```

### Story Management
```typescript
// storyService.ts
export class StoryService {
  // Get all stories
  static getStories(callback: (stories: StoryMetadata[]) => void) {
    return firestore()
      .collection('stories')
      .orderBy('createdAt', 'desc')
      .onSnapshot((snapshot) => {
        const stories = snapshot.docs.map(doc => ({
          id: doc.id,
          ...doc.data()
        } as StoryMetadata));
        callback(stories);
      });
  }

  // Get stories by age group
  static getStoriesByAge(ageGroup: string, callback: (stories: StoryMetadata[]) => void) {
    return firestore()
      .collection('stories')
      .where('ageGroup', 'in', [ageGroup, 'all'])
      .orderBy('createdAt', 'desc')
      .onSnapshot((snapshot) => {
        const stories = snapshot.docs.map(doc => ({
          id: doc.id,
          ...doc.data()
        } as StoryMetadata));
        callback(stories);
      });
  }

  // Increment play count
  static async recordPlay(storyId: string) {
    await firestore()
      .collection('stories')
      .doc(storyId)
      .collection('stats')
      .doc('data')
      .update({
        totalPlays: firestore.FieldValue.increment(1)
      });
  }
}
```

## 📁 Storage Operations

### Audio File Management
```typescript
// storageService.ts
import storage from '@react-native-firebase/storage';

export class StorageService {
  // Upload story audio file
  static async uploadStoryAudio(storyId: string, audioUri: string): Promise<string> {
    const reference = storage().ref(`stories/${storyId}/audio.mp3`);
    await reference.putFile(audioUri);
    return await reference.getDownloadURL();
  }

  // Upload user avatar
  static async uploadAvatar(userId: string, imageUri: string): Promise<string> {
    const reference = storage().ref(`users/${userId}/avatar.jpg`);
    await reference.putFile(imageUri);
    return await reference.getDownloadURL();
  }

  // Download story for offline use
  static async downloadStoryForOffline(storyId: string, audioUrl: string): Promise<string> {
    const reference = storage().refFromURL(audioUrl);
    const localPath = `${RNFS.DocumentDirectoryPath}/stories/${storyId}.mp3`;
    
    await reference.writeToFile(localPath);
    return localPath;
  }

  // Get cached file path
  static getCachedStoryPath(storyId: string): string {
    return `${RNFS.DocumentDirectoryPath}/stories/${storyId}.mp3`;
  }
}
```

## 🎮 State Management Integration

### Using with Zustand (Recommended)
```typescript
// stores/userStore.ts
import { create } from 'zustand';

interface UserStore {
  profile: UserProfile | null;
  settings: UserSettings;
  achievements: UserAchievements;
  favorites: string[];
  
  // Actions
  setProfile: (profile: UserProfile) => void;
  updateSettings: (settings: Partial<UserSettings>) => void;
  unlockAchievement: (key: keyof UserAchievements) => void;
  toggleFavorite: (storyId: string) => void;
}

export const useUserStore = create<UserStore>((set, get) => ({
  profile: null,
  settings: {
    soundEnabled: true,
    nightMode: false,
    notifications: true,
    preferredVolume: 0.8,
    autoPlayNext: true,
  },
  achievements: {
    firstBrush: false,
    weekWarrior: false,
    storyMaster: false,
    perfectMonth: false,
  },
  favorites: [],

  setProfile: (profile) => set({ profile }),
  updateSettings: (newSettings) => 
    set((state) => ({ settings: { ...state.settings, ...newSettings } })),
  unlockAchievement: (key) => 
    set((state) => ({ achievements: { ...state.achievements, [key]: true } })),
  toggleFavorite: (storyId) => 
    set((state) => ({
      favorites: state.favorites.includes(storyId)
        ? state.favorites.filter(id => id !== storyId)
        : [...state.favorites, storyId]
    })),
}));
```

## 🔄 Offline Support

### Data Persistence Strategy
```typescript
// offline.ts
import firestore from '@react-native-firebase/firestore';

// Enable offline persistence
firestore().settings({
  persistence: true,
  cacheSizeBytes: firestore.CACHE_SIZE_UNLIMITED,
});

// Cache essential data
export const enableOfflineMode = async () => {
  // Enable offline persistence for user data
  await firestore().enableNetwork();
  
  // Preload essential collections
  await firestore().collection('stories').get({ source: 'cache' });
};

// Sync when back online
export const syncWhenOnline = async () => {
  await firestore().enableNetwork();
  // Firebase automatically syncs pending writes
};
```

## 💰 Cost Estimates

### Free Tier Limits
- **Firestore**: 50k reads + 20k writes per day
- **Storage**: 5GB total + 1GB/day transfer
- **Authentication**: Unlimited users

### Usage Projections
```
MVP Phase (0-1k users):
- Daily reads: ~10k (well within free tier)
- Daily writes: ~2k (well within free tier)
- Storage: ~500MB audio files
- Cost: $0/month

Growth Phase (1k-5k users):
- Daily reads: ~50k (at free tier limit)
- Daily writes: ~10k (within free tier)
- Storage: ~2GB
- Cost: $0-25/month

Scale Phase (5k+ users):
- Firestore: $25-100/month
- Storage: $5-20/month
- Total: $30-120/month
```

## 🚀 Implementation Timeline

### Week 1: Foundation
- [ ] Firebase project setup
- [ ] Anonymous authentication
- [ ] Basic Firestore collections
- [ ] User profile creation

### Week 2: Core Features
- [ ] Settings persistence
- [ ] Session recording
- [ ] Basic offline support
- [ ] Story metadata setup

### Week 3: Enhanced Features
- [ ] Achievement system
- [ ] Favorites functionality
- [ ] Storage integration for audio
- [ ] Real-time updates

### Week 4: Polish & Optimization
- [ ] Offline story caching
- [ ] Performance optimization
- [ ] Error handling
- [ ] Analytics integration

## 🧪 Testing Strategy

### Local Testing
```typescript
// Use Firebase emulator for development
import { connectFirestoreEmulator } from '@react-native-firebase/firestore';

if (__DEV__) {
  connectFirestoreEmulator(firestore(), 'localhost', 8080);
}
```

### Test Data Structure
```typescript
// testData.ts - Sample data for development
export const testStories: StoryMetadata[] = [
  {
    id: 'story1',
    title: 'The Magic Toothbrush Adventure',
    description: 'Join Captain Sparkle on a magical journey...',
    duration: 120,
    ageGroup: '4-6',
    audioUrl: 'gs://your-bucket/stories/story1/audio.mp3',
    category: 'magical',
    createdAt: firestore.Timestamp.now(),
  },
  // Add more test stories...
];
```

## 📱 Integration Points

### With Existing App Components
```typescript
// In your profile screen (app/(tabs)/profile.tsx)
import { useUserStore } from '@/stores/userStore';
import { UserService } from '@/services/userService';

export default function ProfileScreen() {
  const { profile, settings, updateSettings } = useUserStore();
  
  // Use Firebase data instead of local state
  const handleSoundToggle = async (value: boolean) => {
    await userService.updateSettings({ soundEnabled: value });
    updateSettings({ soundEnabled: value });
  };
  
  // Rest of component...
}
```

## 🔧 Security Rules

### Firestore Rules
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only access their own data
    match /users/{userId}/{document=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Stories are publicly readable
    match /stories/{storyId} {
      allow read: if request.auth != null;
      allow write: if false; // Only admin can write stories
    }
  }
}
```

### Storage Rules
```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    // Stories are publicly readable
    match /stories/{allPaths=**} {
      allow read: if request.auth != null;
      allow write: if false; // Only admin uploads
    }
    
    // Users can manage their own avatars
    match /users/{userId}/{allPaths=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

This implementation provides a complete Firebase backend that scales from MVP to production while maintaining cost efficiency and child safety standards.