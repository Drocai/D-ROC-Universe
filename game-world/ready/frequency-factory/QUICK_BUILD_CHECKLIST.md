# FREQUENCY FACTORY - QUICK BUILD CHECKLIST
**Use this for daily progress tracking**

---

## 🔥 CRITICAL PATH (Must Do First)

### ☐ FIREBASE SETUP (2 hours)
- [ ] Create Firebase project
- [ ] Enable Firestore Database
- [ ] Enable Anonymous Auth
- [ ] Copy config to HTML (line 20)
- [ ] Deploy security rules
- [ ] Test: Click "Clock In" button
- [ ] Verify user appears in Firestore

### ☐ STRIPE PAYMENTS (4 hours)
- [ ] Create Stripe account
- [ ] Create products ($5, $20, $50 submission fees)
- [ ] Get API keys (pk_test_ and sk_test_)
- [ ] Add Stripe.js to HTML
- [ ] Create Netlify function: create-checkout.js
- [ ] Create webhook handler: stripe-webhook.js
- [ ] Test payment flow
- [ ] Verify webhook receives events

### ☐ MUSIC SYSTEM (8 hours)
- [ ] Create Cloudflare R2 bucket
- [ ] Get R2 API credentials
- [ ] Add file input to submission form
- [ ] Create Netlify function: get-upload-url.js
- [ ] Test file upload
- [ ] Add audio player to HTML
- [ ] Test playback in browser

### ☐ ADMIN PANEL (6 hours)
- [ ] Create admin.html file
- [ ] Add Firebase Admin SDK
- [ ] Build pending submissions view
- [ ] Add approve/reject buttons
- [ ] Test moderation workflow

---

## 📋 SECONDARY FEATURES (Add After Core Works)

### ☐ EMAIL SYSTEM (4 hours)
- [ ] Set up SendGrid
- [ ] Create email templates
- [ ] Build Netlify function: send-email.js
- [ ] Test confirmation emails

### ☐ YOUTUBE STREAM (8 hours)
- [ ] Create YouTube channel
- [ ] Design channel art
- [ ] Install OBS Studio
- [ ] Configure browser source
- [ ] Design stream overlays
- [ ] Test stream quality
- [ ] Set up auto-start

### ☐ CONTENT MODERATION (3 hours)
- [ ] Add reCAPTCHA to forms
- [ ] Implement duplicate detection
- [ ] Add profanity filter
- [ ] Create abuse report button

### ☐ ANALYTICS (2 hours)
- [ ] Add Google Analytics 4
- [ ] Set up event tracking
- [ ] Create admin analytics view

### ☐ SEO (2 hours)
- [ ] Add meta tags
- [ ] Create sitemap.xml
- [ ] Add structured data
- [ ] Submit to Search Console

---

## 📄 LEGAL & BUSINESS (4 hours)

### ☐ LEGAL DOCS
- [ ] Terms of Service
- [ ] Privacy Policy
- [ ] Artist Agreement
- [ ] Refund Policy

### ☐ BUSINESS SETUP
- [ ] Register LLC (optional)
- [ ] Open business bank account
- [ ] Set up accounting (QuickBooks)

---

## 🚀 LAUNCH PREP (1 week)

### ☐ BETA TESTING
- [ ] Invite 10-20 beta testers
- [ ] Create feedback form
- [ ] Monitor for bugs
- [ ] Fix critical issues

### ☐ MARKETING
- [ ] Create social accounts
- [ ] Design promo materials
- [ ] Write launch announcement
- [ ] Create promo video

### ☐ GO LIVE
- [ ] Switch to live payment mode
- [ ] Enable 24/7 stream
- [ ] Publish announcement
- [ ] Monitor & support

---

## 📊 DAILY PROGRESS TRACKER

### Week 1: Foundation
```
Mon [ ] Firebase setup complete
Tue [ ] Payment testing done
Wed [ ] Music upload working
Thu [ ] Admin panel functional
Fri [ ] Bug fixes
Sat [ ] Integration testing
Sun [ ] Documentation
```

### Week 2: Polish
```
Mon [ ] Email system live
Tue [ ] Analytics integrated
Wed [ ] SEO optimized
Thu [ ] Legal docs posted
Fri [ ] Beta invites sent
Sat [ ] Feedback collection
Sun [ ] Bug fixes
```

### Week 3: Stream
```
Mon [ ] YouTube setup
Tue [ ] OBS configured
Wed [ ] Stream graphics done
Thu [ ] 24/7 system tested
Fri [ ] Final testing
Sat [ ] Soft launch prep
Sun [ ] Review checklist
```

### Week 4: Launch
```
Mon [ ] Final polish
Tue [ ] PUBLIC LAUNCH 🚀
Wed [ ] Monitor & support
Thu [ ] Fix issues
Fri [ ] Community engagement
Sat [ ] Iterate
Sun [ ] Plan next features
```

---

## ⚠️ BLOCKERS TO WATCH FOR

**Firebase:**
- ❌ Security rules not deployed → nothing works
- ❌ Wrong config values → auth fails

**Payments:**
- ❌ Webhook not verified → payments not recorded
- ❌ Test mode in production → no real money

**Music:**
- ❌ CORS not configured → uploads fail
- ❌ Files too large → performance issues

**Stream:**
- ❌ No fallback playlist → stream dies when queue empty
- ❌ OBS not auto-starting → stream goes down

---

## 🎯 MINIMUM VIABLE PRODUCT (MVP)

**To launch, you need:**
1. ✅ Firebase working
2. ✅ Payments working
3. ✅ Music upload/play working
4. ✅ Admin panel working
5. ✅ Terms & Privacy pages

**Everything else can be added post-launch!**

---

## 📞 QUICK REFERENCE

**Firebase Config Location:** Line 20 in frequency-factory.html
**Stripe Keys Location:** Netlify env variables
**R2 Bucket Name:** frequency-factory-music
**Admin URL:** /admin.html
**Main App URL:** /index.html or frequency-factory.html

---

## ✅ DAILY STANDUP QUESTIONS

**Every morning, ask yourself:**
1. What did I complete yesterday?
2. What am I working on today?
3. What's blocking me?
4. Am I on track for launch?

**Every evening, ask yourself:**
1. Did I check off today's tasks?
2. What surprised me?
3. What needs more time than expected?
4. What can I delegate or skip?

---

## 🏁 WHEN YOU'RE STUCK

**Stuck on Firebase?** → Check console for errors, verify config
**Stuck on Payments?** → Use Stripe test cards, check webhook logs
**Stuck on Music?** → Test with small file first, check CORS
**Stuck on Stream?** → Start simple: just browser source first

**Still stuck?** → Ask Claude for help with specific error messages

---

## 🎉 LAUNCH DAY CHECKLIST

**Morning of Launch:**
- [ ] Coffee/energy ready ☕
- [ ] All systems tested
- [ ] Switch Stripe to live mode
- [ ] Start YouTube stream
- [ ] Post announcement
- [ ] Monitor errors
- [ ] Celebrate! 🎊

---

**REMEMBER:** Done is better than perfect. Launch the MVP, then iterate!

**Current Date:** October 24, 2025  
**Target Launch:** November 24, 2025 (4 weeks)

**YOU GOT THIS!** 💪
