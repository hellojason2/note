# How to Push This Project to GitHub

Follow these steps to push your notes app to GitHub:

## Step 1: Create a GitHub Repository

1. Go to [GitHub](https://github.com) and log in
2. Click the **"+"** icon in the top right corner
3. Select **"New repository"**
4. Fill in the details:
   - **Repository name**: `notes-app` (or your preferred name)
   - **Description**: "A notes-taking app with unique URLs and password protection"
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
5. Click **"Create repository"**

## Step 2: Connect Your Local Project to GitHub

After creating the repository, GitHub will show you commands. Use these commands in your terminal:

### Option A: If you see the "quick setup" page

Copy the repository URL (it looks like `https://github.com/yourusername/notes-app.git`)

Then run these commands in your terminal:

```bash
cd /home/ubuntu/notes-app

# Remove the existing remote
git remote remove origin

# Add your GitHub repository as the remote
git remote add origin https://github.com/YOUR_USERNAME/notes-app.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Option B: Using SSH (if you have SSH keys set up)

```bash
cd /home/ubuntu/notes-app

# Remove the existing remote
git remote remove origin

# Add your GitHub repository as the remote (SSH)
git remote add origin git@github.com:YOUR_USERNAME/notes-app.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Authenticate

When you push for the first time, GitHub will ask for authentication:

### Using HTTPS:
- **Username**: Your GitHub username
- **Password**: Use a **Personal Access Token** (not your GitHub password)
  
To create a Personal Access Token:
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name like "Notes App Deploy"
4. Select scopes: `repo` (full control of private repositories)
5. Click "Generate token"
6. Copy the token and use it as your password

### Using SSH:
- No password needed if you've set up SSH keys
- [Guide to set up SSH keys](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)

## Step 4: Verify the Push

1. Go to your GitHub repository page
2. You should see all your files including:
   - `README.md`
   - `client/` folder
   - `server/` folder
   - `package.json`
   - etc.

## Step 5: Future Updates

After the initial push, to update your GitHub repository with new changes:

```bash
cd /home/ubuntu/notes-app

# Stage all changes
git add -A

# Commit with a message
git commit -m "Your commit message describing the changes"

# Push to GitHub
git push
```

## Common Issues

### Issue: "Authentication failed"
- **Solution**: Make sure you're using a Personal Access Token, not your password

### Issue: "Permission denied (publickey)"
- **Solution**: Set up SSH keys or use HTTPS instead

### Issue: "Repository not found"
- **Solution**: Check that you've created the repository on GitHub and the URL is correct

## Next Steps: Deploy to Vercel

Once your code is on GitHub:

1. Go to [Vercel](https://vercel.com)
2. Sign in with GitHub
3. Click "Import Project"
4. Select your `notes-app` repository
5. Configure environment variables (copy from your `.env` file)
6. Click "Deploy"
7. Once deployed, add your custom domain in Vercel settings

---

**Need help?** Check the main README.md for more information about the project structure and deployment options.

