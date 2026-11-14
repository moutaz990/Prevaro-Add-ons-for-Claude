---
name: post-handover
description: >
  This skill should be used when a post or video is finished and the user asks to "hand it over", "write the
  caption and hashtags", "schedule this post", "queue it", "prepare it for publishing", "سلّم المنشور",
  "جدوِل المنشور", "جهّزه للنشر". It writes the handover card (files, caption, hashtags, alt text, time,
  checks), and only after the owner's explicit yes for that post, places it in the connected scheduler or
  builds a publish pack. Never publishes on its own and never asks for account passwords.
metadata:
  version: "0.1.0"
---

# Post handover

Bring each finished post to the owner in one clear card, and let nothing enter a publishing tool before the owner has approved that specific post.

**The owner connects their social accounts inside the scheduler, on its website. Claude reaches the scheduler through its connector, set up once with the scheduler's API key or by signing in on its page. Never ask for a social media password, a login code or an API key in the chat, and never write one to a file.** If a connector is not set up, say so and point to `CONNECTORS.md`.

## Inputs

- The calendar row, at status `final_approved`.
- The final files with their paths: post-composer images, or the finished video.
- Language, dialect and hashtag habits from `content-studio/content-brief.md`.
- ~~social scheduler, if connected. Check which accounts and platforms it actually offers before promising anything.

## The handover card (one per post)

- **Files:** paths, with size and duration.
- **Caption** in the agreed language, 8 to 15 hashtags (broad, niche, local), and alt text for the image.
- **Where and when:** platform, account, suggested day and time with the reason. If the owner has not set posting times, write `[TBC]`; do not guess.
- **Video signature**, when the brand uses one: the opening and the ending, with a one-line reason.
- **Spent:** the estimated generation cost of this post and what is left under the monthly cap, from the generator's usage tool.
- **Checks:** banned words, no customer or personal data, no text baked into a generated picture, the logo from the official file, story safe areas, the "Illustrative image" tag on anything not real.

Then ask: **approve, change, or drop?**

## After approval

| Situation | Action |
|---|---|
| The platform is available in ~~social scheduler | Create the post as a **draft** first and give the owner its link or id. Schedule it for a time only when the owner says so for this post. Use "publish now" only on the owner's explicit request for this post |
| No connected scheduler covers the platform | Build a publish pack: a folder `content-studio/publish/<date>_<platform>_<slug>/` with the final files, `caption.txt` (caption and hashtags) and `alt.txt`, for the owner to upload by hand |
| The content plan is still `proposed` | Schedule nothing. Show the card and say the plan must be approved first |

Then set the row's status (`scheduled`, or `published` once the owner confirms it is live) and run the calendar check.

## Rules

- One approval covers one post. An earlier approval never extends to another post.
- Before creating a draft, confirm the account shown in the scheduler is the brand's account, not a personal profile. If unsure, stop and ask.
- Never reply to comments or messages, like, follow, delete or edit a published post, unless the owner asks for that specific action.
- Never run paid ads or spend money.
- If the scheduler fails or asks to sign in again, say so, leave the sign-in to the owner, and build a publish pack instead.
- No prices, dates, guarantees or commitments in a caption unless the owner supplied them for publication.
