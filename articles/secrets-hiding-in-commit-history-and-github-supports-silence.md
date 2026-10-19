---
title: "Secrets hiding in commit history, and GitHub Support's silence"
date: "2026-10-19"
category: "Security "
---

<img src="https://res.cloudinary.com/dxlok864h/image/upload/v1792407562/xel-studio/articles/qhvzdxbmsq8pqmdtsnvd.png" alt="Secrets hiding in commit history, and GitHub Support's silence" width="100%">

# Secrets hiding in commit history, and GitHub Support's silence

*Oct 19, 2026*

For the past 3-4 days, I've been waiting for GitHub Support to respond. No reply so far.

Here's what happened. A Cerebras free API key got leaked in one of the commits of my previous project. It wasn't in the code, only in the commit history. Not a huge risk, and I've already removed that key.

After that, I rewrote the entire commit history and fixed it with a force push. But even after a force push, old commits can still remain cached on GitHub, and removing them completely requires GitHub Support. So I emailed them and also raised a ticket. It's been 3 to 4 days. I've checked my mail and everywhere else, and there's been no response from their side.

To me, this isn't just my problem. It's a much bigger one.

In private repos, we often code in a hurry. In those moments, some things get hardcoded and accidentally committed. Later, when we open source the project and make it public, those secrets stay quietly hidden in the commit history. That gives attackers an easy opportunity, straight from the commit history.

I regularly see that most attacks happen because of credential leaks. Leaks in code are somewhat less common, but in commits, I see them far too often.

That's why I believe GitHub and Microsoft need to work on this. When a developer comes forward on their own to clean up a leaked secret, Support should be quick to help. If this continues, the cost will be paid by developers and users alike.

Has something like this ever happened to you?

#GitHub #CyberSecurity #OpenSource #DevSecOps