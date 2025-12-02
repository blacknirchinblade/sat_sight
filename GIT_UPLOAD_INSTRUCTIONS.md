# GitHub Upload Instructions for Sat-Sight

## 📋 Pre-Upload Checklist

✅ README.md created with all details
✅ .env.example created (template for environment variables)
✅ .gitignore configured (excludes data/, models/, docs/)
✅ Code cleaned (no unnecessary prints, emojis removed from backend)
✅ Placeholder directories created (docs/images, docs/videos)

---

## 🚀 Step-by-Step Git Upload Instructions

### Step 1: Navigate to Project Directory

```bash
cd /home/ganesh/GenAi_Project/sat_sight
```

### Step 2: Run Cleanup Script (Optional but Recommended)

```bash
# This will remove test files, backups, and prepare for GitHub
./prepare_github.sh
```

### Step 3: Initialize Git Repository

```bash
# Initialize git in the current directory
git init

# Check git status to see what will be committed
git status
```

### Step 4: Configure Git User (First Time Only)

```bash
# Set your GitHub username
git config --global user.name "blacknirchinblade"

# Set your email (use GitHub no-reply email if you want privacy)
git config --global user.email "ganeshnaik214@gmail.com"

# Verify configuration
git config --list
```

### Step 5: Add Files to Git

```bash
# Add all files (respects .gitignore)
git add .

# Review what will be committed
git status

# If you see any files you don't want to commit, add them to .gitignore:
# echo "filename_or_pattern" >> .gitignore
# git reset HEAD filename_or_pattern
```

### Step 6: Create Initial Commit

```bash
git commit -m "Initial commit: Sat-Sight multi-agent satellite imagery analysis system

- 13 specialized AI agents for satellite imagery analysis
- LangGraph orchestration with state management
- FAISS + ChromaDB vector search (20K+ images)
- 3-layer memory system (short-term, long-term, episodic)
- Streamlit web interface with multi-session chat
- Support for Groq API and local LLMs
- Comprehensive documentation and setup guides

Developed at Indian Institute of Science (IISc), Bangalore"
```

### Step 7: Add Remote Repository

```bash
# Add your GitHub repository as remote origin
git remote add origin https://github.com/blacknirchinblade/sat_sight.git

# Verify remote was added correctly
git remote -v
```

### Step 8: Create Main Branch (if not already created)

```bash
# Rename current branch to 'main' (modern standard)
git branch -M main
```

### Step 9: Push to GitHub

```bash
# Push to GitHub (first time requires -u flag)
git push -u origin main

# You may be prompted for GitHub authentication:
# - Username: blacknirchinblade
# - Password: Use Personal Access Token (PAT), NOT your GitHub password
```

---

## 🔑 GitHub Authentication Setup

### Option 1: Using Personal Access Token (Recommended)

