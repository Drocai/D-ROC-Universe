# FREQUENCY FACTORY - DEPLOYMENT GUIDE
## From Code to Live in 15 Minutes

**Last Updated:** October 24, 2025  
**Deployment Platform:** Netlify (Free Tier)

---

## 📋 PRE-DEPLOYMENT CHECKLIST

**Before you start, make sure you have:**
- [x] Firebase project created
- [x] Firebase config values
- [x] All platform code files
- [x] Netlify account (free)
- [x] Domain name (optional)

---

## 🚀 DEPLOYMENT STEPS

### **STEP 1: Prepare Your Files (5 minutes)**

**File Structure:**
```
frequency-factory/
├── index.html
├── styles.css
├── app.js
├── firebase-config.js
├── assets/
│   ├── images/
│   └── icons/
└── netlify.toml
```

**Insert Firebase Config:**

1. Open `firebase-config.js`
2. Find the config placeholder:
```javascript
const firebaseConfig = {
  apiKey: "YOUR_API_KEY_HERE",
  authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT_ID.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
};
```
3. Replace with your actual Firebase config
4. Save the file

---

### **STEP 2: Create Netlify Account (2 minutes)**

1. Go to: https://netlify.com
2. Click "Sign Up"
3. Choose "Sign up with GitHub" (recommended)
   - OR use email/password
4. Verify your email
5. You're in!

---

### **STEP 3: Deploy to Netlify (3 minutes)**

**Option A: Drag & Drop (Easiest)**

1. Open Netlify dashboard
2. Find the "Want to deploy a new site without connecting to Git?" section
3. **Drag your entire `frequency-factory/` folder** onto the upload area
4. Wait for deployment (usually 30-60 seconds)
5. BOOM - you're live! 🎉

**Option B: Git Deploy (Recommended for updates)**

1. Initialize Git in your project folder:
```bash
cd frequency-factory
git init
git add .
git commit -m "Initial commit"
```

2. Push to GitHub:
```bash
git remote add origin https://github.com/YOUR_USERNAME/frequency-factory.git
git push -u origin main
```

3. In Netlify:
   - Click "New site from Git"
   - Choose GitHub
   - Select your repository
   - Deploy settings:
     - Build command: (leave empty)
     - Publish directory: `/`
   - Click "Deploy site"

---

### **STEP 4: Configure Your Site (5 minutes)**

**Your site is now live at:** `random-name-12345.netlify.app`

**Set a Custom Subdomain:**
1. Click "Site settings"
2. Click "Change site name"
3. Enter: `frequency-factory` (or whatever you want)
4. Now your site is: `frequency-factory.netlify.app`

**Add Custom Domain (Optional):**
1. Buy domain from Namecheap, Google Domains, etc.
2. In Netlify → Site settings → Domain management
3. Click "Add custom domain"
4. Enter your domain: `frequencyfactory.io`
5. Follow DNS setup instructions
6. Wait for DNS propagation (5-60 minutes)
7. SSL certificate auto-generates (free!)

---

### **STEP 5: Enable HTTPS (Automatic)**

Netlify automatically provides FREE SSL certificates:
- HTTP → HTTPS redirect (automatic)
- Certificate renewal (automatic)
- No configuration needed!

Your site is now secure: `https://frequency-factory.netlify.app` 🔒

---

### **STEP 6: Set Environment Variables (If Needed)**

If you have any secret keys (not Firebase config):

1. Site settings → Build & deploy
2. Environment variables
3. Click "Add variable"
4. Enter key/value pairs
5. Save

**Note:** Firebase config is public-facing, so it goes directly in your code. API keys are meant to be restricted by Firebase security rules.

---

## 🔧 NETLIFY CONFIGURATION FILE

**Create `netlify.toml` in your project root:**

```toml
[build]
  publish = "/"
  
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
  
[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"

[build.environment]
  NODE_VERSION = "18"
```

This enables:
- Single-page app routing
- Security headers
- Proper redirects

---

## 🔄 UPDATING YOUR SITE

**For Drag & Drop Deploys:**
1. Make code changes locally
2. Drag updated folder to Netlify deploys tab
3. New version goes live immediately

**For Git Deploys:**
1. Make code changes locally
2. Commit changes:
```bash
git add .
git commit -m "Update feature X"
git push
```
3. Netlify auto-deploys in ~30 seconds

---

## 📊 MONITORING & ANALYTICS

**Netlify Dashboard Shows:**
- Deploy history
- Build logs
- Traffic stats
- Bandwidth usage
- Form submissions (if using Netlify forms)

**Add Google Analytics:**
1. Create GA4 property
2. Add tracking code to `index.html`:
```html
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```
3. Redeploy
4. View analytics in GA dashboard

---

## 🚨 TROUBLESHOOTING

### **Problem: Site won't load**

**Check:**
- Are all files uploaded?
- Is `index.html` in the root directory?
- Check browser console for errors
- Check Netlify deploy log

