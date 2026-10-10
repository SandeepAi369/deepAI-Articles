---
title: "A Narrow Escape from a Supply Chain Attack"
---

<img src="https://res.cloudinary.com/dxlok864h/image/upload/v1791634198/xel-studio/articles/fg5ptwmrmohxl8gg8jfw.png" alt="A Narrow Escape from a Supply Chain Attack" width="100%">

# A Narrow Escape from a Supply Chain Attack

A simple act of procrastination saved my entire system from getting hacked. I was researching open-source projects for free LLM access and found one called Red Team LLM. It reversed the web frontends of Chinese models like Kimi and DeepSeek to generate a free OpenAI-style API. I researched this project about a month or two ago and thought about cloning it for my use, but I decided to put it off for a few days, and that hesitation saved me.

* When I resumed my research later, I discovered the project had suffered a severe supply chain attack starting in April 2025 through a force-push on their GitHub repository.
* On May 5, 2025, Aikido Security revealed that a remote access trojan was hidden inside an npm package, giving attackers full system control.
* When someone cloned and installed the project, this trojan would secretly infiltrate the system, create a hidden folder in the home directory, and connect to a C2 server. This allowed the attacker to run remote shell commands, steal files, and take complete control of the machine.

To their credit, the original author did actually issue a clear warning about the compromise to alert the users. Fortunately, such severe malicious attacks and compromises are actually very rare in the broader open-source community. If we look at how this project actually operates behind the scenes, it is fundamentally a clever example of reverse engineering. It bypasses the restrictions of the official websites providing those models and generates a working API for users.

* Users have to extract cookies from their own web browser and input them directly into the project.
* When a question is asked through an AI agent, this tool acts as a middleware and uses those extracted cookies to send a direct request to the official provider's server.
* It then takes the response and returns it to the agent formatted perfectly as a standard OpenAI request.

Using unofficial API tools always looks tempting because you get expensive models for free, but the hidden dangers are massive. You should always check the recent repository activity, dependencies, and security alerts before cloning any open-source project. This time, a slight delay saved my system, proving that instead of rushing in blindly, taking a little time to research before making a decision is always the right approach.