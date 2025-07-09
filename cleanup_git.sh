#!/bin/bash
# Git cleanup script for health chatbot backend

echo "🧹 Cleaning up Git repository..."

# Remove venv directory from Git tracking (but keep it locally)
echo "📁 Removing venv/ from Git tracking..."
git rm -r --cached venv/ 2>/dev/null || echo "venv/ not tracked or already removed"

# Remove __pycache__ directories from tracking
echo "🗂️ Removing __pycache__ from Git tracking..."
git rm -r --cached __pycache__/ 2>/dev/null || echo "__pycache__ not tracked or already removed"
git rm -r --cached models/__pycache__/ 2>/dev/null || echo "models/__pycache__ not tracked or already removed"

# Remove any other cached files
echo "🗑️ Cleaning cached files..."
git rm -r --cached . 2>/dev/null || echo "No cached files to remove"

# Re-add everything (this time respecting .gitignore)
echo "➕ Re-adding files (respecting .gitignore)..."
git add .

# Show what will be committed
echo "📋 Files to be committed:"
git status

echo "✅ Cleanup complete!"
echo "💡 Run 'git commit -m \"Clean repository - exclude venv and cache files\"' to commit changes" 