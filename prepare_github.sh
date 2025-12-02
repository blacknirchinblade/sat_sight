#!/bin/bash
# GitHub Upload Preparation Script
# This script prepares the codebase for GitHub upload

echo "========================================="
echo "  Sat-Sight GitHub Preparation"
echo "========================================="

# Navigate to project root
cd "$(dirname "$0")"

# Remove unnecessary files
echo "Cleaning up unnecessary files..."

# Remove documentation (will be in separate repo)
rm -rf docs/*.md
rm -rf docs/*.html
rm -f *_SUMMARY.md *_GUIDE.md *_RESULTS.md *_CHECKLIST.md *_STATUS.md
rm -f CLEANUP_SUMMARY.md COORDINATE_STRATEGY.md CRITICAL_FIX_RESULTS.md
rm -f DATA_SOURCES.md DEPLOYMENT_CHECKLIST.md ENHANCED_UI_FEATURES.md
rm -f FINAL_CLEANUP_REPORT.md GENAI_ALIGNMENT_AND_DATASETS.md
rm -f GEOGRAPHIC_DATASETS.md GITHUB_UPLOAD.md IMPLEMENTATION_SUMMARY_MCP_MEMORY.md
rm -f IMPORT_FIX_GUIDE.md IMPROVEMENTS_SUMMARY.md MCP_MEMORY_GUIDE.md
rm -f PROJECT_UPDATE_SUMMARY.md QUICK_REFERENCE.md RESEARCH_IDEAS.md
rm -f TESTING_GUIDE.md TEST_RESULTS.md UI_THINKING_FEATURE.md
rm -f USER_TESTING_RESULTS.md README.old.md README_PROFESSIONAL.md
rm -f PROJECT_TRANSFORMATION_PLAN.md COMPLETE_DOCUMENTATION_SUMMARY.md

# Remove test files
echo "Removing test files..."
rm -f test_*.py *_test.py quick_test.sh test_full_workflow.sh
rm -f PROGRESS_SUMMARY.py download_model.py

# Remove archive directories
echo "Removing archives..."
rm -rf _archive_*
rm -rf *_backup_*

# Remove data directory (users will create their own)
echo "Removing data directory..."
rm -rf data/

# Remove evaluation directory
echo "Removing evaluation directory..."
rm -rf evaluation/

# Remove scripts if they exist
echo "Removing scripts directory..."
rm -rf scripts/

# Remove shell scripts (optional - keep setup scripts)
echo "Removing shell scripts (keeping essential ones)..."
find . -name "*.sh" ! -name "setup_environment.sh" ! -name "prepare_github.sh" -delete

# Clean Python cache
echo "Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*.log" -delete

# Create necessary directories placeholder
echo "Creating directory structure..."
mkdir -p data/memory
mkdir -p data/models
mkdir -p data/images
echo "# Place your satellite images here" > data/images/README.md
echo "# Models will be stored here" > data/models/README.md
echo "# Memory databases will be created here" > data/memory/README.md

echo ""
echo "========================================="
echo "  Cleanup Complete!"
echo "========================================="
echo ""
echo "Files ready for GitHub:"
echo "  [+] Source code (core/, agents/, models/, etc.)"
echo "  [+] Configuration files"
echo "  [+] Requirements"
echo "  [+] Setup scripts"
echo "  [+] Main README"
echo ""
echo "Excluded:"
echo "  [-] Data files"
echo "  [-] Models"
echo "  [-] Documentation (separate repo)"
echo "  [-] Test files"
echo "  [-] Archives"
echo ""
echo "Next steps:"
echo "  1. Review files: git status"
echo "  2. Initialize: git init"
echo "  3. Add files: git add ."
echo "  4. Commit: git commit -m 'Initial commit'"
echo "  5. Push to GitHub"
echo "========================================="
