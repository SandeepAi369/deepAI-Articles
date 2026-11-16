---
title: "# How I Fixed Two Hidden Bugs in wreq While Updating My Search Engine"
date: "2026-11-16"
category: "OpenSource"
---

<img src="https://res.cloudinary.com/dxlok864h/image/upload/v1794841838/xel-studio/articles/om7fw8gdosexun5cpgeh.png" alt="# How I Fixed Two Hidden Bugs in wreq While Updating My Search Engine" width="100%">

# # How I Fixed Two Hidden Bugs in wreq While Updating My Search Engine

*Nov 16, 2026*

Recently I contributed to wreq, a fast Rust HTTP library. It started while I was updating my open source Rust search engine SearchWala and testing some of its core libraries. Since SearchWala relies on wreq to fetch web pages, I decided to check the library from a security and reliability angle. The main engine for browser profiles and network requests worked great, but when I looked closely at the cookie and connection layers, I found two real problems.

* **Cookie security and memory cleanup.** Websites should not be allowed to set cookies for broad public domains like .com or .co.uk because that can leak data across unrelated sites. I added checks to block these broad cookies. Also, in a long running app like a search engine, expired cookies were piling up in RAM and every request scanned the full cookie list. Now expired cookies get cleared automatically to free memory, and lookups only check relevant domains instead of scanning everything.
* **Reusing connections on redirects.** When an HTTP/1.1 server sends a redirect with extra response data, dropping it right away leaves leftover data on the connection and forces the client to close it. I updated wreq to clear up to 256 KB of that leftover data before following the redirect so the same connection stays clean and can be reused for the next request.

I originally sent both fixes together, and at the maintainer's request, I split them into two separate pull requests with proper tests. The cookie security and memory cleanup fix is now merged and pushed as the latest commit aa9644f on the main branch, while the redirect connection reuse fix is still open for review.

* Merged cookie security and memory cleanup fix https://github.com/0x676e67/wreq/pull/1389
* Open redirect connection reuse fix https://github.com/0x676e67/wreq/pull/1390

Checking the libraries you depend on in your own projects is a practical way to catch real issues and make open source software safer and faster for everyone. Both pull request links are included here if you work with Rust or HTTP clients and want to check out the code.
