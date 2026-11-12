---
title: "A Sudden Policy Change Wiped Our Entire Database: How I Rebuilt a 10-15 Year Free Website on a ₹0 Architecture"
date: "2026-11-12"
category: "Website"
---

<img src="https://res.cloudinary.com/dxlok864h/image/upload/v1794522332/xel-studio/articles/npxax9x7wkhusclzhr9c.png" alt="A Sudden Policy Change Wiped Our Entire Database: How I Rebuilt a 10-15 Year Free Website on a ₹0 Architecture" width="100%">

# A Sudden Policy Change Wiped Our Entire Database: How I Rebuilt a 10-15 Year Free Website on a ₹0 Architecture

*Nov 12, 2026*

A few days ago, I shared a platform I built for "Victory Youth" to replace the chaos of paper donation receipts with a secure digital system. The primary goal was to build a heavy duty architecture designed to run for the next 10 to 15 years on a strict zero budget. Initially, everything was set up perfectly using Next.js, CockroachDB (10GB free), and Cloudinary (15GB). However, CockroachDB abruptly removed its free tier without clear notice, and the entire database was wiped out.

* Instead of a setback, I used this as a practical step for resource optimization, completely migrating the architecture from PostgreSQL to SQLite.
* To get that 10GB of free storage back without spending any money, I combined Cloudflare D1 (5GB) and Turso (5GB).
* Media storage remains completely separate via Cloudinary, protecting the main databases from bloat.

Sudden vendor changes are common, so continuous research and adaptability are critical. I strongly believe in building genuinely reliable systems, which is why the Victory Youth project is now completely public and open sourced under the MIT License. 

* 100% Free Hosting and Domain: The website is hosted entirely on Cloudflare, and there are absolutely no domain charges because it utilizes Cloudflare's free default .workers.dev domain.
* Traffic Management: Cloudflare Hyperdrive handles smart server side caching, ensuring the databases never get overwhelmed during heavy traffic.
* Easy Setup: A huge thanks to contributor @canakyuz for adding a simple, screenshot based guide to help non technical users set this up effortlessly.

Going forward, my focus is shifting heavily toward backend and low level systems, so you might only see one web release from me next year if strictly necessary. (The GitHub repository and the direct live website link are in the comments section below)

If you were in my position when the database was wiped out, what would you have done? Would you have been irritated, or would you have taken it as the next challenge and fixed it?

Website link https://victory-youth.bswd.workers.dev/

GitHub link https://github.com/SandeepAi369/victory-youth/tree/main
