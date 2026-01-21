# Deployment Guide

This guide covers deploying Vibe Rated to various platforms.

## Prerequisites

Before deploying, ensure you have:
1. ✅ Supabase project created and schema deployed
2. ✅ Environment variables ready
3. ✅ Code pushed to GitHub repository
4. ✅ Production build tested locally (`npm run build`)

## Vercel Deployment (Recommended)

Vercel provides the best experience for React + Vite applications.

### Method 1: One-Click Deploy

1. Click the "Deploy with Vercel" button in README
2. Sign in with GitHub
3. Select your repository
4. Configure project:
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add environment variables:
   ```
   VITE_SUPABASE_URL=your_supabase_url
   VITE_SUPABASE_ANON_KEY=your_anon_key
   VITE_ENABLE_REAL_SENSORS=true
   ```
6. Click "Deploy"
7. Wait 2-3 minutes for deployment
8. Visit your live site!

### Method 2: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
cd vibe-rated-repo
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? vibe-rated (or custom)
# - Directory? ./
# - Override settings? No

# Add environment variables
vercel env add VITE_SUPABASE_URL
vercel env add VITE_SUPABASE_ANON_KEY

# Deploy to production
vercel --prod
```

### Vercel Configuration

Create `vercel.json` (optional):

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/sw.js",
      "headers": [
        {
          "key": "Service-Worker-Allowed",
          "value": "/"
        }
      ]
    }
  ]
}
```

## Netlify Deployment
### Method 1: Netlify UI

1. Go to [app.netlify.com](https://app.netlify.com)
2. Click "Add new site" > "Import an existing project"
3. Connect to GitHub and select repository
4. Configure build settings:
   - **Build command**: `npm run build`
   - **Publish directory**: `dist`
5. Add environment variables in Site settings > Environment variables
6. Click "Deploy site"

### Method 2: Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Initialize
cd vibe-rated-repo
netlify init

# Deploy
netlify deploy --prod
```

### Netlify Configuration

Create `netlify.toml`:

```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/sw.js"
  [headers.values]
    Service-Worker-Allowed = "/"
```

## Cloudflare Pages

1. Go to [dash.cloudflare.com](https://dash.cloudflare.com)
2. Navigate to Pages
3. Click "Create a project"
4. Connect to GitHub repository
5. Configure build:
   - **Build command**: `npm run build`
   - **Build output directory**: `dist`
6. Add environment variables
7. Click "Save and Deploy"

## Custom Server (VPS/Docker)

### Using Docker

Create `Dockerfile`:

```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Create `nginx.conf`:

```nginx
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /sw.js {
        add_header Service-Worker-Allowed /;
        add_header Cache-Control "no-cache";
    }

    gzip on;
    gzip_types text/css application/javascript application/json;
}
```

Build and run:

```bash
docker build -t vibe-rated .
docker run -p 80:80 vibe-rated
```

### Using PM2 (Node.js)
```bash
# Install PM2
npm install -g pm2

# Build the app
npm run build

# Serve with PM2
pm2 serve dist 3000 --name vibe-rated --spa

# Save PM2 config
pm2 save

# Setup startup script
pm2 startup
```

## Environment Variables

### Required Variables

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

### Optional Variables

```env
VITE_APP_NAME=Vibe Rated
VITE_APP_VERSION=2.0.0
VITE_APP_ENV=production
VITE_ENABLE_REAL_SENSORS=true
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_DEBUG=false
VITE_MAP_TILE_URL=https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png
VITE_MAP_DEFAULT_ZOOM=13
```

## Post-Deployment Checklist

After deploying, verify:

- [ ] App loads correctly
- [ ] PWA manifest is accessible
- [ ] Service worker registers
- [ ] Environment variables are set
- [ ] Supabase connection works
- [ ] Authentication flow works
- [ ] Measurements can be saved
- [ ] Map loads properly
- [ ] Icons and images load
- [ ] Mobile responsiveness
- [ ] PWA installation works
- [ ] Offline mode functions

## Performance Optimization

### Enable Compression

Ensure your hosting platform enables:
- Gzip/Brotli compression
- HTTP/2
- CDN caching

### Custom Domain

1. Add custom domain in platform settings
2. Configure DNS:
   ```
   Type: A or CNAME
   Name: @ or www
   Value: [provided by platform]
   ```
3. Enable HTTPS/SSL (usually automatic)

### Analytics Integration

Add analytics to `index.html`:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_ID');
</script>
```

## Monitoring
### Recommended Tools

- **Vercel Analytics**: Built-in performance monitoring
- **Sentry**: Error tracking
- **LogRocket**: Session replay
- **Supabase Dashboard**: Database and API monitoring

### Health Checks

Create monitoring endpoints:

```javascript
// src/api/health.js
export default function handler(req, res) {
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: process.env.VITE_APP_VERSION
  });
}
```

## Troubleshooting

### Build Fails

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Environment Variables Not Working

- Ensure variables start with `VITE_`
- Restart dev server after changes
- Check platform-specific variable syntax

### Service Worker Issues

- Clear browser cache
- Check HTTPS is enabled
- Verify `sw.js` is accessible
- Check Service-Worker-Allowed header

### Supabase Connection Fails

- Verify URL and key are correct
- Check Supabase project is active
- Ensure RLS policies are configured
- Check network/CORS settings

## Rollback

If deployment fails:

### Vercel
```bash
vercel rollback
```

### Netlify
```bash
netlify rollback
```

### Git
```bash
git revert HEAD
git push origin main
```

## Continuous Deployment

Both Vercel and Netlify automatically deploy when you push to GitHub:

```bash
git add .
git commit -m "Update feature"
git push origin main
# Deployment starts automatically

```

## Security

### Production Checklist

- [ ] Environment variables are secure
- [ ] Supabase RLS policies enabled
- [ ] HTTPS enforced
- [ ] CORS configured properly
- [ ] API keys not exposed in client
- [ ] Error messages don't leak sensitive data
- [ ] Rate limiting configured
- [ ] Security headers enabled

### Recommended Headers

```
Content-Security-Policy: default-src 'self'
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=*, microphone=*, accelerometer=*
```

## Support

For deployment issues:
- Check platform status pages
- Review platform documentation
- Contact platform support
- Open GitHub issue

---

**Happy Deploying! 🚀**