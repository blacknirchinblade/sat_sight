# GitHub Upload Guide

## Step-by-Step Instructions

### 1. Prepare Repository

```bash
cd /home/ganesh/GenAi_Project/sat_sight

# Run cleanup script
chmod +x prepare_github.sh
./prepare_github.sh
```

### 2. Initialize Git

```bash
# Initialize repository
git init

# Check status
git status
```

### 3. Review Files to Upload

**Include:**
- ✅ All Python source code (`.py` files)
- ✅ `requirements.txt` and `requirements_minimal.txt`
- ✅ `README_GITHUB.md` (rename to `README.md`)
- ✅ `setup.py`
- ✅ `.gitignore`
- ✅ `setup_environment.sh`
- ✅ LICENSE (if you have one)

**Exclude (already in .gitignore):**
- ❌ `data/` directory
- ❌ `docs/` documentation files
- ❌ `*.log` files
- ❌ `__pycache__/` directories
- ❌ `*.db` files
- ❌ Model files (`.gguf`, `.bin`, etc.)
- ❌ Test files
- ❌ Archive directories

### 4. Create GitHub Repository

1. Go to https://github.com
2. Click "New Repository"
3. Name: `sat-sight`
4. Description: "Multi-Agent Satellite Imagery Analysis with GenAI"
5. Choose Public or Private
6. **Do NOT** initialize with README (we have our own)
7. Click "Create repository"

### 5. Add Files to Git

```bash
# Stage all files
git add .

# Check what will be committed
git status

# If you see unwanted files, add them to .gitignore
echo "unwanted_file.txt" >> .gitignore
git reset
git add .
```

### 6. Create First Commit

```bash
# Commit with message
git commit -m "Initial commit: Sat-Sight multi-agent system

- Multi-agent architecture with LangGraph
- CLIP + FAISS vision search
- ChromaDB text retrieval
- 3-layer memory system
- Streamlit UI with chat sessions
- Groq API + local LLM support"
```

### 7. Connect to GitHub

```bash
# Add remote (replace with your username)
git remote add origin https://github.com/YOUR_USERNAME/sat-sight.git

# Verify remote
git remote -v
```

### 8. Push to GitHub

```bash
# Push to main branch
git branch -M main
git push -u origin main
```

### 9. Add README and Description

On GitHub:
1. Repository should now show your code
2. Rename `README_GITHUB.md` to `README.md` if not done:
   ```bash
   mv README_GITHUB.md README.md
   git add README.md
   git commit -m "Update README"
   git push
   ```

### 10. Add Topics (Tags)

On GitHub repository page:
1. Click "About" gear icon
2. Add topics:
   - `satellite-imagery`
   - `multi-agent-system`
   - `langchain`
   - `langgraph`
   - `clip`
   - `faiss`
   - `genai`
   - `computer-vision`
   - `nlp`
   - `streamlit`

### 11. Create LICENSE (Optional but Recommended)

```bash
# Create MIT License
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2025 [Your Name]

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

### 12. Verify Upload

Visit: `https://github.com/YOUR_USERNAME/sat-sight`

Check:
- ✅ All source code is visible
- ✅ README displays correctly
- ✅ No data or model files uploaded
- ✅ Directory structure intact
- ✅ requirements.txt present

## Maintenance

### Update Code

```bash
# Make changes to code
git add .
git commit -m "Description of changes"
git push
```

### Create Branches for Features

```bash
git checkout -b feature/new-agent
# Make changes
git add .
git commit -m "Add new agent"
git push -u origin feature/new-agent
```

### Tag Releases

```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## Troubleshooting

### Large Files Error

If you get "file too large" error:

```bash
# Check file sizes
find . -type f -size +50M

# Remove from git
git rm --cached large_file.bin
echo "large_file.bin" >> .gitignore
git add .gitignore
git commit -m "Remove large file"
```

### Reset if Needed

```bash
# Uncommit last commit (keep changes)
git reset --soft HEAD~1

# Discard all uncommitted changes (CAREFUL!)
git reset --hard HEAD
```

### View Commit History

```bash
git log --oneline --graph --all
```

## Best Practices

1. **Commit Often**: Small, focused commits with clear messages
2. **Branch Strategy**: Use branches for new features
3. **Pull Before Push**: Always `git pull` before `git push`
4. **Review Changes**: Use `git diff` before committing
5. **Write Good Messages**: Descriptive commit messages
6. **Tag Releases**: Use semantic versioning (v1.0.0)
7. **Update README**: Keep documentation current
8. **Ignore Secrets**: Never commit API keys or credentials

## Repository Structure on GitHub

```
sat-sight/
├── agents/          # Agent implementations
├── core/            # Core workflow and state
├── models/          # LLM router
├── retrieval/       # Vector stores and search
├── memory/          # Memory systems
├── tools/           # External tool wrappers
├── utils/           # Utility functions
├── ui/              # Streamlit interface
├── .gitignore
├── requirements.txt
├── requirements_minimal.txt
├── setup.py
├── README.md
└── LICENSE
```

## Next Steps After Upload

1. **Enable GitHub Actions** (optional): Add CI/CD workflows
2. **Add Badges**: Build status, license, version badges
3. **Create Issues**: Document known bugs and feature requests
4. **Wiki**: Add detailed documentation
5. **Releases**: Create release notes for versions
6. **Contributors**: Add CONTRIBUTING.md guide

## Contact & Support

For questions: Open an issue on GitHub
