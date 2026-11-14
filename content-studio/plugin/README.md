# Content Studio

Social media content from plan to post, for any brand. Set the brand up once, then let Claude plan the content, compose the final post image with your logo and font, hand each post over for your approval, and report every morning on your accounts and competitors.

**The rule: Claude prepares, you approve.** Nothing is published, scheduled or paid for until you say yes to that specific thing.

## Components

| Skill | What it does | Ask for it like this |
|---|---|---|
| `brand-setup` | Saves your brand profile: name, colours, font, logo, banned words | "Set up my brand" |
| `content-lead` | Runs the whole job: questions, competitor scan, strategy, two-week plan, production through three approval gates | "Plan my content for the next two weeks" |
| `content-calendar` | Keeps the content plan (pillars, shares, pace) and builds and checks the calendar | "Make a two-week calendar" |
| `gemini-visual-generation` | How to use the Gemini image and video tools well, with cost shown before spending | "Generate a sample for this post" |
| `post-composer` | Adds the headline and your official logo to a picture, at exact platform sizes | "Compose this post, square and story" |
| `post-handover` | Handover card, then a draft in your scheduler or a publish pack | "Hand over the post" |
| `social-monitor` | Morning report: competitors, trends, your accounts, ideas for the week | "Morning brief" |

**Connectors** (see `CONNECTORS.md`): none is bundled. Add the scheduler you use as a small add-on from the same repository: `connect-typefully` or `connect-buffer` (you paste your own API key), or `connect-metricool` (you sign in on its page). `CONNECTORS.md` compares their free plans. Image and video generation uses the separate Gemini Images & Video extension, or any image tool you already have.

## Setup

1. Install the plugin.
   - Claude Code: `/plugin install content-studio --marketplace moutaz990/Prevaro-Add-ons-for-Claude`
   - Claude Desktop (Cowork): open the `content-studio-0.2.0.plugin` file and accept it.
2. Choose a working folder and say "set up my brand". You need your logo file, your colours and your font.
3. Optional: add a scheduler add-on, for example `/plugin install connect-buffer --marketplace moutaz990/Prevaro-Add-ons-for-Claude`, and install the Gemini extension.

This plugin itself needs no keys and no environment variables. A scheduler add-on asks for that scheduler's API key once.

## Usage

Your files live in a `content-studio/` folder inside your working folder, not inside the plugin:

`brand.json` (brand profile), `content-brief.md` (goal, audience, competitors), `content-plan.json` (pillars and pace), `calendar.csv`, `social-log.csv`, `deliver/` (final images), `publish/` (publish packs).

The scripts (final image, calendar, report figures) need Python 3, and the final image also needs Chrome or Edge and your brand font. They run wherever Claude can run commands on your computer. In a chat that cannot run commands, the skills still produce the plans and texts, and say what they could not do.

## Privacy

- This plugin stores nothing outside your working folder and sends nothing anywhere by itself.
- It never asks for your social media usernames, passwords or login codes. You connect your social accounts inside the scheduler, on its website; Claude reaches the scheduler with an API key the scheduler issued to you, or by signing in on its page.
- A connected scheduler receives the posts you approve. An image generator receives your prompts and any picture you ask it to edit. Each service's own privacy policy applies; read it on that service's website before connecting.
- The morning report only reads: it never likes, follows, comments, messages or posts.

## Customization

Tool categories are written as `~~social scheduler` and `~~image generator` in the skills; `CONNECTORS.md` lists them. Change the pillars, pace and banned words in your own `content-plan.json` and `brand.json`, not in the plugin.

## Limits

- Posting is done through a scheduling tool, because the platforms' own APIs need per-app approval or are paid per use.
- Reading competitors depends on what public pages show, or on a browser where you are logged in. Whatever could not be read is listed at the top of the report.
- Not yet tried inside a real Claude Desktop install; the scripts were tested on Linux with Chromium.

License: MIT.
