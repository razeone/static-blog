# static-blog

This is my personal blog using Hugo + S3 + CloudFront + Lambda.

## Quickstart

```bash
git clone https://github.com/razeone/static-blog.git
cd static-blog/
git submodule init
git submodule update
hugo serve -D
```

## Docker Quickstart

```bash
docker build . -t raze-website:<daVersion>
docker run -p 8080:80 localhost/raze-website:<daVersion>
```