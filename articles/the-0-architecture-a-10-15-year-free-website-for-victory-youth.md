---
title: "The ₹0 Architecture: A 10-15 Year Free Website for 'Victory Youth"
---

<img src="https://res.cloudinary.com/dxlok864h/image/upload/v1790439841/xel-studio/articles/d3b46b5uxxl2ar5rw58c.png" alt="The ₹0 Architecture: A 10-15 Year Free Website for 'Victory Youth" width="100%">

# The ₹0 Architecture: A 10-15 Year Free Website for 'Victory Youth

'Relying on paper receipts for community donations is highly impractical. Every festival season brings the same chaos—lost notes and untraceable calculations. At scale, this isn't just about money; it's about memory and trust. Due to an urgent requirement, I needed a permanent, foolproof system for "Victory Youth," a youth group I am personally part of. The brief was simple: securely store and categorize every donation permanently. I built the entire project using Next.js (my strictly preferred JavaScript framework) with one goal: build a heavy-duty digital platform that runs for the next 10-15 years on a strict zero-budget—not as an afterthought, but as the core architecture.

Like my previous project, Xel Studio, everything is managed from a private backend admin panel, keeping the frontend completely transparent. To ensure maximum performance without server bloat, the backend is smartly divided:

* Database (CockroachDB / PostgreSQL): Handles all text data, queries, and donations. It provides 10GB of free space—virtually impossible to exhaust with just text entries, even in a decade.
* Images (Cloudinary): To prevent main database overload, media storage is completely separate. Cloudinary’s dedicated CDN automatically optimizes images, giving us a fresh 15GB of free space.

Combined, we secured 25GB of premium cloud space—completely replacing paid hosting, bandwidth, and media delivery—hosted entirely free on Cloudflare's default domain. To handle heavy traffic smoothly, I used Cloudflare Hyperdrive. Let's be real: without caching, a sudden rush of database requests will quickly exhaust free-tier limits and overload the system. Hyperdrive smartly 'caches' data on the server side. (By the way, while this uses Cloudflare, Xel Studio is integrated with Google's Firebase for brilliant in-browser caching). Both methods ensure that even if a massive wave of users hits simultaneously, they instantly see saved data without repeatedly pinging the main database. The site stays lightning-fast and entirely risk-free.

I’ll be brutally honest—I am deep into the R&D of my massive main project, "Neuro Trap," and I strictly avoid taking on web development for outside clients. It pulls too much focus away from my work. However, I made exactly two exceptions:

* The Only Two Exceptions: I paused my work solely for our family business website, and this Victory Youth project. Building a solid system for my own people was non-negotiable.
* The MIT License Future: Designing for zero cost from day one proves you can build something genuinely reliable. Given its robustness, I will eventually open-source this codebase under the MIT License so any NGO or developer can build a zero-server-cost website for free.

Since this site isn't on Google Search Console yet, it won't appear in direct searches. 

Website link https://victory-youth.sandeepmudhiraj7500.workers.dev/