# FREQUENCY FACTORY - COMPLETE BUILD DOCUMENT
**Version:** 1.0  
**Date:** October 24, 2025  
**Owner:** DaDDi (D RoC)  
**Status:** PRE-LAUNCH DEVELOPMENT

---

## 📋 TABLE OF CONTENTS
1. [Executive Summary](#executive-summary)
2. [Business Model](#business-model)
3. [Technical Architecture](#technical-architecture)
4. [Build Checklist](#build-checklist)
5. [Firebase Setup Guide](#firebase-setup-guide)
6. [Payment Integration](#payment-integration)
7. [Music System](#music-system)
8. [Admin Dashboard](#admin-dashboard)
9. [YouTube Stream](#youtube-stream)
10. [Legal Documents](#legal-documents)
11. [Launch Plan](#launch-plan)
12. [Code Snippets](#code-snippets)

---

## 🎯 EXECUTIVE SUMMARY

### **What Is Frequency Factory?**
An independent A&R gaming platform where users rate submitted music tracks (Hook/Vibe/Prod/Barz) in real-time, earn tokens through gamification, and compete on leaderboards. Top-rated tracks get "Factory Certified" stamps and featured placement.

### **The Vision**
- **Core Platform:** Runs 24/7, fully independent
- **Revenue:** Artist submissions, token purchases, merch, franchising
- **Growth:** Organic community + 24/7 YouTube stream
- **Future:** White-label franchise model for other review shows

### **Key Differentiator**
NOT dependent on any creator partnership. Factory exists standalone. Creators can optionally license the wrapper, but Factory thrives independently.

---

## 💰 BUSINESS MODEL

### **Revenue Streams**

**1. Artist Submissions**
- Standard Queue: FREE (24-48hr wait)
- Priority Slot #2: $20 (12hr review)
- Priority Slot #1: $50 (next up, 1hr review)
- Monthly Access Pass: $20/month (unlimited standard submissions)

**2. Token Economy**
- Players earn tokens by rating tracks
- Buy tokens with real money: $5 for 100 tokens, $20 for 500 tokens
- Spend tokens on:
  - Queue skips
  - Profile customization
  - Exclusive challenges
  - Merch discounts

**3. Factory Certified Merch**
- Tracks rated 90+ get certification
- Artists buy official badge graphics: $10
- Physical certificates: $25
- Custom merch with certification: $40+
- Profit margin: ~42%

**4. Creator Franchise (Future)**
- Setup Fee: $500 one-time
- Monthly License: $200-300/month OR 20% revenue share
- Provides: Branded wrapper, white-label platform, technical support

**5. YouTube Revenue**
- Ad revenue from 24/7 stream
- Sponsorships (future)
- Affiliate links

### **Projected Revenue (Month 3)**
- Artist submissions: $1,500-3,000
- Token purchases: $500-1,000
- Merch: $300-800
- YouTube: $200-500
- **Total: $2,500-5,300/month**

### **Monthly Costs**
- Firebase: $25-100
- Stripe fees: 2.9% + $0.30 per transaction
- Cloudflare R2: $0.50-5
- Email service: $0-15
- Domain: $1
- **Total: $50-150/month initially**

**Net Profit (Month 3):** $2,000-5,000+

---

## 🏗️ TECHNICAL ARCHITECTURE

### **Stack**
- **Frontend:** HTML/CSS/JavaScript (Tailwind CSS)
- **Backend:** Firebase (Firestore + Auth + Storage)
- **Payments:** Stripe
- **Hosting:** Netlify
- **Storage:** Cloudflare R2 (music files)
- **Functions:** Netlify Functions or Cloudflare Workers
- **CDN:** Cloudflare
- **Email:** SendGrid
- **Analytics:** Firebase Analytics + Google Analytics 4

### **Database Structure (Firestore)**

```
artifacts/
  └── frequency-factory-prod/
      ├── public/
      │   └── data/
      │       ├── tracks/ (collection)
      │       │   └── {trackId}/
      │       │       ├── artist: string
      │       │       ├── title: string
      │       │       ├── audioUrl: string
      │       │       ├── order: number (1, 2, or 100)
      │       │       ├── submittedAt: timestamp
      │       │       ├── submittedBy: userId
      │       │       ├── status: "pending" | "approved" | "rejected"
      │       │       ├── votes/ (subcollection)
      │       │       │   └── {userId}/
      │       │       │       ├── hook: number (0-100)
      │       │       │       ├── vibe: number (0-100)
      │       │       │       ├── prod: number (0-100)
      │       │       │       ├── barz: number (0-100)
      │       │       └── feedback/ (subcollection)
      │       │           └── {userId}/
      │       │               └── action: "like" | "dislike" | "none"
      │       └── profiles/ (collection - public leaderboard)
      │           └── {userId}/
      │               ├── name: string
      │               ├── tokens: number
      │               └── avatar: string (optional)
      └── users/ (collection)
          └── {userId}/
              ├── profile/
              │   └── main (document)
              │       ├── tokens: number
              │       ├── streak: number
              │       ├── lastLogin: timestamp
              │       ├── name: string
              │       └── email: string (optional)
              ├── my_ratings/
              │   └── all_ratings (document)
              │       └── {trackId}: true (for queue filtering)
              └── submissions/ (collection)
                  └── {submissionId}/
                      ├── trackId: reference
                      ├── submittedAt: timestamp
                      └── status: string
```

### **Firestore Security Rules**

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Public data - anyone can read
    match /artifacts/frequency-factory-prod/public/data/{document=**} {
      allow read: if true;
      allow write: if false; // Only via admin or functions
    }
    
    // Tracks - authenticated users can submit
    match /artifacts/frequency-factory-prod/public/data/tracks/{trackId} {
      allow read: if true;
      allow create: if request.auth != null;
      
      // Votes - users can only write their own
      match /votes/{userId} {
        allow read: if true;
        allow write: if request.auth.uid == userId;
      }
      
      // Feedback - users can only write their own
      match /feedback/{userId} {
        allow read: if true;
        allow write: if request.auth.uid == userId;
      }
    }
    
    // User profiles - users can only write their own
    match /artifacts/frequency-factory-prod/users/{userId}/{document=**} {
      allow read: if request.auth.uid == userId;
      allow write: if request.auth.uid == userId;
    }
    
    // Public profiles for leaderboard
    match /artifacts/frequency-factory-prod/public/data/profiles/{userId} {
      allow read: if true;
      allow write: if request.auth.uid == userId;
    }
  }
}
```

---

## ✅ BUILD CHECKLIST

### **PHASE 1: FOUNDATION (Week 1)**

#### Firebase Setup
- [ ] Create Firebase project at console.firebase.google.com
- [ ] Enable Firestore Database
- [ ] Enable Authentication (Anonymous)
- [ ] Enable Firebase Storage
- [ ] Set up security rules (see above)
- [ ] Copy config credentials to HTML
- [ ] Test anonymous auth
- [ ] Test Firestore write/read
- [ ] Verify real-time listeners work

#### Payment Processing
- [ ] Create Stripe account
- [ ] Get API keys (test & live)
- [ ] Create products in Stripe:
  - [ ] One-time submission ($5)
  - [ ] Monthly subscription ($20)
  - [ ] Priority #2 ($20)
  - [ ] Priority #1 ($50)
  - [ ] Token pack 100 ($5)
  - [ ] Token pack 500 ($20)
- [ ] Implement Stripe Checkout
- [ ] Create webhook endpoint (Netlify Function)
- [ ] Test payment flow
- [ ] Handle payment success/failure
- [ ] Send confirmation emails

#### Music Upload System
- [ ] Set up Cloudflare R2 bucket
- [ ] Create upload form component
- [ ] Implement file validation (MP3/WAV, max 10MB)
- [ ] Generate presigned upload URLs
- [ ] Store file metadata in Firestore
- [ ] Create audio player component
- [ ] Test playback in browser
- [ ] Add loading states
- [ ] Handle errors gracefully

#### Admin Dashboard
- [ ] Create admin HTML page
- [ ] Add Firebase Admin SDK
- [ ] List all pending submissions
- [ ] Approve/reject functionality
- [ ] Edit track metadata
- [ ] View user analytics
- [ ] Ban/unban users
- [ ] Manage queue order manually
- [ ] Export data (CSV)

---

### **PHASE 2: POLISH (Week 2)**

#### Email Notifications
- [ ] Set up SendGrid account
- [ ] Create email templates:
  - [ ] Submission confirmation
  - [ ] Payment receipt
  - [ ] Track approved
  - [ ] Track rejected
  - [ ] Factory Certified (90+)
  - [ ] Daily leaderboard
  - [ ] Mission reminders
- [ ] Implement email sending (Netlify Function)
- [ ] Test all email flows
- [ ] Add unsubscribe links

#### Content Moderation
- [ ] Add reCAPTCHA to submission form
- [ ] Implement duplicate detection
- [ ] Add profanity filter
- [ ] Create abuse reporting button
- [ ] Manual review queue
- [ ] Automated flagging system
- [ ] DMCA takedown process

#### Analytics Integration
- [ ] Add Google Analytics 4
- [ ] Set up Firebase Analytics
- [ ] Track key events:
  - [ ] User signups (clock-in)
  - [ ] Track submissions
  - [ ] Ratings submitted
  - [ ] Payments completed
  - [ ] Tokens earned/spent
- [ ] Create admin analytics dashboard
- [ ] Set up conversion tracking

#### SEO & Discoverability
- [ ] Add Open Graph tags
- [ ] Add Twitter Card tags
- [ ] Create sitemap.xml
- [ ] Add structured data (JSON-LD)
- [ ] Optimize meta descriptions
- [ ] Create robots.txt
- [ ] Submit to Google Search Console

---

### **PHASE 3: STREAMING (Week 3)**

#### YouTube Channel
- [ ] Create "Frequency Factory" channel
- [ ] Design channel art (banner, logo)
- [ ] Write channel description
- [ ] Add links to platform
- [ ] Enable live streaming
- [ ] Set up stream key

#### OBS Automation
- [ ] Install OBS Studio
- [ ] Create browser source (Factory platform)
- [ ] Design stream overlays:
  - [ ] "Now Playing" graphic
  - [ ] Rating display
  - [ ] Queue countdown
  - [ ] Leaderboard ticker
  - [ ] Factory logo
- [ ] Set up audio routing
- [ ] Configure stream settings (1080p, 60fps)
- [ ] Test stream quality

#### 24/7 System
- [ ] Set up dedicated streaming PC/VPS
- [ ] Install OBS
- [ ] Configure auto-start on boot
- [ ] Set up fallback playlist (when queue empty)
- [ ] Use Restream.io for redundancy
- [ ] Monitor uptime
- [ ] Create stream schedule
- [ ] Test failover

---

### **PHASE 4: LEGAL & COMPLIANCE**

#### Legal Documents
- [ ] Terms of Service (template + customize)
- [ ] Privacy Policy (GDPR/CCPA compliant)
- [ ] Cookie Policy
- [ ] Artist Submission Agreement
- [ ] Payment Terms & Refunds
- [ ] Community Guidelines
- [ ] DMCA Takedown Process
- [ ] Get legal review (optional but recommended)

#### Business Setup
- [ ] Register LLC (recommended)
- [ ] Get EIN from IRS
- [ ] Open business bank account
- [ ] Set up accounting system (QuickBooks/Wave)
- [ ] Register for sales tax (if needed)
- [ ] Get business insurance (optional)

---

### **PHASE 5: SOFT LAUNCH (Week 4)**

#### Beta Testing
- [ ] Invite 10-20 beta testers
- [ ] Create feedback form
- [ ] Monitor for bugs
- [ ] Track user behavior
- [ ] Gather feature requests
- [ ] Fix critical issues
- [ ] Optimize performance

#### Marketing Prep
- [ ] Create social media accounts:
  - [ ] Twitter/X
  - [ ] Instagram
  - [ ] TikTok
  - [ ] Discord server
- [ ] Design marketing assets
- [ ] Write launch announcement
- [ ] Create promo video
- [ ] Reach out to music blogs
- [ ] Prepare press release

---

### **PHASE 6: PUBLIC LAUNCH**

#### Go-Live
- [ ] Final testing checklist
- [ ] Switch from test to live payments
- [ ] Enable YouTube stream 24/7
- [ ] Publish launch announcement
- [ ] Post on social media
- [ ] Email artist communities
- [ ] Reach out to creator partners
- [ ] Monitor for issues
- [ ] Respond to feedback

#### Post-Launch
- [ ] Daily check-ins (first week)
- [ ] Fix bugs as reported
- [ ] Onboard new artists
- [ ] Grow community
- [ ] Iterate based on feedback
- [ ] Plan feature updates

---

## 🔥 FIREBASE SETUP GUIDE

### **Step 1: Create Project**
1. Go to https://console.firebase.google.com
2. Click "Add Project"
3. Name it "Frequency Factory"
4. Disable Google Analytics (for now, can enable later)
5. Click "Create Project"

### **Step 2: Enable Services**

**Firestore:**
1. Click "Firestore Database" in left menu
2. Click "Create database"
3. Choose "Start in test mode" (we'll add rules later)
4. Select location closest to target audience
5. Click "Enable"

**Authentication:**
1. Click "Authentication" in left menu
2. Click "Get started"
3. Click "Anonymous" provider
4. Toggle "Enable"
5. Click "Save"

**Storage:**
1. Click "Storage" in left menu
2. Click "Get started"
3. Choose "Start in test mode"
4. Click "Next"
5. Select same location as Firestore
6. Click "Done"

### **Step 3: Get Config Credentials**
1. Click gear icon → "Project settings"
2. Scroll to "Your apps"
3. Click "</>" (Web icon)
4. Register app name: "Frequency Factory"
5. Check "Also set up Firebase Hosting" (optional)
6. Click "Register app"
7. Copy the `firebaseConfig` object

**It will look like this:**
```javascript
const firebaseConfig = {
  apiKey: "AIzaSyBXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  authDomain: "frequency-factory-xxxxx.firebaseapp.com",
  projectId: "frequency-factory-xxxxx",
  storageBucket: "frequency-factory-xxxxx.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abcdef1234567890abcdef"
};
```

### **Step 4: Update HTML**
Replace the placeholder config in `frequency-factory.html`:

```javascript
// OLD (line ~20)
const firebaseConfig = {
    apiKey: "YOUR_API_KEY_HERE",
    authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_PROJECT_ID.appspot.com",
    messagingSenderId: "YOUR_SENDER_ID",
    appId: "YOUR_APP_ID_FROM_FIREBASE"
};

// NEW (paste your actual config)
const firebaseConfig = {
    apiKey: "AIzaSyBXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    authDomain: "frequency-factory-xxxxx.firebaseapp.com",
    projectId: "frequency-factory-xxxxx",
    storageBucket: "frequency-factory-xxxxx.appspot.com",
    messagingSenderId: "123456789012",
    appId: "1:123456789012:web:abcdef1234567890abcdef"
};
```

### **Step 5: Deploy Security Rules**
1. Go back to Firestore Database
2. Click "Rules" tab
3. Paste the security rules from [Technical Architecture](#technical-architecture)
4. Click "Publish"

### **Step 6: Test**
1. Open `frequency-factory.html` in browser
2. Open browser console (F12)
3. Click "Clock In" button
4. Check console for "User is signed in: [userId]"
5. Check Firestore for new user document
6. If working → ✅ Firebase is configured!

---

## 💳 PAYMENT INTEGRATION

### **Stripe Setup**

**Step 1: Create Account**
1. Go to https://stripe.com
2. Sign up for account
3. Complete business verification
4. Get approved

**Step 2: Create Products**
1. Go to Dashboard → Products
2. Click "Add product" for each:

**Product: One-Time Submission**
- Name: "Track Submission - One Time"
- Price: $5 USD
- Type: One-time
- Copy Price ID: `price_XXXXXXXXXXXXX`

**Product: Monthly Subscription**
- Name: "Track Submission - Monthly Pass"
- Price: $20 USD
- Type: Recurring (monthly)
- Copy Price ID: `price_XXXXXXXXXXXXX`

**Product: Priority Slot #2**
- Name: "Priority Review #2"
- Price: $20 USD
- Type: One-time
- Copy Price ID: `price_XXXXXXXXXXXXX`

**Product: Priority Slot #1**
- Name: "Priority Review #1"
- Price: $50 USD
- Type: One-time
- Copy Price ID: `price_XXXXXXXXXXXXX`

**Step 3: Get API Keys**
1. Go to Developers → API Keys
2. Copy "Publishable key" (starts with `pk_test_`)
3. Copy "Secret key" (starts with `sk_test_`)
4. Store secret key securely (never in frontend code)

### **Implementation**

**Frontend (HTML):**
```javascript
// Add Stripe script to <head>
<script src="https://js.stripe.com/v3/"></script>

// Replace handleUnlockSubForm function:
async function handlePayment(priceId, type) {
    playSound('click');
    
    const stripe = Stripe('pk_test_YOUR_PUBLISHABLE_KEY_HERE');
    
    // Call your backend to create checkout session
    const response = await fetch('/.netlify/functions/create-checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            priceId: priceId,
            userId: userId,
            type: type 
        })
    });
    
    const session = await response.json();
    
    // Redirect to Stripe Checkout
    const { error } = await stripe.redirectToCheckout({
        sessionId: session.id
    });
    
    if (error) {
        showModal('Payment Error', error.message, false);
        playSound('error');
    }
}

// Update button click handlers:
UIElements.btnPayOnce.addEventListener('click', () => {
    handlePayment('price_XXXXXXXXXXXXX', 'one-time');
});

UIElements.btnPaySub.addEventListener('click', () => {
    handlePayment('price_XXXXXXXXXXXXX', 'subscription');
});
```

**Backend (Netlify Function):**

Create file: `netlify/functions/create-checkout.js`

```javascript
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

exports.handler = async (event) => {
    const { priceId, userId, type } = JSON.parse(event.body);
    
    try {
        const session = await stripe.checkout.sessions.create({
            mode: type === 'subscription' ? 'subscription' : 'payment',
            line_items: [{ price: priceId, quantity: 1 }],
            success_url: `${process.env.URL}?payment=success&session_id={CHECKOUT_SESSION_ID}`,
            cancel_url: `${process.env.URL}?payment=cancel`,
            client_reference_id: userId,
            metadata: { userId: userId, type: type }
        });
        
        return {
            statusCode: 200,
            body: JSON.stringify({ id: session.id })
        };
    } catch (error) {
        return {
            statusCode: 400,
            body: JSON.stringify({ error: error.message })
        };
    }
};
```

**Webhook Handler:**

Create file: `netlify/functions/stripe-webhook.js`

```javascript
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const admin = require('firebase-admin');

// Initialize Firebase Admin
if (!admin.apps.length) {
    admin.initializeApp({
        credential: admin.credential.cert({
            projectId: process.env.FIREBASE_PROJECT_ID,
            clientEmail: process.env.FIREBASE_CLIENT_EMAIL,
            privateKey: process.env.FIREBASE_PRIVATE_KEY.replace(/\\n/g, '\n')
        })
    });
}

const db = admin.firestore();

exports.handler = async (event) => {
    const sig = event.headers['stripe-signature'];
    let stripeEvent;
    
    try {
        stripeEvent = stripe.webhooks.constructEvent(
            event.body,
            sig,
            process.env.STRIPE_WEBHOOK_SECRET
        );
    } catch (err) {
        return { statusCode: 400, body: `Webhook Error: ${err.message}` };
    }
    
    // Handle successful payment
    if (stripeEvent.type === 'checkout.session.completed') {
        const session = stripeEvent.data.object;
        const userId = session.client_reference_id;
        
        // Unlock submission form for this user
        await db.doc(`artifacts/frequency-factory-prod/users/${userId}/access/submissions`).set({
            hasAccess: true,
            purchasedAt: admin.firestore.FieldValue.serverTimestamp(),
            type: session.metadata.type
        });
        
        // Send confirmation email (implement later)
    }
    
    return { statusCode: 200, body: 'Success' };
};
```

**Environment Variables (Netlify):**
```
STRIPE_SECRET_KEY=sk_test_XXXXXXXXXXXXX
STRIPE_WEBHOOK_SECRET=whsec_XXXXXXXXXXXXX
FIREBASE_PROJECT_ID=frequency-factory-xxxxx
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@frequency-factory-xxxxx.iam.gserviceaccount.com
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nXXXXXXXXXXXXXXXXXXX\n-----END PRIVATE KEY-----\n"
URL=https://frequencyfactory.com
```

---

## 🎵 MUSIC SYSTEM

### **Cloudflare R2 Setup**

**Step 1: Create Bucket**
1. Go to Cloudflare Dashboard
2. Click "R2" in sidebar
3. Click "Create bucket"
4. Name: "frequency-factory-music"
5. Location: Auto
6. Click "Create bucket"

**Step 2: Generate API Token**
1. Click "Manage R2 API Tokens"
2. Click "Create API Token"
3. Name: "Frequency Factory Upload"
4. Permissions: Read & Write
5. Copy Access Key ID & Secret Access Key

**Step 3: Configure CORS**
```json
[
  {
    "AllowedOrigins": ["https://frequencyfactory.com"],
    "AllowedMethods": ["GET", "PUT", "POST"],
    "AllowedHeaders": ["*"],
    "MaxAgeSeconds": 3600
  }
]
```

### **Upload Implementation**

**Frontend (Add to HTML):**

```javascript
// Add file input to submission form
<input type="file" id="audioFile" name="audioFile" accept=".mp3,.wav" required class="w-full h-10 px-3 form-input">

// Update handleTrackSubmission:
async function handleTrackSubmission(e) {
    e.preventDefault();
    playSound('click');
    
    const form = e.target;
    const artist = form.artist.value.trim();
    const title = form.title.value.trim();
    const audioFile = form.audioFile.files[0];
    const order = parseInt(UIElements.prioritySelect.value);
    
    if (!artist || !title || !audioFile) {
        showModal('Error', 'All fields are required.', false);
        playSound('error');
        return;
    }
    
    // Validate file
    if (audioFile.size > 10 * 1024 * 1024) { // 10MB max
        showModal('Error', 'File too large. Max 10MB.', false);
        playSound('error');
        return;
    }
    
    if (!['audio/mpeg', 'audio/wav'].includes(audioFile.type)) {
        showModal('Error', 'Only MP3 and WAV files allowed.', false);
        playSound('error');
        return;
    }
    
    UIElements.submitButton.classList.add('hidden');
    UIElements.submitSpinner.classList.remove('hidden');
    
    try {
        // 1. Get presigned upload URL from backend
        const urlResponse = await fetch('/.netlify/functions/get-upload-url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                fileName: audioFile.name,
                fileType: audioFile.type,
                userId: userId
            })
        });
        
        const { uploadUrl, fileKey } = await urlResponse.json();
        
        // 2. Upload file to R2
        await fetch(uploadUrl, {
            method: 'PUT',
            body: audioFile,
            headers: { 'Content-Type': audioFile.type }
        });
        
        // 3. Create track in Firestore
        const newTrack = {
            artist,
            title,
            audioUrl: `https://pub-XXXXX.r2.dev/${fileKey}`, // Your R2 public URL
            order,
            submittedAt: serverTimestamp(),
            submittedBy: userId,
            status: 'pending'
        };
        
        const tracksRef = collection(db, `artifacts/${appId}/public/data/tracks`);
        await addDoc(tracksRef, newTrack);
        
        showModal('Submission Received', `"${title}" by ${artist} has been added to the queue.`);
        form.reset();
        UIElements.submissionFields.classList.add('hidden');
        UIElements.paymentButtons.classList.remove('hidden');
        
    } catch (error) {
        console.error("Error submitting track:", error);
        showModal("Error", `Could not submit track: ${error.message}`, false);
        playSound('error');
    } finally {
        UIElements.submitButton.classList.remove('hidden');
        UIElements.submitSpinner.classList.add('hidden');
    }
}
```

**Backend Function:**

Create file: `netlify/functions/get-upload-url.js`

```javascript
const AWS = require('aws-sdk');

const s3 = new AWS.S3({
    endpoint: `https://${process.env.R2_ACCOUNT_ID}.r2.cloudflarestorage.com`,
    accessKeyId: process.env.R2_ACCESS_KEY_ID,
    secretAccessKey: process.env.R2_SECRET_ACCESS_KEY,
    signatureVersion: 'v4',
    region: 'auto'
});

exports.handler = async (event) => {
    const { fileName, fileType, userId } = JSON.parse(event.body);
    
    // Generate unique file key
    const fileKey = `uploads/${userId}/${Date.now()}-${fileName}`;
    
    // Generate presigned URL (valid for 5 minutes)
    const uploadUrl = await s3.getSignedUrlPromise('putObject', {
        Bucket: 'frequency-factory-music',
        Key: fileKey,
        ContentType: fileType,
        Expires: 300
    });
    
    return {
        statusCode: 200,
        body: JSON.stringify({ uploadUrl, fileKey })
    };
};
```

### **Audio Player Component**

Add to HTML where nowPlaying is rendered:

```javascript
function renderNowPlaying() {
    if (!nowPlaying) return;
    
    UIElements.nowArtist.textContent = nowPlaying.artist;
    UIElements.nowTitle.textContent = nowPlaying.title;
    
    // Add audio player
    if (nowPlaying.audioUrl && nowPlaying.status === 'approved') {
        const audioHTML = `
            <audio controls class="w-full mt-4">
                <source src="${nowPlaying.audioUrl}" type="audio/mpeg">
                Your browser does not support the audio element.
            </audio>
        `;
        document.getElementById('audioPlayerContainer').innerHTML = audioHTML;
    }
    
    UIElements.nowArt.src = `https://placehold.co/400x400/${getHexColor(nowPlaying.title)}/050510?text=${encodeURIComponent(nowPlaying.artist.substring(0, 2))}&font=inter`;
    hideCertificationStamp();
}
```

---

## 🛡️ ADMIN DASHBOARD

Create file: `admin.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Frequency Factory - Admin Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="module">
        import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
        import { getAuth, signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
        import { getFirestore, collection, query, where, orderBy, onSnapshot, doc, updateDoc } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";

        const firebaseConfig = {
            // Same config as main app
        };

        const app = initializeApp(firebaseConfig);
        const db = getFirestore(app);
        const auth = getAuth(app);

        // Admin login
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            try {
                await signInWithEmailAndPassword(auth, email, password);
                document.getElementById('loginPanel').classList.add('hidden');
                document.getElementById('adminPanel').classList.remove('hidden');
                loadPendingTracks();
            } catch (error) {
                alert('Login failed: ' + error.message);
            }
        });

        // Load pending tracks
        function loadPendingTracks() {
            const tracksRef = collection(db, 'artifacts/frequency-factory-prod/public/data/tracks');
            const q = query(tracksRef, where('status', '==', 'pending'), orderBy('submittedAt', 'desc'));
            
            onSnapshot(q, (snapshot) => {
                const list = document.getElementById('tracksList');
                list.innerHTML = '';
                
                snapshot.forEach(docSnap => {
                    const track = docSnap.data();
                    const div = document.createElement('div');
                    div.className = 'bg-gray-800 p-4 rounded-lg mb-4';
                    div.innerHTML = `
                        <h3 class="text-xl font-bold text-white">${track.title}</h3>
                        <p class="text-gray-400">by ${track.artist}</p>
                        <audio controls class="w-full mt-2">
                            <source src="${track.audioUrl}" type="audio/mpeg">
                        </audio>
                        <div class="mt-3 flex gap-3">
                            <button onclick="approveTrack('${docSnap.id}')" class="bg-green-600 px-4 py-2 rounded">Approve</button>
                            <button onclick="rejectTrack('${docSnap.id}')" class="bg-red-600 px-4 py-2 rounded">Reject</button>
                        </div>
                    `;
                    list.appendChild(div);
                });
            });
        }

        // Approve track
        window.approveTrack = async (trackId) => {
            await updateDoc(doc(db, `artifacts/frequency-factory-prod/public/data/tracks/${trackId}`), {
                status: 'approved'
            });
            alert('Track approved!');
        };

        // Reject track
        window.rejectTrack = async (trackId) => {
            await updateDoc(doc(db, `artifacts/frequency-factory-prod/public/data/tracks/${trackId}`), {
                status: 'rejected'
            });
            alert('Track rejected!');
        };
    </script>
</head>
<body class="bg-gray-900 text-white p-8">
    
    <!-- Login Panel -->
    <div id="loginPanel" class="max-w-md mx-auto">
        <h1 class="text-3xl font-bold mb-6">Admin Login</h1>
        <form id="loginForm" class="space-y-4">
            <input type="email" id="email" placeholder="Admin Email" class="w-full p-3 bg-gray-800 rounded">
            <input type="password" id="password" placeholder="Password" class="w-full p-3 bg-gray-800 rounded">
            <button type="submit" class="w-full bg-blue-600 p-3 rounded font-bold">Login</button>
        </form>
    </div>

    <!-- Admin Panel -->
    <div id="adminPanel" class="hidden max-w-6xl mx-auto">
        <h1 class="text-3xl font-bold mb-6">Pending Submissions</h1>
        <div id="tracksList"></div>
    </div>

</body>
</html>
```

---

## 📺 YOUTUBE STREAM SETUP

### **OBS Configuration**

**Scene Layout:**
1. **Main Scene - "Factory Floor"**
   - Browser Source: `https://frequencyfactory.com` (1920x1080)
   - Audio: Desktop audio capture
   - Overlay: PNG graphics (logo, "LIVE" indicator)

2. **Overlay Elements:**
   - Top bar: Factory logo + "LIVE 24/7"
   - Bottom ticker: Scrolling queue positions
   - Side panel: Current leaderboard (auto-refresh)
   - "Now Playing" card: Track info + ratings

**OBS Settings:**
- Output: 1920x1080, 60fps
- Bitrate: 6000 kbps
- Encoder: x264 or NVENC (if GPU available)
- Audio: 44.1kHz stereo

### **Auto-Start Script (Windows)**

Create file: `start-factory-stream.bat`

```batch
@echo off
cd "C:\Program Files\obs-studio\bin\64bit"
start "" "obs64.exe" --startstreaming --profile "Frequency Factory" --scene "Factory Floor"
```

Add to Windows Startup folder.

### **Restream.io Setup**
1. Sign up at restream.io
2. Connect YouTube account
3. Add fallback destinations (Twitch, etc.)
4. Copy RTMP URL and Stream Key
5. Add to OBS: Settings → Stream
6. Test connection

---

## 📄 LEGAL DOCUMENTS

### **Terms of Service (Template)**

```markdown
# Terms of Service - Frequency Factory

Last Updated: [DATE]

## 1. Acceptance of Terms
By accessing Frequency Factory ("the Service"), you agree to these Terms.

## 2. User Accounts
- Users may participate anonymously or create accounts
- You are responsible for account security
- Minimum age: 13 years old

## 3. Artist Submissions
- You retain ownership of submitted music
- You grant us license to stream and display your music
- Submissions must not violate copyright or contain illegal content
- We reserve the right to reject any submission
- No refunds on submission fees

## 4. Payments
- All fees are non-refundable
- Processed securely via Stripe
- Priority placement does not guarantee specific ratings

## 5. Token Economy
- Tokens have no real-world cash value
- Cannot be transferred or sold
- We may adjust token values at any time

## 6. Prohibited Conduct
- No harassment, hate speech, or spam
- No automated bots or scripts
- No manipulation of ratings
- Violations result in immediate ban

## 7. Intellectual Property
- The Factory platform is owned by [YOUR COMPANY]
- You may not copy, reproduce, or redistribute our content

## 8. Disclaimer
- Service provided "as is"
- No guarantee of uptime or availability
- Not responsible for user-generated content

## 9. Changes to Terms
We may update these terms at any time. Continued use constitutes acceptance.

Contact: [YOUR EMAIL]
```

### **Privacy Policy (Template)**

```markdown
# Privacy Policy - Frequency Factory

Last Updated: [DATE]

## Information We Collect
- Anonymous usage data (Firebase Analytics)
- Email addresses (if provided)
- Payment information (processed by Stripe, not stored by us)
- IP addresses and device information

## How We Use Information
- To operate and improve the Service
- To process payments
- To send notifications (if opted in)
- To prevent abuse

## Information Sharing
- We do not sell your personal information
- We share data with service providers (Firebase, Stripe)
- We may disclose data if required by law

## Your Rights
- You may request data deletion
- You may opt out of emails
- EU users have additional GDPR rights

## Cookies
We use cookies for:
- Authentication
- Analytics
- Preferences

## Contact
[YOUR EMAIL]
```

---

## 🚀 LAUNCH PLAN

### **Week 1: Foundation**
- Days 1-2: Firebase setup & testing
- Days 3-4: Stripe integration & payment flow
- Days 5-6: Music upload system
- Day 7: Admin dashboard basics

### **Week 2: Polish**
- Days 8-9: Email notifications
- Days 10-11: Content moderation
- Days 12-13: Analytics & SEO
- Day 14: Bug fixes & optimization

### **Week 3: Streaming**
- Days 15-16: YouTube channel setup
- Days 17-18: OBS configuration
- Days 19-20: 24/7 system setup
- Day 21: Stream testing

### **Week 4: Soft Launch**
- Days 22-24: Beta testing with 20 users
- Days 25-27: Fix bugs, gather feedback
- Day 28: Final prep for public launch

### **Week 5: PUBLIC LAUNCH**
- Day 29: Go live announcement
- Day 30: Monitor, support, iterate

---

## 💻 CODE SNIPPETS REFERENCE

### **Firebase Init Check**
```javascript
// Add this after initFirebase()
console.log('Firebase Status Check:');
console.log('- App initialized:', !!app);
console.log('- Auth available:', !!auth);
console.log('- Firestore available:', !!db);
```

### **Manual Token Award (Admin)**
```javascript
async function awardTokensToUser(targetUserId, amount, reason) {
    const privateRef = doc(db, `artifacts/${appId}/users/${targetUserId}/profile`, 'main');
    const publicRef = doc(db, `artifacts/${appId}/public/data/profiles`, targetUserId);
    
    const privateSnap = await getDoc(privateRef);
    const currentTokens = privateSnap.exists() ? privateSnap.data().tokens : 0;
    const newTokens = currentTokens + amount;
    
    const batch = writeBatch(db);
    batch.update(privateRef, { tokens: newTokens });
    batch.update(publicRef, { tokens: newTokens });
    await batch.commit();
    
    console.log(`Awarded ${amount} tokens to ${targetUserId} for: ${reason}`);
}
```

### **Emergency Kill Switch**
```javascript
// Add to admin dashboard
async function pausePlatform() {
    await setDoc(doc(db, 'artifacts/frequency-factory-prod/config/status'), {
        active: false,
        message: 'Platform temporarily offline for maintenance.'
    });
}
```

---

## 🎯 SUCCESS METRICS

### **Week 1 Goals**
- 50 user signups (clock-ins)
- 20 track submissions
- 500+ total ratings
- $100 revenue

### **Month 1 Goals**
- 500 active users
- 100 track submissions
- 10,000+ ratings
- $2,000+ revenue
- 1,000 YouTube subscribers

### **Month 3 Goals**
- 2,000 active users
- 400 track submissions
- 50,000+ ratings
- $5,000+ revenue
- 5,000 YouTube subscribers
- First franchise customer

---

## 📞 SUPPORT & MAINTENANCE

### **Daily Tasks**
- Check admin dashboard for new submissions
- Approve/reject tracks within 24 hours
- Monitor Firebase usage/costs
- Respond to support emails
- Check stream uptime

### **Weekly Tasks**
- Review analytics
- Process payments/payouts
- Update leaderboard manually (if needed)
- Social media engagement
- Bug fixes

### **Monthly Tasks**
- Financial reconciliation
- Backup Firestore data
- Review and update legal docs
- Platform improvements
- Marketing campaigns

---

## 🔐 SECURITY CHECKLIST

- [ ] Firebase security rules deployed
- [ ] Stripe webhook verified
- [ ] Admin dashboard password-protected
- [ ] API keys in environment variables (never in code)
- [ ] HTTPS enforced
- [ ] CORS configured correctly
- [ ] Rate limiting on API endpoints
- [ ] Input validation on all forms
- [ ] File upload scanning (virus check)
- [ ] Regular security audits

---

## ✅ FINAL PRE-LAUNCH CHECKLIST

### **Technical**
- [ ] Firebase connected and tested
- [ ] Payments working (test mode)
- [ ] Music upload working
- [ ] Playback working in all browsers
- [ ] Admin dashboard functional
- [ ] Mobile responsive
- [ ] All links working
- [ ] No console errors

### **Content**
- [ ] Terms of Service live
- [ ] Privacy Policy live
- [ ] Community Guidelines posted
- [ ] FAQ page created
- [ ] Contact information visible

### **Business**
- [ ] Stripe account verified
- [ ] Bank account connected
- [ ] Business entity registered
- [ ] Accounting system set up

### **Marketing**
- [ ] Social media accounts created
- [ ] Launch announcement written
- [ ] Promo materials ready
- [ ] Email list started
- [ ] Press contacts identified

### **Monitoring**
- [ ] Analytics installed
- [ ] Error tracking set up
- [ ] Uptime monitoring active
- [ ] Support email configured

---

## 🎉 YOU'RE READY TO LAUNCH!

**This document contains everything you need to build and launch Frequency Factory.**

Keep this document handy and check off items as you complete them.

**Questions?** Refer back to specific sections.

**Ready to start?** Begin with [Firebase Setup](#firebase-setup-guide).

---

**END OF MASTER BUILD DOCUMENT**
