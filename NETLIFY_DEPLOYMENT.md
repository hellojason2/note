# Deploying to Netlify

## ⚠️ Important Limitations

**Netlify is primarily for frontend apps.** Your full-stack application will face these challenges:

### Issues with Netlify:
- ❌ **Serverless functions have timeouts** (10 seconds on free tier, 26 seconds on paid)
- ❌ **Database connections are difficult** (each function call creates new connections)
- ❌ **Cold starts** (functions sleep when not in use, causing delays)
- ❌ **No persistent server** (Express server needs to restart for each request)
- ❌ **More complex setup** than platforms designed for full-stack apps

### Better Alternatives:
- ✅ **Railway** - Best for full-stack apps (recommended)
- ✅ **Render** - Great for Node.js + database apps
- ✅ **DigitalOcean App Platform** - Good balance of features
- ✅ **Fly.io** - Excellent for persistent servers

---

## If You Still Want to Use Netlify

Here's how to deploy (with limitations):

### Step 1: Install Netlify CLI (Optional)

```bash
npm install -g netlify-cli
```

### Step 2: Deploy via Netlify Website

1. **Go to [netlify.com](https://netlify.com)**
2. **Sign in with GitHub**
3. **Click "Add new site" → "Import an existing project"**
4. **Choose GitHub** and select your **"note"** repository
5. **Configure build settings:**
   - **Build command**: `pnpm install && pnpm build`
   - **Publish directory**: `client/dist`
   - **Functions directory**: `netlify/functions`

### Step 3: Add Environment Variables

In Netlify dashboard → Site settings → Environment variables:

```
DATABASE_URL=mysql://user:password@host:port/database
JWT_SECRET=your-secret-key
VITE_APP_ID=your-app-id
OAUTH_SERVER_URL=https://api.manus.im
VITE_OAUTH_PORTAL_URL=https://oauth.manus.im
VITE_APP_TITLE=Notes App
VITE_APP_LOGO=your-logo-url
NODE_VERSION=22
```

### Step 4: Install Required Dependencies

You'll need to add Netlify-specific packages. Run locally:

```bash
cd /home/ubuntu/notes-app
pnpm add -D @netlify/functions serverless-http
```

### Step 5: Deploy

- Click "Deploy site"
- Netlify will build and deploy
- You'll get a URL like `your-site.netlify.app`

### Step 6: Add Custom Domain

1. Go to **Domain settings** in Netlify
2. Click **"Add custom domain"**
3. Enter your domain (e.g., `notes.yourdomain.com`)
4. Netlify will provide DNS instructions
5. Add the CNAME record in your domain registrar
6. Netlify automatically provisions SSL certificate

---

## Known Issues with This Setup

### 1. Database Connection Pooling
Serverless functions create new database connections for each request, which can:
- Exhaust your database connection limit
- Cause slow response times
- Lead to connection errors

**Solution**: Use a connection pooling service like PlanetScale or Neon.

### 2. Function Timeouts
If a request takes longer than 10 seconds (free tier), it will fail.

**Solution**: Upgrade to Pro ($19/month) for 26-second timeout, or use a different platform.

### 3. Cold Starts
Functions "sleep" after inactivity, causing 1-3 second delays on first request.

**Solution**: Use Netlify's "Background Functions" or accept the delay.

### 4. OAuth Callback Issues
OAuth redirects might fail due to serverless function URLs.

**Solution**: Configure OAuth callback URL to match Netlify function endpoint.

---

## Recommended: Use Railway Instead

**Railway is purpose-built for apps like yours:**

### Why Railway is Better:

| Feature | Netlify | Railway |
|---------|---------|---------|
| **Persistent server** | ❌ No | ✅ Yes |
| **Database support** | ⚠️ Limited | ✅ Native |
| **No cold starts** | ❌ Has cold starts | ✅ Always on |
| **No timeouts** | ❌ 10-26s limit | ✅ No limit |
| **Setup complexity** | ⚠️ Complex | ✅ Simple |
| **Cost (free tier)** | ✅ Generous | ✅ $5 credit/month |

### Deploy to Railway in 5 Minutes:

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your "note" repository
5. Add environment variables
6. Deploy! (Railway auto-detects everything)
7. Add custom domain in settings

**That's it!** No serverless functions, no cold starts, no timeouts.

---

## My Recommendation

**Don't use Netlify for this app.** Use Railway, Render, or DigitalOcean App Platform instead.

Your app needs:
- Persistent database connections
- Long-running server process
- Real-time capabilities
- No function timeouts

All of these work better on platforms designed for full-stack apps.

---

## Still Want Netlify?

If you absolutely must use Netlify, you'll need to:

1. Refactor the database connection handling
2. Add connection pooling
3. Handle cold starts gracefully
4. Test thoroughly for timeout issues
5. Monitor function execution times
6. Potentially upgrade to Pro tier

**This is significantly more work than just using Railway.**

---

## Quick Comparison

### Netlify Deployment:
- ⏱️ Setup time: 2-3 hours (with refactoring)
- 💰 Cost: Free (with limitations) or $19/month
- 🔧 Maintenance: High (connection issues, timeouts)
- 📊 Performance: Variable (cold starts)

### Railway Deployment:
- ⏱️ Setup time: 5 minutes
- 💰 Cost: Free $5/month credit, then pay-as-you-go
- 🔧 Maintenance: Low (just works)
- 📊 Performance: Consistent (always on)

---

**Need help deciding or deploying?** Let me know which platform you'd like to use!

