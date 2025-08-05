#!/bin/bash

# Complete migration script from Hugo to GitHub Pages
# This script orchestrates the entire migration process

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HUGO_DIR="${SCRIPT_DIR}"
OUTPUT_DIR="github-pages-site"

echo "🚀 Hugo to GitHub Pages Migration Script"
echo "========================================"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo "📋 Checking dependencies..."
if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

if ! command_exists git; then
    echo "❌ Git is required but not installed"
    exit 1
fi

echo "✅ Dependencies check passed"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
python3 -m pip install --user pyyaml toml pillow || {
    echo "⚠️  Some dependencies might not be installed. Continuing..."
}
echo ""

# Run migration
echo "🔄 Starting migration process..."
python3 "${SCRIPT_DIR}/migrate_to_github_pages.py" --source "${HUGO_DIR}" --output "${OUTPUT_DIR}"

if [ $? -ne 0 ]; then
    echo "❌ Migration failed"
    exit 1
fi

echo ""
echo "🔍 Validating migrated content..."
python3 "${SCRIPT_DIR}/validate_github_pages.py" "${OUTPUT_DIR}"

if [ $? -ne 0 ]; then
    echo "⚠️  Validation completed with warnings"
fi

echo ""
echo "📁 Setting up Git repository..."
cd "${OUTPUT_DIR}"

if [ ! -d ".git" ]; then
    git init
    echo "📋 Initialized Git repository"
fi

# Create .gitignore
cat > .gitignore << 'EOF'
_site/
.sass-cache/
.jekyll-cache/
.jekyll-metadata
.bundle/
vendor/
*.gem
*.rbc
.rvmrc
.ruby-version
.ruby-gemset
Gemfile.lock

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~
EOF

echo "📄 Created .gitignore"

# Add all files
git add .
git status

echo ""
echo "🎉 Migration completed successfully!"
echo ""
echo "📊 Summary:"
echo "  📁 Output directory: ${OUTPUT_DIR}"
echo "  📝 Posts migrated: $(find _posts -name '*.md' 2>/dev/null | wc -l || echo '0')"
echo "  🖼️  Images copied: $(find assets/images -type f 2>/dev/null | wc -l || echo '0')"
echo ""
echo "📋 Next steps:"
echo "1. Review the generated files in ${OUTPUT_DIR}/"
echo "2. Test locally:"
echo "   cd ${OUTPUT_DIR}"
echo "   bundle install"
echo "   bundle exec jekyll serve"
echo ""
echo "3. Create GitHub repository and push:"
echo "   cd ${OUTPUT_DIR}"
echo "   git remote add origin https://github.com/USERNAME/REPOSITORY.git"
echo "   git branch -M main"
echo "   git commit -m 'Initial migration from Hugo to GitHub Pages'"
echo "   git push -u origin main"
echo ""
echo "4. Enable GitHub Pages:"
echo "   - Go to repository Settings > Pages"
echo "   - Select 'GitHub Actions' as source"
echo "   - Your site will be available at: https://USERNAME.github.io/REPOSITORY/"
echo ""
echo "💡 Tips:"
echo "  - Update _config.yml with your site details"
echo "  - Customize CSS in assets/css/main.css"
echo "  - Add your own domain in repository Settings > Pages if desired"
echo ""
echo "⚠️  Remember to clean up your old AWS S3 bucket and CloudFront distribution!"
echo ""
