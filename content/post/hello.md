---
title: "Hello world!"
date: 2021-01-29T16:39:29-06:00
draft: false
thumbnail: "images/golang-gopher.jpg"
tags: ["markdown", "static website", "hugo", "cloudfront"]
categories: ["first", "general"]
---


Hello internet :smile: it's being a long time since I stopped blogging, however, as I've always said, writting is more a necesity than a luxury.

Today I'm gonna talk about the tech stack I'm using for blogging, In the past I've used [Ghost](https://ghost.org/) for my previous blog, and a long time ago I also used [Joomla!](https://www.joomla.org/), those are great tools and a lot of technical writters do use Ghost for writting articles, or blogging. Also I remember there's [Jekyll]("https://github.com/jekyll/jekyll") and [Octopress]("http://octopress.org/") out there, but this time I'll stick to a command line, Markdown friendly golang tool.

Today I'm using [Hugo](https://gohugo.io/) backed by AWS [S3](https://aws.amazon.com/s3/)/[CloudFront](https://aws.amazon.com/es/cloudfront/).

## My new Stack and Why?

NodeJS and PHP blogging platforms and CMS are great, however for hosting that kind of websites I have to spin up a container or a VM on AWS or any cloud platform, previously I had my platform hosted on [Linode](https://www.linode.com/) using the cheapest VM that costs $5 USD/Month, but that's $60 USD yearly which is expensive just for showing my ideas on the internet, yeah it's expensive for me cause that's up to $1200 MXN a year plus other services.

So I started thinking on creating a serverless blogging platform backed by [AWS Lambda](https://aws.amazon.com/lambda/) [API Gateway](https://aws.amazon.com/es/api-gateway/) and [DynamoDB](https://aws.amazon.com/dynamodb/), but even if I fit on the free tier, I'd need to write the CRUD for the posts model, and I'm still on a risk of getting lots of request and I'd end up paying lots of money for the API GW and also the pricing model for DynamoDB is risky since you have to provision read/write units and you still have to pay, even since it does exist the on-demand pricing model that can also become an endless hole. And since in my experience I've seen a lot of people spending money on the cloud I'm trying to minimize spending in every possible way.

### Enter the S3

With S3 you can have website hosting, which according to the AWS' documentation:

> Q: How much will it cost to host my website?

The total cost of hosting your personal website on AWS will vary depending on your usage. Typically, it will cost $1-3/month if you are outside the AWS Free Tier limits. If you are eligible for AWS Free Tier and within the limits, hosting your personal website will cost around $0.50/month. To see a breakdown of the services used and their associated costs, see Services Used and Costs.

Plus I don't have to manage/patch any server.

Downsides:

* For hosting a website on S3 **you have to make your objects public**, which is not always a best practice since you could potentially have something stored on your bucket that you don't want to share with the public
* **No SSL**: your objects can be accessed through SSL/TLS but the static website hosting is restricted to HTTP

### Solution: CloudFront

If you publish your website using CloudFront, you can use an OAI to [make your bucket's objects only visible to your Cloudfront distribution](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html), in that way you don't have any security hole, since with CloudFront you can use an alternate domain name and also use an SSL certificate created through ACM.

Now that I have my secure hosting platform, I need to generate a static website blogging platform.

### Here comes Hugo

According to Hugo's features documentation:

> Hugo boasts blistering speed, robust content management, and a powerful templating language making it a great fit for all kinds of static websites.

In general:

* [Extremely fast]("https://github.com/bep/hugo-benchmark") build times (<1 ms per page)
* Completely cross platform, with [easy installation]("https://gohugo.io/getting-started/installing/") on macOS, Linux, Windows, and more
* Renders changes on the fly with [LiveReload]("https://gohugo.io/getting-started/usage/") as you develop
* [Powerful theming]("https://gohugo.io/themes/")
* [Host your site anywhere]("https://gohugo.io/hosting-and-deployment/")

So it basically covers all I need, it's markdown based which makes it great for not writting HTML at all, it has code highlight features and it doesn't require an application server at all.

Now I need to get profficient on this tool, so going through the [Quickstart]("https://gohugo.io/getting-started/quick-start/") seems like a good start. After going through that Tutorial I have choosen the minimalistic [anatole theme]("https://themes.gohugo.io/anatole/") and configured it with my own information, I had to copy the Google Analytics code and created a new [Formspree]("https://formspree.io/") to have the contact form working, so I basically did:

```
# Install hugo
brew install hugo
hugo new site static-blog
cd static-blog
git init
git submodule add https://github.com/lxndrblz/anatole.git themes/anatole
hugo new posts/hello.md
hugo server -D
```

The previous commands got me with a fully functional blog, now I need to set up all the stuff that the theme provides. Like enabling emojis :heart:, set up all the folders structure and also remove the unecessary example contents.

After that I need to deploy my website by:

```
hugo -D
# This will build the site and place it in the public folder
aws s3 sync public s3://my-secret-bucket/blog
```

After that I need to wait a little in order to get Cloudfront read from the S3 origin and my blog will be all set up :smiley:

So I'm basically gonna start learning how to get the most of this amazing tool since it seems great at first sighty and of course I'm going to document everything in here, so please standby :grin:

### Update

Please have a look to [this new post](/post/hugo-cloudfront/) since the fully functional Hugo website is described right there.

Also please note that currently [there's no free tier for Lambda@Edge](https://aws.amazon.com/lambda/pricing/#Lambda.40Edge_Pricing) so this new component increases the costs of this solution by:

> $0.60 per 1M requests

Keep that in mind.

So the overall costs for this solution at the moment is: $1.10 USD each month, around $22.0 MXN.