**Solution:**
- Re-upload files
- Check file paths (case-sensitive!)
- Clear browser cache

---

### **Problem: Firebase not connecting**

**Check:**
- Is Firebase config correct?
- Are Firebase services enabled (Auth, Firestore)?
- Check browser console for Firebase errors
- Verify Firebase security rules

**Solution:**
- Double-check config values
- Enable required Firebase services
- Update security rules
- Check Firebase project settings

---

### **Problem: 404 errors on page refresh**

**Cause:** Single-page app routing not configured

**Solution:**
- Add `netlify.toml` with redirect rules (see above)
- Redeploy

---

### **Problem: Slow load times**

**Optimizations:**
- Enable Netlify's asset optimization (automatic)
- Compress images before uploading
- Minify CSS/JS
- Use CDN for large assets
- Lazy load images

---

### **Problem: Build fails**

**Check:**
- Build command correct?
- All dependencies installed?
- Node version compatible?

**Solution:**
- Check deploy log for errors
- Update `netlify.toml` with correct settings
- Contact Netlify support if needed

---

## 💰 PRICING & LIMITS

**Netlify Free Tier Includes:**
- ✅ 100 GB bandwidth/month
- ✅ 300 build minutes/month
- ✅ Unlimited sites
- ✅ Automatic HTTPS
- ✅ Form submissions (100/month)
- ✅ Serverless functions (125k requests/month)

**This is MORE than enough for initial launch.**

**When to Upgrade:**
- Traffic > 100 GB/month
- Need team collaboration
- Want advanced features (A/B testing, etc.)

**Pro Plan:** $19/month
**Business Plan:** $99/month

---

## 🎯 POST-DEPLOYMENT CHECKLIST

After deploying, verify everything works:

- [ ] Site loads at custom URL
- [ ] HTTPS is active (green lock)
- [ ] User can create account
- [ ] User can login
- [ ] Tracks load properly
- [ ] Rating system works
- [ ] Tokens are awarded
- [ ] Leaderboard updates
- [ ] Profile loads
- [ ] Mobile responsive
- [ ] No console errors
- [ ] Firebase connected
- [ ] All links work
- [ ] Images load
- [ ] Analytics tracking

---

## 🔗 CONNECTING CUSTOM DOMAIN

**Step-by-Step:**

1. **Buy Domain:**
   - Namecheap (recommended): ~$10/year
   - Google Domains: ~$12/year
   - GoDaddy: ~$15/year

2. **Add to Netlify:**
   - Site settings → Domain management
   - Add custom domain
   - Enter: `frequencyfactory.io`

3. **Configure DNS:**
   - Go to your domain registrar
   - Find DNS settings
   - Add these records:
   
   **For apex domain (frequencyfactory.io):**
   - Type: A
   - Name: @
   - Value: 75.2.60.5
   
   **For www subdomain:**
   - Type: CNAME
   - Name: www
   - Value: your-site.netlify.app

4. **Wait for Propagation:**
   - Usually 5-30 minutes
   - Up to 48 hours max
   - Check status at: https://dnschecker.org

5. **Verify SSL:**
   - Netlify auto-generates certificate
   - Should show green lock in browser
   - If not, wait 10 more minutes

---

## 🎨 BONUS: CUSTOM 404 PAGE

**Create `404.html`:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - Page Not Found | Frequency Factory</title>
    <style>
        body {
            font-family: sans-serif;
            background: #1F2937;
            color: #F3F4F6;
            text-align: center;
            padding: 50px;
        }
        h1 { font-size: 72px; margin: 0; }
        p { font-size: 24px; }
        a { color: #10B981; text-decoration: none; }
    </style>
</head>
<body>
    <h1>404</h1>
    <p>Track not found in the Factory.</p>
    <a href="/">← Back to the Factory Floor</a>
</body>
</html>
```

Upload this with your other files - Netlify uses it automatically!

---

## 📈 PERFORMANCE OPTIMIZATION

**After Launch:**

1. **Enable Netlify Features:**
   - Asset optimization (automatic)
   - Pretty URLs (automatic)
   - Post processing (automatic)

2. **Optimize Images:**
   - Use WebP format
   - Compress before upload
   - Use lazy loading

3. **Minify Code:**
   - CSS minification
   - JS minification
   - Remove comments

4. **Use CDN:**
   - Netlify provides global CDN (automatic)
   - Assets served from closest edge location

5. **Monitor Performance:**
   - Google PageSpeed Insights
   - GTmetrix
   - Lighthouse audit

---

## ✅ DEPLOYMENT COMPLETE!

**Your Frequency Factory is now LIVE! 🎉**

**What's Next:**
1. Test everything thoroughly
2. Share link with beta testers
3. Start onboarding users
4. Monitor Firebase usage
5. Collect feedback
6. Iterate and improve

**Your live site:** `https://frequency-factory.netlify.app`

---

**TIME TO MAKE MUSIC HISTORY! 🏭🎵**