1. **Generate PAT on GitHub:**
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"
   - Select scopes: `repo` (all sub-options)
   - Set expiration (recommend: 90 days or No expiration)
   - Click "Generate token"
   - **COPY THE TOKEN IMMEDIATELY** (you won't see it again!)

2. **Use PAT when pushing:**
   ```bash
   git push -u origin main
   # Username: blacknirchinblade
   # Password: paste_your_personal_access_token_here
   ```

3. **Save credentials (optional):**
   ```bash
   # Cache credentials for 1 hour
   git config --global credential.helper 'cache --timeout=3600'
   
   # OR store permanently (less secure but convenient)
   git config --global credential.helper store
   ```

### Option 2: Using SSH Keys

1. **Generate SSH key:**
   ```bash
   ssh-keygen -t ed25519 -C "ganeshnaik214@gmail.com"
   # Press Enter to accept default location
   # Enter passphrase (optional but recommended)
   ```

2. **Add SSH key to GitHub:**
   ```bash
   # Copy public key to clipboard
   cat ~/.ssh/id_ed25519.pub
   
   # Then add it on GitHub:
   # Settings → SSH and GPG keys → New SSH key
   ```

3. **Change remote URL to SSH:**
   ```bash
   git remote set-url origin git@github.com:blacknirchinblade/sat_sight.git
   git push -u origin main
   ```

---

## 📝 After First Push

### Verify Upload

1. Visit: https://github.com/blacknirchinblade/sat_sight
2. Check that all files are present
3. Verify README.md displays correctly

### Add Project Images and Videos

```bash
# Add your banner image
cp /path/to/your/banner.png docs/images/banner.png

# Add your demo video
cp /path/to/your/demo.mp4 docs/videos/demo.mp4

# Commit and push
git add docs/images/banner.png docs/videos/demo.mp4
git commit -m "Add project banner and demo video"
git push
```

### Set Repository Description

On GitHub repository page:
1. Click "About" (gear icon)
2. Add description: "Multi-agent satellite imagery analysis system with LangGraph orchestration"
3. Add website: http://10.32.38.102:8501
4. Add topics: `satellite-imagery`, `multi-agent`, `langraph`, `ai`, `machine-learning`, `clip`, `faiss`

### Create Releases

```bash
# Create a tag for version 1.0.0
git tag -a v1.0.0 -m "Initial release: Sat-Sight v1.0.0"
git push origin v1.0.0

# Then create release on GitHub:
# Releases → Draft a new release → Choose tag v1.0.0
```

---

## 🔄 Future Updates

When you make changes and want to push updates:

```bash
# Check status
git status

# Add specific files
git add filename1.py filename2.py

# Or add all changed files
git add .

# Commit with descriptive message
git commit -m "Brief description of changes"

# Push to GitHub
git push

# If you get "rejected" error, pull first:
git pull origin main --rebase
git push
```

---

## 🚨 Troubleshooting

### Issue: "Repository not found"

**Solution:**
```bash
# Verify remote URL
git remote -v

# Update if wrong
git remote set-url origin https://github.com/blacknirchinblade/sat_sight.git
```

### Issue: "Authentication failed"

**Solution:**
- Use Personal Access Token, NOT password
- Generate new token if expired: https://github.com/settings/tokens

### Issue: "Large files rejected"

**Solution:**
```bash
# Remove large files from git
git rm --cached path/to/large/file

# Add to .gitignore
echo "path/to/large/file" >> .gitignore

# Commit and try again
git commit -m "Remove large files"
git push
```

### Issue: Files that should be ignored are being tracked

**Solution:**
```bash
# Remove from git but keep locally
git rm -r --cached data/
git rm -r --cached models/
git rm -r --cached docs/*.md

# Commit changes
git commit -m "Remove ignored files from tracking"
git push
```

---

## 📊 Repository Settings Recommendations

### Enable GitHub Pages (for documentation)
1. Settings → Pages
2. Source: Deploy from branch → main → /docs
3. Your docs will be at: https://blacknirchinblade.github.io/sat_sight/

### Add LICENSE
```bash
# Create MIT License file
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2025 Ganesh Islavath, IISc Bangalore

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

git add LICENSE
git commit -m "Add MIT License"
git push
```

### Protect Main Branch
1. Settings → Branches → Add rule
2. Branch name pattern: `main`
3. Enable: "Require pull request before merging"

---

## ✅ Final Checklist Before Push

- [ ] README.md is complete and professional
- [ ] .env.example created (no actual API keys)
- [ ] .gitignore properly configured
- [ ] No sensitive data (API keys, passwords) in code
- [ ] No large files (models, datasets) in repository
- [ ] All code tested and working
- [ ] Commit messages are descriptive
- [ ] GitHub username and email configured
- [ ] Personal Access Token or SSH key ready

---

## 🎯 Quick Command Reference

```bash
# One-time setup
git init
git config --global user.name "blacknirchinblade"
git config --global user.email "ganeshnaik214@gmail.com"
git remote add origin https://github.com/blacknirchinblade/sat_sight.git

# Initial push
git add .
git commit -m "Initial commit"
git branch -M main
git push -u origin main

# Regular updates
git add .
git commit -m "Description of changes"
git push
```

---

**Your Repository Information:**
- **Repository URL**: https://github.com/blacknirchinblade/sat_sight
- **Username**: blacknirchinblade
- **Email**: ganeshnaik214@gmail.com
- **Clone Command**: `git clone https://github.com/blacknirchinblade/sat_sight.git`

**Good luck with your upload! 🚀**
