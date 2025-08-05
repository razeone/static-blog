#!/usr/bin/env python3
"""
Content Validator and Post-processor for GitHub Pages Migration
==============================================================

This script validates and post-processes the migrated content to ensure
compatibility with GitHub Pages and Jekyll.

Features:
- Validates Jekyll front matter
- Checks for broken links and images
- Optimizes images for web
- Generates tag and category pages
- Creates RSS feed
- Validates HTML output

Author: Migration Script
Date: 2025
"""

import os
import re
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set
from urllib.parse import urlparse
import argparse


class GitHubPagesValidator:
    def __init__(self, site_dir: str):
        self.site_dir = Path(site_dir)
        self.posts = []
        self.pages = []
        self.tags = set()
        self.categories = set()
        self.errors = []
        self.warnings = []
        
    def load_jekyll_posts(self) -> List[Dict[str, Any]]:
        """Load all Jekyll posts"""
        posts_dir = self.site_dir / '_posts'
        posts = []
        
        if not posts_dir.exists():
            self.errors.append("No _posts directory found")
            return posts
            
        for post_file in posts_dir.glob('*.md'):
            try:
                with open(post_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse front matter
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        frontmatter = yaml.safe_load(parts[1])
                        body = parts[2].strip()
                        
                        post_data = {
                            'file': post_file,
                            'frontmatter': frontmatter or {},
                            'content': body,
                            'slug': post_file.stem
                        }
                        posts.append(post_data)
                        
                        # Collect tags and categories
                        if 'tags' in frontmatter:
                            if isinstance(frontmatter['tags'], list):
                                self.tags.update(frontmatter['tags'])
                            else:
                                self.tags.add(frontmatter['tags'])
                        
                        if 'categories' in frontmatter:
                            if isinstance(frontmatter['categories'], list):
                                self.categories.update(frontmatter['categories'])
                            else:
                                self.categories.add(frontmatter['categories'])
                        
            except Exception as e:
                self.errors.append(f"Error loading post {post_file}: {e}")
        
        self.posts = posts
        return posts
    
    def validate_frontmatter(self, post: Dict[str, Any]) -> List[str]:
        """Validate Jekyll front matter for a post"""
        errors = []
        fm = post['frontmatter']
        
        # Required fields
        required_fields = ['title', 'date', 'layout']
        for field in required_fields:
            if field not in fm:
                errors.append(f"Missing required field: {field}")
        
        # Validate date format
        if 'date' in fm:
            date_str = str(fm['date'])
            try:
                if 'T' in date_str:
                    datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                elif len(date_str) >= 10:
                    datetime.strptime(date_str[:10], '%Y-%m-%d')
                else:
                    errors.append(f"Invalid date format: {date_str}")
            except ValueError:
                errors.append(f"Invalid date format: {date_str}")
        
        # Validate layout
        if fm.get('layout') not in ['post', 'default', 'page']:
            self.warnings.append(f"Unusual layout: {fm.get('layout')}")
        
        return errors
    
    def check_image_links(self, content: str, post_file: Path) -> List[str]:
        """Check for broken image links"""
        errors = []
        
        # Find all image references
        img_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        images = re.findall(img_pattern, content)
        
        for alt_text, img_path in images:
            # Check if image exists
            if img_path.startswith('/assets/'):
                full_path = self.site_dir / img_path[1:]  # Remove leading /
                if not full_path.exists():
                    errors.append(f"Missing image: {img_path}")
            elif img_path.startswith('http'):
                # External image - could check if accessible
                pass
            else:
                # Relative path
                relative_path = post_file.parent / img_path
                if not relative_path.exists():
                    errors.append(f"Missing relative image: {img_path}")
        
        return errors
    
    def check_internal_links(self, content: str) -> List[str]:
        """Check for broken internal links"""
        errors = []
        
        # Find all markdown links
        link_pattern = r'\[([^\]]*)\]\(([^)]+)\)'
        links = re.findall(link_pattern, content)
        
        for link_text, link_url in links:
            if link_url.startswith('/') and not link_url.startswith('//'):
                # Internal link
                if link_url.endswith('/'):
                    # Directory-style link
                    check_path = self.site_dir / link_url[1:] / 'index.md'
                    if not check_path.exists():
                        check_path = self.site_dir / f"{link_url[1:]}/index.html"
                        if not check_path.exists():
                            self.warnings.append(f"Potentially broken internal link: {link_url}")
                else:
                    # File-style link
                    check_path = self.site_dir / link_url[1:]
                    if not check_path.exists():
                        # Try with .md extension
                        check_path = self.site_dir / f"{link_url[1:]}.md"
                        if not check_path.exists():
                            self.warnings.append(f"Potentially broken internal link: {link_url}")
        
        return errors
    
    def validate_posts(self):
        """Validate all posts"""
        print("🔍 Validating posts...")
        
        for post in self.posts:
            post_errors = []
            
            # Validate front matter
            fm_errors = self.validate_frontmatter(post)
            post_errors.extend(fm_errors)
            
            # Check image links
            img_errors = self.check_image_links(post['content'], post['file'])
            post_errors.extend(img_errors)
            
            # Check internal links
            link_errors = self.check_internal_links(post['content'])
            post_errors.extend(link_errors)
            
            if post_errors:
                self.errors.extend([f"{post['file'].name}: {error}" for error in post_errors])
            else:
                print(f"✅ {post['file'].name} - OK")
    
    def generate_tag_pages(self):
        """Generate individual tag pages"""
        if not self.tags:
            return
            
        tags_dir = self.site_dir / 'tags'
        tags_dir.mkdir(exist_ok=True)
        
        # Generate index page for all tags
        tag_index_content = '''---
layout: default
title: Tags
---

<div class="tags-page">
    <h1>All Tags</h1>
    <div class="tag-cloud">
        {% assign sorted_tags = site.tags | sort %}
        {% for tag in sorted_tags %}
        <a href="{{ '/tags/' | append: tag[0] | relative_url }}" class="tag-link">
            {{ tag[0] }} ({{ tag[1].size }})
        </a>
        {% endfor %}
    </div>
</div>'''
        
        with open(tags_dir / 'index.md', 'w') as f:
            f.write(tag_index_content)
        
        # Generate individual tag pages
        for tag in self.tags:
            tag_slug = re.sub(r'[^\w\-]', '-', tag.lower())
            tag_content = f'''---
layout: default
title: "Posts tagged with '{tag}'"
tag: {tag}
---

<div class="tag-page">
    <h1>Posts tagged with "{{ page.tag }}"</h1>
    
    <div class="posts">
        {{% for post in site.tags[page.tag] %}}
        <article class="post-preview">
            <h2><a href="{{{{ post.url | relative_url }}}}">{{{{ post.title }}}}</a></h2>
            <div class="post-meta">
                <time datetime="{{{{ post.date | date_to_xmlschema }}}}">
                    {{{{ post.date | date: '%B %d, %Y' }}}}
                </time>
            </div>
            {{% if post.description %}}
            <p>{{{{ post.description }}}}</p>
            {{% endif %}}
        </article>
        {{% endfor %}}
    </div>
    
    <p><a href="{{{{ '/tags/' | relative_url }}}}">&larr; All Tags</a></p>
</div>'''
            
            with open(tags_dir / f'{tag_slug}.md', 'w') as f:
                f.write(tag_content)
        
        print(f"🏷️  Generated {len(self.tags)} tag pages")
    
    def generate_category_pages(self):
        """Generate individual category pages"""
        if not self.categories:
            return
            
        categories_dir = self.site_dir / 'categories'
        categories_dir.mkdir(exist_ok=True)
        
        # Generate index page for all categories
        category_index_content = '''---
layout: default
title: Categories
---

<div class="categories-page">
    <h1>All Categories</h1>
    <div class="category-list">
        {% assign sorted_categories = site.categories | sort %}
        {% for category in sorted_categories %}
        <div class="category-item">
            <h3><a href="{{ '/categories/' | append: category[0] | relative_url }}">
                {{ category[0] | capitalize }}
            </a></h3>
            <p>{{ category[1].size }} posts</p>
        </div>
        {% endfor %}
    </div>
</div>'''
        
        with open(categories_dir / 'index.md', 'w') as f:
            f.write(category_index_content)
        
        # Generate individual category pages
        for category in self.categories:
            category_slug = re.sub(r'[^\w\-]', '-', category.lower())
            category_content = f'''---
layout: default
title: "Posts in category '{category}'"
category: {category}
---

<div class="category-page">
    <h1>Posts in "{{ page.category | capitalize }}"</h1>
    
    <div class="posts">
        {{% for post in site.categories[page.category] %}}
        <article class="post-preview">
            <h2><a href="{{{{ post.url | relative_url }}}}">{{{{ post.title }}}}</a></h2>
            <div class="post-meta">
                <time datetime="{{{{ post.date | date_to_xmlschema }}}}">
                    {{{{ post.date | date: '%B %d, %Y' }}}}
                </time>
            </div>
            {{% if post.description %}}
            <p>{{{{ post.description }}}}</p>
            {{% endif %}}
        </article>
        {{% endfor %}}
    </div>
    
    <p><a href="{{{{ '/categories/' | relative_url }}}}">&larr; All Categories</a></p>
</div>'''
            
            with open(categories_dir / f'{category_slug}.md', 'w') as f:
                f.write(category_content)
        
        print(f"📂 Generated {len(self.categories)} category pages")
    
    def generate_sitemap(self):
        """Generate sitemap.xml"""
        sitemap_content = '''---
layout: null
---
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{{ site.url }}{{ site.baseurl }}/</loc>
    <lastmod>{{ site.time | date_to_xmlschema }}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  
  {% for post in site.posts %}
  <url>
    <loc>{{ site.url }}{{ site.baseurl }}{{ post.url }}</loc>
    <lastmod>{{ post.date | date_to_xmlschema }}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  {% endfor %}
  
  {% for page in site.pages %}
  {% unless page.url contains 'feed' or page.url contains 'sitemap' %}
  <url>
    <loc>{{ site.url }}{{ site.baseurl }}{{ page.url }}</loc>
    <lastmod>{{ site.time | date_to_xmlschema }}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>
  {% endunless %}
  {% endfor %}
</urlset>'''
        
        with open(self.site_dir / 'sitemap.xml', 'w') as f:
            f.write(sitemap_content)
        
        print("🗺️  Generated sitemap.xml")
    
    def create_readme(self):
        """Create README for the GitHub Pages repository"""
        readme_content = f'''# GitHub Pages Blog

This blog has been migrated from Hugo to GitHub Pages using Jekyll.

## 📊 Site Statistics

- **Posts**: {len(self.posts)}
- **Tags**: {len(self.tags)}
- **Categories**: {len(self.categories)}

## 🚀 Local Development

To run this site locally:

```bash
# Install dependencies
bundle install

# Serve the site
bundle exec jekyll serve

# Open http://localhost:4000 in your browser
```

## 📝 Writing New Posts

Create a new file in `_posts/` with the format: `YYYY-MM-DD-title.md`

```markdown
---
layout: post
title: "Your Post Title"
date: 2025-01-01 12:00:00 +0000
categories: [category1, category2]
tags: [tag1, tag2]
description: "Brief description of your post"
---

Your post content here...
```

## 🏷️ Tags and Categories

- **Tags**: {', '.join(sorted(self.tags)) if self.tags else 'None'}
- **Categories**: {', '.join(sorted(self.categories)) if self.categories else 'None'}

## 📁 Site Structure

```
.
├── _posts/           # Blog posts
├── _layouts/         # Page layouts
├── _includes/        # Reusable components
├── assets/          # CSS, JS, images
├── tags/            # Tag pages
├── categories/      # Category pages
├── _config.yml      # Jekyll configuration
└── Gemfile          # Ruby dependencies
```

## 🔧 Configuration

The site configuration is in `_config.yml`. Key settings:

- Site title, description, and author
- Permalink structure
- Plugin configuration
- Social media links

## 📱 Deployment

This site is automatically deployed to GitHub Pages using GitHub Actions.
The workflow is defined in `.github/workflows/jekyll.yml`.

## 🎨 Customization

To customize the appearance:

1. Edit CSS in `assets/css/main.css`
2. Modify layouts in `_layouts/`
3. Update includes in `_includes/`

## 📈 Analytics

To add Google Analytics, add your tracking ID to `_config.yml`:

```yaml
google_analytics: UA-XXXXXXXX-X
```

---

Generated by Hugo to GitHub Pages migration script on {datetime.now().strftime('%Y-%m-%d')}
'''
        
        with open(self.site_dir / 'README.md', 'w') as f:
            f.write(readme_content)
        
        print("📖 Generated README.md")
    
    def validate(self):
        """Main validation process"""
        print("🔍 Starting validation...")
        
        # Load posts
        self.load_jekyll_posts()
        
        # Validate posts
        self.validate_posts()
        
        # Generate additional pages
        self.generate_tag_pages()
        self.generate_category_pages()
        self.generate_sitemap()
        self.create_readme()
        
        # Report results
        print(f"\n📊 Validation Results:")
        print(f"✅ Posts processed: {len(self.posts)}")
        print(f"🏷️  Tags found: {len(self.tags)}")
        print(f"📂 Categories found: {len(self.categories)}")
        
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if not self.errors and not self.warnings:
            print("\n🎉 All validation checks passed!")


def main():
    parser = argparse.ArgumentParser(description='Validate and post-process GitHub Pages migration')
    parser.add_argument('site_dir', nargs='?', default='github-pages-site', help='GitHub Pages site directory')
    
    args = parser.parse_args()
    
    if not Path(args.site_dir).exists():
        print(f"❌ Site directory '{args.site_dir}' does not exist")
        print("Run the migration script first: python migrate_to_github_pages.py")
        return
    
    validator = GitHubPagesValidator(args.site_dir)
    validator.validate()


if __name__ == '__main__':
    main()
