---
title: "Major Upgrade in Rising Chat AI – Advanced SearXNG Search Integration "
category: "Ai"
---

![Major Upgrade in Rising Chat AI – Advanced SearXNG Search Integration ](https://res.cloudinary.com/dxlok864h/image/upload/v1773601059/xel-studio/articles/dqwhlwilxnje5b51rkwx.jpg)

# Major Upgrade in Rising Chat AI – Advanced SearXNG Search Integration 

I’ve introduced one of the biggest upgrades to Rising Chat AI: a fully customized SearXNG search integration.

What is SearXNG?
SearXNG is an open-source meta-search engine. It allows AI systems and LLMs to access the internet by collecting results from multiple search engines at the same time. This helps the AI analyze many sources, instead of relying on a single limited API.

Normally, SearXNG is designed to run locally on a personal server or local machine. Running it on a public server is very difficult because search engines quickly detect repeated, automated requests from a single IP address and start blocking them. So, simply hosting it online without modifications usually doesn’t work.

How We Solved It
To solve this, I redesigned and optimized the system so it can run reliably on a hosted environment like Hugging Face Spaces. Without these changes, the system would quickly get blocked and stop returning results. 

To make it stable, I implemented two important techniques:
* IP Rotation: Every search request goes through different proxy IP addresses, so the main server doesn’t get blocked by search engines.
* User-Agent Rotation: For each request, the browser identity automatically changes. This makes the traffic look like normal human browsing instead of a bot.

Simple Example
Imagine one person asking Google 100 questions in one minute from the same device. The system will quickly detect it as automated traffic and block it. But, if those requests come from different locations and different browsers, it looks like normal users searching the web. That is exactly how this system avoids detection and keeps running smoothly.

Why This Upgrade Was Necessary
Previously, Rising Chat AI relied on the Tavily search API, which had strict limits:
* It allowed only 10 sources per query.
* It had a 1,000 total search limit.

With the new private SearXNG integration, Rising Chat AI can now do much more:
* It can scan over 50 sources for a single query.
* It can support up to 200 sources when needed.
* It delivers far deeper and more accurate answers.

Hosting & Integration
I deployed and optimized this system on Hugging Face Spaces using Turant infrastructure, running 24/7. This upgrade is already integrated into Rising Chat AI. In the future, we will also integrate it into Xel Studio.

What This Means for Users
If you have used Rising Chat AI before, you will instantly notice the improvements:
* Up to 2x better answers.
* More accurate information.
* Much wider source coverage.

I built and optimized this system to make Rising Chat AI smarter, faster, and far more powerful.

Try It Now
Telegram bot link: (@Risingstars33_bot)