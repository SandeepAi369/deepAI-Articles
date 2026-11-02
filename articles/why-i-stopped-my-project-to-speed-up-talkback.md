---
title: "Why I Stopped My Project to Speed Up TalkBack"
date: "2026-11-02"
category: "TalkBack accessibility"
---

<img src="https://res.cloudinary.com/dxlok864h/image/upload/v1793616443/xel-studio/articles/hcgycn78d85rrqtmsyux.png" alt="Why I Stopped My Project to Speed Up TalkBack" width="100%">

# Why I Stopped My Project to Speed Up TalkBack

*Nov 02, 2026*

*What I learned about Google's public TalkBack code*

Author: Sandeep | Published: November 2026

## Who this report is for

Developers, students, researchers and users who are thinking about contributing to TalkBack's public code or building on top of it.

## The short version

I wanted to make TalkBack, the Android screen reader, respond faster by rewriting part of its code. I tested the idea and then dropped it. The main reason is not technical. I do not think TalkBack's public code is maintained well enough to be worth contributing to.

## What I assumed at the start

I assumed that the open-source code on GitHub and the TalkBack app on the Play Store were the same version, and that Google kept GitHub updated whenever it updated TalkBack. So I downloaded the code from GitHub and built it as an app. I believed that the timings I measured on my build would be accurate for the real TalkBack that people use.

## What I planned and how I tested

TalkBack reads the screen aloud for visually impaired people. When you swipe, it works out what to say and hands the words to the phone's speech engine, which makes the voice.

The public TalkBack code has roughly 437,000 lines. About 208,000 of them are Braille support code taken from other projects. About 225,000 lines are TalkBack's own code that runs on the phone, mostly in Java. I did not want to change all of that. I wanted to improve one small part of about 5,000 lines: the part that receives your swipe, decides what to say, and sends the words to the speech engine. This part decides how fast the screen responds. I guessed that Java's background memory cleanup might add small delays there, so I planned to rewrite it in Rust, a language with steadier speed.

I added timers to the code. One starts when TalkBack receives a swipe. The other stops just before TalkBack hands the words to the speech engine. I tested on a Xiaomi Poco M3 running Android 12 and took 25 measurements while swiping through Settings. I did not measure the time the speech engine needs to make the voice, or the time for the sound to play.

## What I measured

| What I measured | Result |
|---|---|
| Fastest swipe | 38 milliseconds |
| Slowest swipe | 73 milliseconds |
| Changing to a new screen (one example) | 84 milliseconds |
| Average of 24 measurements | 51 milliseconds |
| Very first speech after turning TalkBack on | 2.2 seconds, one time only |

TalkBack's own part takes about 50 milliseconds, one twentieth of a second. The first speech was slow because the speech engine was starting up, which happens once. The speech engine usually needs 50 to 200 milliseconds to make the voice. That is a typical figure, not something I measured. My estimate is that a rewrite would save at most 20 to 30 milliseconds.

## What I found on GitHub

The TalkBack code on GitHub has only about 30 updates in 11 years, and the latest was in March 2026. Almost every update is labelled "Push to GitHub" with a date, and each holds many months of changes added at once. The page lists 18 open pull requests, which are proposed changes from outside people. I did not see any of them being merged, though I did not check each one.

| | Built from public code | Play Store version |
|---|---|---|
| Version | 16.2 | 17.1 |
| Designed for | Android 11 level (API 30) | A much newer level (API 37) |
| Last updated | March 2026 | Updated regularly |

The GrapheneOS project says the same in the release notes of its own TalkBack version. They write that Google's TalkBack is closed source, and that Google extracts the code several times a year and puts it on GitHub without the history of changes. So the public code is a periodic copy, not the place where TalkBack is built.

## Why I stopped

My biggest reason is that I do not think the public code is maintained well, so sending pull requests there has little benefit. The few updates and few pull requests made me feel that way. I contribute to open-source projects that are actively maintained, and this did not look like one of them.

The second reason is what I felt while using it. The build I made from the GitHub code was a developer (debug) build, and it was slow. Then I installed the official TalkBack from the Play Store, and it was clearly fast and smooth. The difference was easy to feel, so I did not need to measure it. It made me feel that something is wrong, and that the open-source code is not what Google actually ships.

The third reason is that the Play Store version is closed source. I cannot add timers to it, so I cannot measure it. This matters because the Play Store version is already fast and the GitHub build is slow. Suppose I improved the GitHub code and pushed it. I could not produce a report showing how much faster or slower it is, or whether my improvement is valid at all.

And even if I finished the work and sent it, there is no guarantee that anyone at Google would look at it.

## What others can learn

Check that the public code matches the real app before you invest time, and look at its update history. Measure before you build: my timing work took a few hours and saved me weeks. If your goal is faster speech, the speech engine is a better target.

## Limits of this study

I used one phone and 25 measurements, so the numbers are a good guide, not a final answer. I ran the tests while my phone was connected through wireless ADB, which is a tool that links the phone to a computer. This connection may have added a small delay to my measurements. This is a possibility, not something I confirmed. Google may also accept feedback through other channels that I did not test.
