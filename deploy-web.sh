#!/bin/bash
set -e

echo "🚀 Deploying web landing page to GitHub Pages..."

# Create a temporary directory for the web content
TEMP_DIR=$(mktemp -d)
echo "📁 Using temp directory: $TEMP_DIR"

# Copy web landing page files
cp -r web/pop-landing/* "$TEMP_DIR/"
cp -r web/static/images "$TEMP_DIR/" 2>/dev/null || true

# Initialize git in temp directory
cd "$TEMP_DIR"
git init
git config user.email "madge@example.com"
git config user.name "Madge"
git remote add origin https://github.com/MADGE-petter/Virtual-Assistantpop-Linux.git || true

# Create gh-pages branch
git checkout -b gh-pages 2>/dev/null || git checkout gh-pages

# Add and commit
git add -A
git commit -m "Deploy web landing page $(date +%Y-%m-%d)" || true

# Force push to gh-pages branch
git push -f origin gh-pages

# Cleanup
cd -
rm -rf "$TEMP_DIR"

echo "✅ Deployment complete!"
echo "🌐 Your site will be available at: https://MADGE-petter.github.io/Virtual-Assistantpop-Linux/"
