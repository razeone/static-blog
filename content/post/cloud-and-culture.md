---
title: "Cloud and Culture or Why enterprises fail on Cloud adoption?"
date: 2021-05-31T14:14:34-05:00
draft: true
thumbnail: "images/anti-type-a.png"
tags: ["agile", "devops", "enterprise", "cloud"]
categories: ["devops", "cloud"]
---

Hi everyone, I hope you're having a great time during this pandemic or at least staying healthy and safe enjoying your 127.0.0.1.

In my case I've been studying, dealing with anxiety, changing routines for all that stuff that we considered as normal life before this lockdown. Also this pandemic came with the opportunity to change my current job, I got the opportunity to land a technical manager offer at a big insurance enterprise which later I declined in favor of sticking to my technical career.

As a cloud solutions architect I mostly dealt with technical challenges, however, those challenges are commonly solved by the patterns in the architecture proposal, some workaround, open source or propietary solution, in the technical side there's always a way to solve most of the problems that we face.

On the other hand, when we talk about cloud adoption, digital transformation and culture, this is a different story since now the thing that must be placed in the middle of the discussions is people. I know this is not new, this is one of the core messages of the [agile manifesto](http://agilemanifesto.org/) and is some of the mantras of the lean startup communities, however, as technologists or leaders, we sometimes tend to focus on different stuff.

Basically I'd like to summarize the behaviours/anti patterns and challenges that I've seen through my professional experience on helping enterprises adopt new technologies like cloud computing in this case.

## Technology over People

As I've mentioned, as technologists, architects, developers, technical and non technical managers, engineers and technical teams, we're always exposed to tons of documentation, blog posts, advertisements and all kind of sources of information for new and trendy technical stuff, and of course is too complex to stay on top of all the new things from methodologies to the new killer framework that will solve all our problems. I'm not lying when I say that I sometimes get hited by the imposter syndrome when I start thinking in the finite time available for learning vs. the amount of topics I want to learn about, in addition to the pressure of our bosses for a fast delivery of features, depending what's the expected outcome on our BAU work.

I cannot count the several times that I've seen people concerned of speaking out loud the new buzzword they just learned instead of really understanding what's the problem this tool or methodology is trying to solve and if it works for my enterprise. Most of the projects I've seen to fail have in common this lack of understanding of the tool/method that is trying to introduce to the company.

This reminds me this project in a banking corporation that I collaborated with. It was an API for targeted advertising, basically it was a [Lambda function](https://aws.amazon.com/lambda/) behind an [API gateway](https://aws.amazon.com/api-gateway/?nc1=h_ls) on AWS consuming a [MySQL database on RDS](https://aws.amazon.com/rds/), good, right? Except for the RDS, all serverless technologies cut the operational load and everything seems great, don't you think? Wrong!

This project had the problem that by the number of requests, we reached the bottleneck of the relational database. You might think, come on, you just need to scale up or scale out the database to solve that issue, well technically yes but let's rethink this again. This piece of software was developed by someone who clearly was comfortable writing complex SQL queries and joins to make applications work, but what if you think about a different solution like using [DynamoDB](https://aws.amazon.com/dynamodb/), this of course changes all your project, but this seems to be the more cloud native solution to the heavy read problem, I know there are some other limitations on using key value stores vs. a RDBMS, but if you think in a more "cloudy" way, then you know that you can address those limitations in code and have a better control in this fully serverless scenario. The main problem here is that instead of having a big picture and overview of the options, we tend to just think that moving to the cloud is just using the same approaches that we used before the cloud, and it's ok, that's one option but again, if this is a whole new project that doesn't need to stick to a legacy application, then let's do it in the most scalable and operationally optimal way. That's something that people solve, not technology. Choosing the best tool only reflects the better understanding of the options out there and 

Another problem was that since this was a fairly simple codebase (one single lambda) the managers of the project only wanted to hire one or two junior devs. It's ok if you have someone helping them how to discuss issues in a project of this nature, however, if you have a single lambda built by a person that lacks of experience it will probably end up in a bad way and yes it was. I'm not saying that junior devs are bad and need to be mentored all the time, instead I'm saying that if you put someone to write code and you don't give any other guidelines, this person is going to do exactly that, and what was the result? A single lambda function of around 2k lines, written in Python 3 but with a syntax inspired by C (this was first created by a C developer), that constructs complex queries on the fly, that no one understands, with several nested ifs and nested loops that truly begs for a refactor. The problem here is again, people that had no idea of the complexity behind this, thought it was a good idea to save money in that way, and then, when the project needed a new feature because the C dev that was there left the position in favor of becoming an embedded engineer, nobody is able to even try to make a small change to that ugly spaghetti. What was the solution? Ironically money, by scaling up things, eventually they reached the desired performance, but instead of investing in the people who can make this really happen, they decided to pay more money to the provider for until the end of time.

## Tools over Culture

This idea is actually pretty similar to the previous one. But in this case you have:

* Bosses that are aware or at least they've heard of the benefits of using X tool or methodology
* Practitioners of that tool/method
* Some experience even if is so little

This is awesome, I think this is one of the best ways of achieving good results, by getting the hands dirty. There's a famous saying here in Mexico that says: "El diablo está en los detalles" ("The devil is in the details"), and it's so true. You can have all this good intentions, good projects, amazing tools backed by an amazing team but if you don't look deeper into the details, the implementation can fail as well.

I'm going to rephrase the idea for: DevOps Tools over DevOps Culture

## Sticking with the legacy mindset

Again in this banking company there was an aggressive initiative for adopting DevOps Tools. There was two [Jenkins](https://www.jenkins.io/) tenants, an [Artifactory](https://jfrog.com/artifactory/), [Jira](https://www.atlassian.com/es/software/jira), [Confluence](https://www.atlassian.com/es/software/confluence), [BitBucket](https://bitbucket.org/) and all that shit well-connected and integrated. Sound great, right? Well yes but what if the process don't matches the tools? This company focused on having all this tools available for supporting the transformation which is an enormous effort and an amazing challenge, but this initiative lacked of moving the SDLC to a more agile way supported by this tools.

The process of sending a new change or feature was still slow and bureaucratic. I'm going to describe it a little:

* You push your code to the SVC
* You create a project on an internal tool that associates your code with a Jenkins project
* The pipeline is being provided by the company (nice!)
* This pipeline only builds your project and executes some static analysis on it

The outcome of this pipeline is only a report of your code using [SonarQube](https://www.sonarqube.org/), but then where's the CI/CD on this Jenkins? Ok, maybe that comes after I pass all this tests, wrong!

After compiling and passing all tests defined for that kind of projects, you have to promote your code on an internal tool to deploy it in dev and staging. Great, an extra manual step, I can live with it if is only one, wrong!

Once you deploy to this non productive environments, you have to create a Jira issue to ask to a different area to perform load testing against your code to confirm it will behave good in production, cool since this sound like a process that must be automated then probably will take so few time, wrong!

This process was completely manual and the outcome of this process is to generate a report where they confirm your code and queries and behave correctly, this for when you followed best practices, otherwise they will send a report where they don't recommend using your code in production and you're back to level 1. This process takes one week approximately since you have to give test data and other inputs.

After having a report stating that your code is ok and passes all tests, then you have to promote your code again, but this will happen only on Thursdays (for some reason), so if you have this on Friday, you have to wait one week to see your code in production.

As you see, even having all the tools that support a really agile and DevOps culture, it doesn't mean that you don't have to double-check your existing processes and people doing this, I bet the people executing load testing against this components, would be happy to just verify the result of this tests as part of a whole pipeline and giving a binary answer that doesn't necesarily need a people in between manually writing tests and come and by through email if thing don't go as expected.

## Be careful of The Cobra Effect

When you decide to start your cloud journey, one of the first things that happen is to define [KPI](https://en.wikipedia.org/wiki/Performance_indicator) or [OKRs](https://en.wikipedia.org/wiki/OKR) or at least goals for the project. However, if the targeted metrics are not well-defined, those will not show your expected outcome, let's make an example.

If you define "migrate all the applications to the cloud by the EOY" as an objective, you're going to have a complete and total mess. Because again, you're not focusing on people neither the technology, you're just saying that by migrating things to the cloud you're solving something, nobody knows what but they have to make those goals because that's how they're being measured.

## WDD (Whim Driven Development)

Another absurd goal I've seen before is: "migrate our most critical applications to the cloud". When a vendor says you can build high available and resilient applications on the cloud it doesn't mean this comes out of the box by using the cloud, so you probably don't want to start learning the cloud arts with a huge project that will probably take more than 6 months to complete or at least to give you measurements that you can translate into business outcomes. I know it sounds conservative tell you avoid big first projects, and that's not the real point, if you have the people and the skills then go for it tiger, but read again; people and skills. A good starting point for organizations adopting the cloud would be to have your technical staff have some training on cloud technologies and patterns. Then maybe recap on what's available and what can work on our industry/company if the first project is a success you'll gain momentum and credibility, in opposition to have one big project fail that will en up in a reduced trust on the technology and of course in the abilities of your team for execution.

And the last, most controversial and the most wrongful idea I've heard when talking about cloud computing: "With cloud you can save lots of money". Let's step back with this idea before we get into more details. If you're planning to introduce a new trendy technology to your company, this is not going to be cheap at all, trust me. I know there's a lot of vendor white papers and documentation saying that by using the cloud you can in advance forecast the costs for your project, and yeah I think this is in some way can be done, however, always there's hidden costs behind new tech adoption, as I mentioned before, training, support and licensing costs almost always will be there. Also if you're planning on modernize an application for move it to the cloud, again, this is not going to be cheap, almost all migrations have a double spend in some moment, because you have to support the legacy and the new infrastructure and as soon as you create a single machine within any cloud provider then the cost starts to grow. Another misunderstood pattern for cloud is elasticity, some people belive that cloud is out of the box elastic, and well that's true in a serverless scenario, but not with IaaS unless you configure it to behave in certain way that YOU need to define. When I worked at this big support company with an R in its logo, there was a lot of costumers genuinely surprised on why their application crashed since they're running in the cloud and the cloud is supposed to be resilient, well yes if you architect it in that way. The same applies on costs, I found a lot of customers paying lots of money by not defining the right metric to monitor for auto scaling or by just scaling up or out in respond to demand, instead of going deeper on the actual causes of slow response times or latency for example. And once again, this is lack of knowledge, enterprises need to have forums where people can ask questions to experts and clarify all the questions they have to be successful in adopt some method.

## Not empowering DevOps practices or Avoiding the Agile practices adoption

DevOps culture encourages autonomous teams, if you don't remove the wall between Dev and Ops, you're going to have your same legacy culture but with new tools. There's a huge talk on this topic specifically on how DevOps teams should be implemented in organizations see [DevOps Topologies](https://web.devopstopologies.com/).

There's a lot of different team configurations and roles that you can adopt in order to start moving things to a more agile and DevOpsy way of delivering software and outcomes in general. But again, any decision that you make inside your organization should be the result of analyzing all available options vs. the current state and the necessary steps to make the defined goal. And not only saying let's use DevOps, install a CI/CD tool and plug it into anything.

DevOps birth happened inside agile community, therefore you should step back a little when you talk about it, I mean. Does your company already uses other agile methods or practices? If no, then probably that's a good starting point, by understanding what's the benefit of using them, once you have the full picture, then you probably want to adopt some of those techniques or maybe create your own way of doing DevOps, Agile, Scrum or SRE. It all depends on the people executing those tasks, maybe X framework lacks of some artifact or doesn't adapt well to your oganization's needs, then maybe you need to create your own flavor of SAFe or Scrum. Also please bear in mind that all this methodologies are there as a reference, a company that has decided to use new tools for a business need should be flexible enough to define if a given method is useful or not for their culture.

## Final thoughts

Sorry for all this verbose complaints based only on my experience. I know there's out there more serious studies about cloud adoption and agile methodologies in big companies, however, I felt the need of framing some of the most common scenarios that I've seen during this years of using cloud technologies and all the hype and myths behind it. I hope you find it insightful and at least help you see thing differently or help your company don't commit all this mistakes. Also this is not intended to become a guide or essay on why I hate big old companies, I do love work for them, and I understand all of us are struggling with the idea of being the early adopters when we see our competition doing amazing stuff with new things, but the only thing I say is that big companies need to focus develop the people that will be executing their vision.