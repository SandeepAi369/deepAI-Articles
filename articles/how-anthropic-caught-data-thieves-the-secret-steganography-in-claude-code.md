---
title: "How Anthropic Caught Data Thieves: The Secret Steganography in Claude Code"
category: "Security"
---

<img src="https://res.cloudinary.com/dxlok864h/image/upload/v1784480008/xel-studio/articles/hr22et5mccyaarpqyyso.jpg" alt="How Anthropic Caught Data Thieves: The Secret Steganography in Claude Code" width="100%">

# How Anthropic Caught Data Thieves: The Secret Steganography in Claude Code

The controversy started when Anthropic accused Chinese labs, especially Alibaba, of using 25,000 fake accounts to steal Claude’s data 28.8 million times in just 44 days. To stop this, Anthropic added a hidden steganography feature that triggered a big privacy debate.

What is Steganography?
It is the technique of hiding secret data inside normal-looking text or files so that it works completely in the background without the user ever knowing it exists.

The Game of Hide & Seek: A Simple Example

Suppose I am Sandeep, a user in China. Since Claude is banned here, I connect to a Singapore proxy server to bypass the block.

* Before the Update: I type “Hello” and send. My message goes through the Singapore server to Anthropic. Because there are no hidden marks in Claude Code, they only see the proxy server. I am completely invisible.
* The Steganography Update: Anthropic noticed repeated, suspicious requests from proxies but couldn't prove who was behind them. To fix this blind spot, they quietly pushed a software update to Claude Code containing a hidden steganography feature.
* After the Update: Now, as soon as I type "Hello" and send, Claude Code checks my system's time zone in the background. If it detects China, it secretly swaps a standard apostrophe in the hidden system prompt (like "Today's date is") with visually identical but technically distinct invisible Unicode characters. These hidden marks basically tell Anthropic: "Hey, this is a Chinese user."
* The Catch: The request still routes through Singapore, but when Anthropic receives it, they read those hidden marks. They completely bypassed the proxy by putting this logic directly inside Claude Code.

How It Was Exposed & My Opinion

* I use Claude Code every day. Large-scale data theft by Chinese companies is 100% wrong, and Anthropic has every right to protect its hard work.
* However, secretly implementing steganography in a user's local Claude Code application raises big trust issues. For a company calling itself the most ethical AI lab, doing this without telling anyone disappointed many developers.
* This feature was exposed on June 30, 2026, by independent developers LegitMichel777 and Thereallo while checking the code for a different reason. Otherwise, it might still be a secret today.

This incident highlights a key tension in AI. Companies must defend against massive theft, but secretly putting steganography in Claude Code breaks user trust. Better communication is the way forward. Security should not come at the cost of transparency.