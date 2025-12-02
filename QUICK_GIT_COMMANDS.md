# 🚀 Git Upload - Quick Command Reference

## COPY AND PASTE THESE COMMANDS:

```bash
# 1. Navigate to project directory
cd /home/ganesh/GenAi_Project/sat_sight

# 2. Initialize Git repository
git init

# 3. Configure Git (first time only)
git config --global user.name "blacknirchinblade"
git config --global user.email "ganeshnaik214@gmail.com"

# 4. Add all files (respects .gitignore)
git add .

# 5. Create initial commit
git commit -m "Initial commit: Sat-Sight multi-agent satellite imagery analysis system

- 13 specialized AI agents for satellite imagery analysis
- LangGraph orchestration with state management
- FAISS + ChromaDB vector search (20K+ images)
- 3-layer memory system (short-term, long-term, episodic)
- Streamlit web interface with multi-session chat
- Support for Groq API and local LLMs
- Comprehensive documentation and setup guides

Developed at Indian Institute of Science (IISc), Bangalore"

# 6. Rename branch to 'main'
git branch -M main

# 7. Add remote repository
git remote add origin https://github.com/blacknirchinblade/sat_sight.git

# 8. Push to GitHub
git push -u origin main
```

## AUTHENTICATION:

**Username:** blacknirchinblade  
**Password:** [Use Personal Access Token - NOT your GitHub password]

### Generate Personal Access Token:
1. Visit: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name it: "Sat-Sight Upload"
4. Select: ✅ repo (all sub-options)
5. Click "Generate token"
6. COPY THE TOKEN (you won't see it again!)
7. Use this token as your password when pushing

---

## TROUBLESHOOTING:

### If push fails with "authentication failed":
```bash
# Make sure you're using PAT, not password
# Generate new token at: https://github.com/settings/tokens
```

### If push fails with "rejected":
```bash
# Pull first, then push
git pull origin main --rebase
git push
```

### If large files are rejected:
```bash
# Check file sizes
du -sh data/ models/ docs/

# These should already be in .gitignore
# If not, add them:
echo "data/" >> .gitignore
echo "models/" >> .gitignore
git add .gitignore
git commit -m "Update .gitignore"
git push
```

---

## AFTER SUCCESSFUL UPLOAD:

### Verify on GitHub:
1. Visit: https://github.com/blacknirchinblade/sat_sight
2. Check README displays correctly
3. Verify all source code is present

### Add Repository Description:
1. Click "About" gear icon
2. Description: "Multi-agent satellite imagery analysis system with LangGraph orchestration"
3. Website: http://10.32.38.102:8501
4. Topics: satellite-imagery, multi-agent, langraph, ai, clip, faiss, python, streamlit

### Add Banner & Video:
```bash
# Add your banner (recommended size: 1200x630px)
cp /path/to/banner.png docs/images/banner.png
git add docs/images/banner.png
git commit -m "Add project banner"
git push

# Add demo video (if < 100MB)
cp /path/to/demo.mp4 docs/videos/demo.mp4
git add docs/videos/demo.mp4
git commit -m "Add demo video"
git push
```

### Create First Release:
```bash
# Tag version 1.0.0
git tag -a v1.0.0 -m "Sat-Sight v1.0.0 - Initial Release"
git push origin v1.0.0

# Then on GitHub: Releases → Draft new release → Choose v1.0.0
```

---

## REPOSITORY INFO:

**URL:** https://github.com/blacknirchinblade/sat_sight  
**Clone:** `git clone https://github.com/blacknirchinblade/sat_sight.git`  
**Live Demo:** http://10.32.38.102:8501/ (IISc network only)  
**License:** MIT  

---

## CONTRIBUTORS:

1. Ganesh Islavath - gaenshi@iisc.ac.in (GitHub: blacknirchinblade)
2. Rajiv Poorna - rajivpoorna@iisc.ac.in
3. Suraj Sai Praneeth - surajs@iisc.ac.in
4. Bhookya Raju - bhookyaraju@iisc.ac.in

General Contact: ganeshnaik214@gmail.com

---

**GOOD LUCK! 🎉**
