# static-blog

This is my personal blog, originally built with Hugo + S3 + CloudFront + Lambda, now migrated to GitHub Pages.

## 🚀 Migration to GitHub Pages

This repository now includes Python scripts to migrate from Hugo to GitHub Pages (Jekyll). The migration process converts Hugo's TOML/YAML front matter to Jekyll format and creates a complete GitHub Pages-compatible site.

### Quick Migration

```bash
# Run the complete migration process
chmod +x complete_migration.sh
./complete_migration.sh
```

### Manual Migration Steps

1. **Install dependencies:**
```bash
pip install pyyaml toml pillow
```

2. **Run migration script:**
```bash
python3 migrate_to_github_pages.py --source . --output github-pages-site
```

3. **Validate the migration:**
```bash
python3 validate_github_pages.py github-pages-site
```

4. **Test locally (in the output directory):**
```bash
cd github-pages-site
bundle install
bundle exec jekyll serve
```

### Migration Features

- ✅ Converts Hugo posts to Jekyll format
- ✅ Preserves all metadata (tags, categories, dates)
- ✅ Copies and reorganizes static assets
- ✅ Generates Jekyll layouts and configuration
- ✅ Creates tag and category pages
- ✅ Includes GitHub Actions workflow
- ✅ Validates content and links
- ✅ Generates sitemap and SEO files

## 📁 Original Hugo Setup (Legacy)

### Quickstart

```bash
git clone https://github.com/razeone/static-blog.git
cd static-blog/
git submodule init
git submodule update
hugo serve -D
```

### Docker Quickstart

```bash
docker build . -t raze-website:<daVersion>
docker run -p 8080:80 localhost/raze-website:<daVersion>
```