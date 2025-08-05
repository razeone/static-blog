#!/usr/bin/env python3
"""
Hugo to GitHub Pages Migration Script
====================================

This script converts a Hugo static site to a format compatible with GitHub Pages
using Jekyll-style front matter and directory structure.

Features:
- Converts Hugo front matter to Jekyll format
- Creates proper directory structure for GitHub Pages
- Processes images and static assets
- Generates index files and navigation
- Creates GitHub Actions workflow for deployment

Author: Migration Script
Date: 2025
"""

import os
import re
import shutil
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse


class HugoToGitHubPagesMigrator:
    def __init__(self, source_dir: str, output_dir: str = "github-pages-site"):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.config = {}
        self.posts = []
        self.pages = []
        
    def load_hugo_config(self) -> Dict[str, Any]:
        """Load and parse Hugo configuration from config.toml"""
        config_file = self.source_dir / "config.toml"
        if not config_file.exists():
            print("⚠️  Warning: config.toml not found, using defaults")
            return {}
            
        try:
            import toml
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = toml.load(f)
                print(f"✅ Loaded Hugo configuration from {config_file}")
                return self.config
        except ImportError:
            print("❌ Error: toml package not installed. Install with: pip install toml")
            return {}
        except Exception as e:
            print(f"❌ Error loading config.toml: {e}")
            return {}
    
    def parse_hugo_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
        """Parse Hugo front matter (TOML, YAML, or JSON)"""
        if content.startswith('---'):
            # YAML front matter
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1])
                    body = parts[2].strip()
                    return frontmatter or {}, body
                except yaml.YAMLError as e:
                    print(f"⚠️  Warning: Error parsing YAML front matter: {e}")
                    return {}, content
        
        elif content.startswith('+++'):
            # TOML front matter
            parts = content.split('+++', 2)
            if len(parts) >= 3:
                try:
                    import toml
                    frontmatter = toml.loads(parts[1])
                    body = parts[2].strip()
                    return frontmatter, body
                except Exception as e:
                    print(f"⚠️  Warning: Error parsing TOML front matter: {e}")
                    return {}, content
        
        elif content.startswith('{'):
            # JSON front matter (less common)
            try:
                lines = content.split('\n')
                json_end = 0
                brace_count = 0
                for i, line in enumerate(lines):
                    brace_count += line.count('{') - line.count('}')
                    if brace_count == 0 and i > 0:
                        json_end = i + 1
                        break
                
                json_part = '\n'.join(lines[:json_end])
                body = '\n'.join(lines[json_end:]).strip()
                frontmatter = json.loads(json_part)
                return frontmatter, body
            except json.JSONDecodeError as e:
                print(f"⚠️  Warning: Error parsing JSON front matter: {e}")
                return {}, content
        
        return {}, content
    
    def convert_frontmatter_to_jekyll(self, hugo_fm: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Hugo front matter to Jekyll format"""
        jekyll_fm = {}
        
        # Basic fields mapping
        field_mapping = {
            'title': 'title',
            'date': 'date',
            'description': 'description',
            'Description': 'description',
            'tags': 'tags',
            'Tags': 'tags',
            'categories': 'categories',
            'Categories': 'categories',
            'author': 'author',
            'thumbnail': 'image',
            'Thumbnail': 'image',
        }
        
        for hugo_key, jekyll_key in field_mapping.items():
            if hugo_key in hugo_fm:
                jekyll_fm[jekyll_key] = hugo_fm[hugo_key]
        
        # Set layout
        jekyll_fm['layout'] = 'post'
        
        # Handle draft status
        if hugo_fm.get('draft', False):
            jekyll_fm['published'] = False
        
        # Convert date format if needed
        if 'date' in jekyll_fm:
            date_str = str(jekyll_fm['date'])
            try:
                # Parse various date formats
                if 'T' in date_str:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    jekyll_fm['date'] = dt.strftime('%Y-%m-%d %H:%M:%S %z')
                elif len(date_str) == 10:  # YYYY-MM-DD
                    jekyll_fm['date'] = date_str
            except Exception as e:
                print(f"⚠️  Warning: Could not parse date {date_str}: {e}")
        
        return jekyll_fm
    
    def process_content_images(self, content: str, post_slug: str) -> str:
        """Update image paths for GitHub Pages"""
        # Replace relative image paths
        content = re.sub(
            r'!\[([^\]]*)\]\(images/([^)]+)\)',
            r'![\1](/assets/images/\2)',
            content
        )
        
        # Replace other Hugo-specific shortcodes if needed
        content = re.sub(r'{{<\s*rawhtml\s*>}}', '', content)
        content = re.sub(r'{{<\s*/rawhtml\s*>}}', '', content)
        
        return content
    
    def convert_post(self, post_path: Path) -> Optional[Dict[str, Any]]:
        """Convert a single Hugo post to Jekyll format"""
        try:
            with open(post_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            hugo_fm, body = self.parse_hugo_frontmatter(content)
            jekyll_fm = self.convert_frontmatter_to_jekyll(hugo_fm)
            
            # Generate slug from filename
            slug = post_path.stem
            if slug == '_index':
                return None  # Skip index files
            
            # Process content
            processed_body = self.process_content_images(body, slug)
            
            # Create post data
            post_data = {
                'frontmatter': jekyll_fm,
                'content': processed_body,
                'slug': slug,
                'filename': post_path.name,
                'original_path': str(post_path)
            }
            
            return post_data
            
        except Exception as e:
            print(f"❌ Error processing {post_path}: {e}")
            return None
    
    def create_output_structure(self):
        """Create the output directory structure for GitHub Pages"""
        directories = [
            self.output_dir,
            self.output_dir / '_posts',
            self.output_dir / '_layouts',
            self.output_dir / '_includes',
            self.output_dir / 'assets',
            self.output_dir / 'assets' / 'images',
            self.output_dir / 'assets' / 'css',
            self.output_dir / 'assets' / 'js',
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created directory: {directory}")
    
    def copy_static_assets(self):
        """Copy static assets (images, CSS, JS)"""
        static_dir = self.source_dir / 'static'
        if static_dir.exists():
            # Copy images
            images_src = static_dir / 'images'
            if images_src.exists():
                images_dst = self.output_dir / 'assets' / 'images'
                shutil.copytree(images_src, images_dst, dirs_exist_ok=True)
                print(f"📸 Copied images from {images_src} to {images_dst}")
            
            # Copy other static files
            for item in static_dir.iterdir():
                if item.name != 'images':
                    dst = self.output_dir / 'assets' / item.name
                    if item.is_dir():
                        shutil.copytree(item, dst, dirs_exist_ok=True)
                    else:
                        shutil.copy2(item, dst)
                    print(f"📄 Copied {item} to {dst}")
    
    def generate_jekyll_layouts(self):
        """Generate basic Jekyll layouts"""
        
        # Default layout
        default_layout = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% if page.title %}{{ page.title }} - {% endif %}{{ site.title }}</title>
    <meta name="description" content="{% if page.description %}{{ page.description }}{% else %}{{ site.description }}{% endif %}">
    
    <!-- CSS -->
    <link rel="stylesheet" href="{{ '/assets/css/main.css' | relative_url }}">
    
    <!-- Favicon -->
    <link rel="icon" type="image/x-icon" href="{{ '/assets/favicon.ico' | relative_url }}">
</head>
<body>
    <header>
        <nav>
            <h1><a href="{{ '/' | relative_url }}">{{ site.title }}</a></h1>
            <ul>
                <li><a href="{{ '/' | relative_url }}">Home</a></li>
                <li><a href="{{ '/posts/' | relative_url }}">Posts</a></li>
                <li><a href="{{ '/about/' | relative_url }}">About</a></li>
            </ul>
        </nav>
    </header>
    
    <main>
        {{ content }}
    </main>
    
    <footer>
        <p>&copy; {{ site.time | date: '%Y' }} {{ site.author }}. All rights reserved.</p>
    </footer>
</body>
</html>'''
        
        # Post layout
        post_layout = '''---
layout: default
---

<article class="post">
    <header class="post-header">
        <h1 class="post-title">{{ page.title }}</h1>
        <div class="post-meta">
            <time datetime="{{ page.date | date_to_xmlschema }}">
                {{ page.date | date: '%B %d, %Y' }}
            </time>
            {% if page.author %}
            <span class="post-author">by {{ page.author }}</span>
            {% endif %}
        </div>
        {% if page.tags %}
        <div class="post-tags">
            {% for tag in page.tags %}
            <span class="tag">{{ tag }}</span>
            {% endfor %}
        </div>
        {% endif %}
    </header>
    
    {% if page.image %}
    <div class="post-image">
        <img src="{{ page.image | relative_url }}" alt="{{ page.title }}">
    </div>
    {% endif %}
    
    <div class="post-content">
        {{ content }}
    </div>
</article>'''
        
        # Write layouts
        with open(self.output_dir / '_layouts' / 'default.html', 'w') as f:
            f.write(default_layout)
        
        with open(self.output_dir / '_layouts' / 'post.html', 'w') as f:
            f.write(post_layout)
        
        print("📄 Generated Jekyll layouts")
    
    def generate_jekyll_config(self):
        """Generate _config.yml for Jekyll"""
        config = {
            'title': self.config.get('params', {}).get('title', 'My Blog'),
            'description': self.config.get('params', {}).get('description', 'A blog migrated from Hugo'),
            'author': self.config.get('params', {}).get('author', 'Blog Author'),
            'url': '',  # Will be set by GitHub Pages
            'baseurl': '',  # Will be set by GitHub Pages
            
            # Jekyll configuration
            'markdown': 'kramdown',
            'highlighter': 'rouge',
            'permalink': '/posts/:title/',
            'paginate': 10,
            'paginate_path': '/posts/page:num/',
            
            # Plugins
            'plugins': [
                'jekyll-feed',
                'jekyll-sitemap',
                'jekyll-seo-tag',
                'jekyll-paginate'
            ],
            
            # Collections
            'collections': {
                'posts': {
                    'output': True,
                    'permalink': '/posts/:title/'
                }
            },
            
            # Defaults
            'defaults': [
                {
                    'scope': {
                        'path': '',
                        'type': 'posts'
                    },
                    'values': {
                        'layout': 'post',
                        'author': self.config.get('params', {}).get('author', 'Blog Author')
                    }
                }
            ]
        }
        
        with open(self.output_dir / '_config.yml', 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        print("⚙️  Generated _config.yml")
    
    def generate_index_page(self):
        """Generate main index page"""
        index_content = '''---
layout: default
---

<div class="home">
    <h1>Welcome to My Blog</h1>
    <p>This blog has been migrated from Hugo to GitHub Pages.</p>
    
    <h2>Recent Posts</h2>
    <ul class="post-list">
        {% for post in site.posts limit:5 %}
        <li>
            <span class="post-meta">{{ post.date | date: '%b %-d, %Y' }}</span>
            <h3>
                <a class="post-link" href="{{ post.url | relative_url }}">
                    {{ post.title | escape }}
                </a>
            </h3>
            {% if post.description %}
            <p>{{ post.description }}</p>
            {% endif %}
        </li>
        {% endfor %}
    </ul>
    
    <p><a href="{{ '/posts/' | relative_url }}">View all posts →</a></p>
</div>'''
        
        with open(self.output_dir / 'index.md', 'w') as f:
            f.write(index_content)
        
        print("📄 Generated index page")
    
    def generate_posts_index(self):
        """Generate posts listing page"""
        posts_content = '''---
layout: default
title: All Posts
---

<div class="posts">
    <h1>All Posts</h1>
    
    {% for post in site.posts %}
    <article class="post-preview">
        <h2><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
        <div class="post-meta">
            <time datetime="{{ post.date | date_to_xmlschema }}">
                {{ post.date | date: '%B %d, %Y' }}
            </time>
        </div>
        {% if post.description %}
        <p>{{ post.description }}</p>
        {% endif %}
    </article>
    {% endfor %}
</div>'''
        
        with open(self.output_dir / 'posts.md', 'w') as f:
            f.write(posts_content)
        
        print("📄 Generated posts index page")
    
    def migrate(self):
        """Main migration process"""
        print("🚀 Starting Hugo to GitHub Pages migration...")
        
        # Load Hugo configuration
        self.load_hugo_config()
        
        # Create output structure
        self.create_output_structure()
        
        # Process content
        content_dir = self.source_dir / 'content'
        if content_dir.exists():
            # Process posts
            posts_dir = content_dir / 'post'
            if posts_dir.exists():
                print(f"📝 Processing posts from {posts_dir}")
                
                for post_file in posts_dir.glob('*.md'):
                    post_data = self.convert_post(post_file)
                    if post_data:
                        self.posts.append(post_data)
                        
                        # Write Jekyll post
                        date_str = post_data['frontmatter'].get('date', '2021-01-01')
                        if isinstance(date_str, str) and len(date_str) >= 10:
                            date_prefix = date_str[:10]
                        else:
                            date_prefix = '2021-01-01'
                        
                        filename = f"{date_prefix}-{post_data['slug']}.md"
                        output_path = self.output_dir / '_posts' / filename
                        
                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write('---\n')
                            yaml.dump(post_data['frontmatter'], f, default_flow_style=False)
                            f.write('---\n\n')
                            f.write(post_data['content'])
                        
                        print(f"✅ Converted post: {post_file.name} → {filename}")
            
            # Process other pages
            for md_file in content_dir.glob('*.md'):
                if md_file.name not in ['_index.md']:
                    page_data = self.convert_post(md_file)
                    if page_data:
                        output_path = self.output_dir / f"{page_data['slug']}.md"
                        
                        # Set page layout
                        page_data['frontmatter']['layout'] = 'default'
                        
                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write('---\n')
                            yaml.dump(page_data['frontmatter'], f, default_flow_style=False)
                            f.write('---\n\n')
                            f.write(page_data['content'])
                        
                        print(f"✅ Converted page: {md_file.name}")
        
        # Copy static assets
        self.copy_static_assets()
        
        # Generate Jekyll files
        self.generate_jekyll_layouts()
        self.generate_jekyll_config()
        self.generate_index_page()
        self.generate_posts_index()
        
        # Generate basic CSS
        self.generate_basic_css()
        
        # Generate GitHub Actions workflow
        self.generate_github_actions()
        
        print(f"\n🎉 Migration completed!")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📊 Processed {len(self.posts)} posts")
        print(f"\n📋 Next steps:")
        print(f"1. Review the generated files in {self.output_dir}")
        print(f"2. Initialize a new git repository in {self.output_dir}")
        print(f"3. Push to GitHub and enable GitHub Pages")
        print(f"4. Your site will be available at: https://username.github.io/repository-name/")
    
    def generate_basic_css(self):
        """Generate basic CSS for the site"""
        css_content = '''/* Basic styles for GitHub Pages site */
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

header {
    border-bottom: 1px solid #eee;
    margin-bottom: 40px;
    padding-bottom: 20px;
}

header nav h1 {
    margin: 0;
    font-size: 2em;
}

header nav h1 a {
    text-decoration: none;
    color: #333;
}

header nav ul {
    list-style: none;
    padding: 0;
    margin: 10px 0 0 0;
}

header nav ul li {
    display: inline-block;
    margin-right: 20px;
}

header nav ul li a {
    text-decoration: none;
    color: #666;
    padding: 5px 10px;
    border-radius: 3px;
}

header nav ul li a:hover {
    background-color: #f5f5f5;
}

.post-header {
    margin-bottom: 30px;
}

.post-title {
    margin-bottom: 10px;
    color: #2c3e50;
}

.post-meta {
    color: #666;
    font-size: 0.9em;
    margin-bottom: 10px;
}

.post-tags {
    margin-bottom: 20px;
}

.tag {
    background-color: #f1f1f1;
    padding: 2px 8px;
    border-radius: 3px;
    font-size: 0.8em;
    margin-right: 5px;
}

.post-image img {
    max-width: 100%;
    height: auto;
    border-radius: 5px;
    margin-bottom: 20px;
}

.post-content {
    line-height: 1.8;
}

.post-content h1,
.post-content h2,
.post-content h3,
.post-content h4,
.post-content h5,
.post-content h6 {
    margin-top: 30px;
    margin-bottom: 15px;
    color: #2c3e50;
}

.post-content code {
    background-color: #f8f8f8;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: 'Monaco', 'Consolas', monospace;
}

.post-content pre {
    background-color: #f8f8f8;
    padding: 15px;
    border-radius: 5px;
    overflow-x: auto;
}

.post-content pre code {
    background: none;
    padding: 0;
}

.post-list {
    list-style: none;
    padding: 0;
}

.post-list li {
    margin-bottom: 20px;
    padding-bottom: 20px;
    border-bottom: 1px solid #eee;
}

.post-list li:last-child {
    border-bottom: none;
}

.post-preview {
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 1px solid #eee;
}

.post-preview:last-child {
    border-bottom: none;
}

footer {
    margin-top: 50px;
    padding-top: 20px;
    border-top: 1px solid #eee;
    text-align: center;
    color: #666;
    font-size: 0.9em;
}

/* Responsive design */
@media (max-width: 600px) {
    body {
        padding: 10px;
    }
    
    header nav ul li {
        display: block;
        margin-bottom: 5px;
    }
}'''
        
        with open(self.output_dir / 'assets' / 'css' / 'main.css', 'w') as f:
            f.write(css_content)
        
        print("🎨 Generated basic CSS")
    
    def generate_github_actions(self):
        """Generate GitHub Actions workflow for Jekyll"""
        workflow_content = '''name: Build and deploy Jekyll site to GitHub Pages

on:
  push:
    branches: [ "main", "master" ]
  pull_request:
    branches: [ "main", "master" ]

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.1' 
          bundler-cache: true 
          cache-version: 0 
      
      - name: Setup Pages
        id: pages
        uses: actions/configure-pages@v3
      
      - name: Build with Jekyll
        run: bundle exec jekyll build --baseurl "${{ steps.pages.outputs.base_path }}"
        env:
          JEKYLL_ENV: production
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v2

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v2'''
        
        # Create .github/workflows directory
        workflow_dir = self.output_dir / '.github' / 'workflows'
        workflow_dir.mkdir(parents=True, exist_ok=True)
        
        with open(workflow_dir / 'jekyll.yml', 'w') as f:
            f.write(workflow_content)
        
        # Generate Gemfile for Jekyll
        gemfile_content = '''source "https://rubygems.org"

gem "jekyll", "~> 4.3"
gem "minima", "~> 2.5"

group :jekyll_plugins do
  gem "jekyll-feed", "~> 0.12"
  gem "jekyll-sitemap"
  gem "jekyll-seo-tag"
  gem "jekyll-paginate"
end

platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data"
end

gem "wdm", "~> 0.1.1", :platforms => [:mingw, :x64_mingw, :mswin]
gem "http_parser.rb", "~> 0.6.0", :platforms => [:jruby]'''
        
        with open(self.output_dir / 'Gemfile', 'w') as f:
            f.write(gemfile_content)
        
        print("⚙️  Generated GitHub Actions workflow and Gemfile")


def main():
    parser = argparse.ArgumentParser(description='Migrate Hugo site to GitHub Pages')
    parser.add_argument('--source', '-s', default='.', help='Source Hugo directory (default: current directory)')
    parser.add_argument('--output', '-o', default='github-pages-site', help='Output directory (default: github-pages-site)')
    parser.add_argument('--install-deps', action='store_true', help='Install required Python dependencies')
    
    args = parser.parse_args()
    
    if args.install_deps:
        print("📦 Installing required dependencies...")
        os.system("pip install pyyaml toml")
        print("✅ Dependencies installed!")
        return
    
    # Check dependencies
    try:
        import yaml
        import toml
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: python migrate_to_github_pages.py --install-deps")
        return
    
    migrator = HugoToGitHubPagesMigrator(args.source, args.output)
    migrator.migrate()


if __name__ == '__main__':
    main()
