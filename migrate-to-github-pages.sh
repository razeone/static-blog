#!/bin/bash

# Migration script from AWS S3 + CloudFront to GitHub Pages
# This script helps automate the migration process

set -e  # Exit on any error

echo "🚀 Starting migration to GitHub Pages..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: This is not a git repository. Please run this script from your Hugo project root."
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo "🔍 Checking dependencies..."
if ! command_exists git; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

if ! command_exists hugo; then
    echo "❌ Hugo is not installed. Please install Hugo first."
    exit 1
fi

echo "✅ Dependencies check passed!"

# Backup current config
echo "📋 Creating backup of current config..."
cp config.toml config.toml.backup
echo "✅ Backup created: config.toml.backup"

# Update Hugo config for GitHub Pages
echo "⚙️  Updating Hugo configuration for GitHub Pages..."

# Get the GitHub repository name
REPO_NAME=$(basename `git rev-parse --show-toplevel`)
GITHUB_USER=$(git config user.name)

if [ -z "$GITHUB_USER" ]; then
    echo "❓ Enter your GitHub username:"
    read GITHUB_USER
fi

# Update baseURL in config.toml for GitHub Pages
echo "🔧 Updating baseURL for GitHub Pages..."
sed -i.bak "s|baseURL = \".*\"|baseURL = \"https://${GITHUB_USER}.github.io/${REPO_NAME}/\"|g" config.toml

echo "✅ Configuration updated!"
echo "   - Repository: ${REPO_NAME}"
echo "   - GitHub User: ${GITHUB_USER}"
echo "   - New baseURL: https://${GITHUB_USER}.github.io/${REPO_NAME}/"

# Create .nojekyll file to prevent Jekyll processing
echo "📄 Creating .nojekyll file..."
touch static/.nojekyll
echo "✅ .nojekyll file created in static/ directory"

# Test Hugo build
echo "🔨 Testing Hugo build..."
if hugo --minify; then
    echo "✅ Hugo build successful!"
else
    echo "❌ Hugo build failed. Please check your configuration."
    exit 1
fi

# Clean up build artifacts
rm -rf public

echo ""
echo "🎉 Migration preparation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Commit and push your changes to GitHub:"
echo "   git add ."
echo "   git commit -m 'Migrate to GitHub Pages'"
echo "   git push origin master"
echo ""
echo "2. Go to your GitHub repository settings:"
echo "   - Navigate to Settings > Pages"
echo "   - Select 'GitHub Actions' as the source"
echo "   - Your site will be available at: https://${GITHUB_USER}.github.io/${REPO_NAME}/"
echo ""
echo "3. Optional: Set up a custom domain if needed"
echo ""
echo "⚠️  Important notes:"
echo "- Your old AWS S3 bucket and CloudFront distribution are still active"
echo "- Remember to clean up AWS resources to avoid charges"
echo "- Update any hardcoded URLs in your content to use the new GitHub Pages URL"
echo ""
echo "🔄 To revert changes, restore the backup:"
echo "   mv config.toml.backup config.toml"
