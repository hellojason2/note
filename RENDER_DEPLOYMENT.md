# Deploy to Render.com

This guide will help you deploy your notes app to Render.com with automatic deployments from GitHub.

## Prerequisites

- A Render.com account (free tier available)
- Your GitHub repository connected to Render

## Deployment Steps

### Option 1: Using Blueprint (Recommended - Automatic)

1. **Go to Render Dashboard**
   - Visit [render.com](https://render.com)
   - Log in to your account

2. **Create New Blueprint**
   - Click "New +" in the top right
   - Select "Blueprint"

3. **Connect GitHub Repository**
   - Select your GitHub account
   - Choose the `hellojason2/note` repository
   - Click "Connect"

4. **Render Auto-Configures**
   - Render will read the `render.yaml` file
   - It will create:
     - A web service for your app
     - A PostgreSQL database (free tier)
   - Click "Apply" to create the services

5. **Set Required Environment Variables**
   
   After blueprint creation, you need to add these secret values:
   
   - Go to your web service → "Environment"
   - Add these variables (they're marked as `sync: false` in the blueprint):
   
   ```
   DATABASE_URL=<will be auto-filled by Render from the database>
   VITE_APP_ID=<your Manus OAuth app ID, or leave empty>
   OWNER_OPEN_ID=<optional>
   OWNER_NAME=<optional>
   BUILT_IN_FORGE_API_KEY=<optional>
   ```

6. **Deploy**
   - Render will automatically build and deploy
   - Wait 5-10 minutes for the first deployment
   - You'll get a URL like: `https://notes-app.onrender.com`

### Option 2: Manual Setup

If you prefer manual setup:

1. **Create Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select `hellojason2/note`

2. **Configure Build Settings**
   - **Name**: notes-app
   - **Region**: Oregon (or closest to you)
   - **Branch**: main
   - **Build Command**: `pnpm install && pnpm build`
   - **Start Command**: `pnpm start`

3. **Add Environment Variables**
   
   Add all the variables from the blueprint manually:
   
   ```
   NODE_ENV=production
   JWT_SECRET=<auto-generate or create your own>
   OAUTH_SERVER_URL=https://api.manus.im
   VITE_OAUTH_PORTAL_URL=https://oauth.manus.im
   VITE_APP_TITLE=Notes App
   BUILT_IN_FORGE_API_URL=https://api.manus.im
   ```

4. **Create Database**
   - Click "New +" → "PostgreSQL"
   - Name: notes-db
   - Plan: Free
   - After creation, copy the "Internal Database URL"
   - Add it to your web service as `DATABASE_URL`

5. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy automatically

## Post-Deployment

### Add Custom Domain

1. Go to your web service → "Settings"
2. Scroll to "Custom Domains"
3. Click "Add Custom Domain"
4. Enter your domain (e.g., `note.jsralgo.com`)
5. Add the CNAME record to your DNS:
   - Type: CNAME
   - Name: note (or your subdomain)
   - Value: `<your-app>.onrender.com`

### Enable Auto-Deploy

Auto-deploy is enabled by default. Every push to the `main` branch on GitHub will trigger a new deployment.

## Troubleshooting

### Build Fails

- Check the build logs in Render dashboard
- Make sure all environment variables are set
- Verify `pnpm` is being used (not npm)

### Database Connection Issues

- Make sure `DATABASE_URL` is set correctly
- Use the "Internal Database URL" from Render's PostgreSQL service
- Format: `postgresql://user:password@host:port/database`

### App Crashes

- Check the logs in Render dashboard
- Verify all required environment variables are present
- Make sure the start command is correct: `pnpm start`

## Notes

- **Free tier limitations**:
  - Service spins down after 15 minutes of inactivity
  - First request after spin-down takes 30-60 seconds
  - 750 hours/month of runtime
  
- **Database**:
  - Render uses PostgreSQL (not MySQL)
  - You may need to adjust database queries if using MySQL-specific syntax
  - Free tier: 90 days, then requires paid plan

## Support

If you encounter issues:
- Check Render's documentation: https://render.com/docs
- Review deployment logs in the Render dashboard
- Verify environment variables are correctly set

