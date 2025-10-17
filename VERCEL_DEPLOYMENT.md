# Deploying to Vercel

## Important Note

This is a **full-stack application** with both frontend (React) and backend (Express + tRPC). Vercel is primarily designed for frontend applications and serverless functions.

## Current Issue

Your deployment at https://note-seven-beige.vercel.app/ is showing source code because Vercel needs proper configuration for full-stack apps.

## Recommended Deployment Options

### Option 1: Railway (Recommended for Full-Stack)

Railway is better suited for full-stack applications with databases:

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `note` repository
5. Railway will auto-detect the Node.js app
6. Add environment variables:
   - `DATABASE_URL` - Your MySQL/TiDB connection string
   - `JWT_SECRET` - A random secret key
   - `VITE_APP_ID` - Your OAuth app ID
   - `OAUTH_SERVER_URL` - https://api.manus.im
   - `VITE_OAUTH_PORTAL_URL` - https://oauth.manus.im
   - All other environment variables from your `.env` file
7. Deploy!
8. Railway will give you a URL like `your-app.railway.app`
9. Add your custom domain in Railway settings

### Option 2: Render

Similar to Railway:

1. Go to [render.com](https://render.com)
2. Sign in with GitHub
3. Click "New" → "Web Service"
4. Connect your `note` repository
5. Configure:
   - **Build Command**: `pnpm install && pnpm build`
   - **Start Command**: `pnpm start`
6. Add environment variables
7. Deploy!

### Option 3: DigitalOcean App Platform

1. Go to [digitalocean.com](https://www.digitalocean.com/products/app-platform)
2. Create a new app from GitHub
3. Select your repository
4. Configure build and run commands
5. Add environment variables
6. Deploy!

### Option 4: Self-Host on VPS

For full control:

1. Get a VPS (DigitalOcean Droplet, AWS EC2, Linode, etc.)
2. SSH into your server
3. Install Node.js, pnpm, and MySQL
4. Clone your repository
5. Set up environment variables
6. Run `pnpm install && pnpm build`
7. Use PM2 to keep the app running: `pm2 start dist/index.js`
8. Set up Nginx as a reverse proxy
9. Configure SSL with Let's Encrypt

## Why Not Vercel?

Vercel is optimized for:
- Static sites
- Next.js applications
- Serverless functions

Your app has:
- A persistent Express server
- Database connections
- WebSocket support (if needed)
- Long-running processes

While it's possible to deploy to Vercel with serverless functions, it requires significant refactoring.

## Environment Variables You'll Need

Make sure to set these in your deployment platform:

```env
# Database
DATABASE_URL=mysql://user:password@host:port/database

# Authentication
JWT_SECRET=your-random-secret-key-here
VITE_APP_ID=your-manus-app-id
OAUTH_SERVER_URL=https://api.manus.im
VITE_OAUTH_PORTAL_URL=https://oauth.manus.im

# App Configuration
VITE_APP_TITLE=Notes App
VITE_APP_LOGO=https://your-logo-url.com/logo.png

# Manus Built-in APIs (if you have them)
BUILT_IN_FORGE_API_URL=your-api-url
BUILT_IN_FORGE_API_KEY=your-api-key

# Owner Info (Optional)
OWNER_OPEN_ID=your-owner-id
OWNER_NAME=Your Name
```

## Connecting Your Custom Domain

After deployment:

1. Go to your deployment platform's domain settings
2. Add your custom domain (e.g., `notes.yourdomain.com`)
3. The platform will give you DNS instructions
4. Go to your domain registrar (GoDaddy, Namecheap, Cloudflare, etc.)
5. Add a CNAME record:
   - **Name**: `notes` (or your subdomain)
   - **Value**: The URL provided by your deployment platform
6. Wait for DNS propagation (5 minutes to 48 hours)
7. Your app will be live at your custom domain!

## Quick Start: Railway Deployment

**Easiest option for your full-stack app:**

1. Delete the current Vercel deployment
2. Go to Railway.app
3. Connect GitHub
4. Deploy your `note` repository
5. Add environment variables
6. Get your production URL
7. Add custom domain

**Need help?** Let me know which platform you'd like to use and I can guide you through it!

