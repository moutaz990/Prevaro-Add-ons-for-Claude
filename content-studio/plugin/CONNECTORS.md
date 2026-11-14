# Connectors

## How tool references work

The skills in this plugin use `~~category` as a placeholder for whatever tool you connect in that category. For example, `~~social scheduler` might be Typefully, Buffer or Metricool. The skills describe the work in terms of categories, not specific products.

## Connectors for this plugin

This plugin bundles **no connector**. You add only the ones you use, each as its own small add-on from the same repository.

| Category | Placeholder | Add-on | Other options |
|---|---|---|---|
| Social scheduler | `~~social scheduler` | `connect-typefully`, `connect-buffer`, `connect-metricool` | Any scheduling tool with an MCP server |
| Image and video generator | `~~image generator` | Gemini Images & Video extension (same repository) | Any image tool you have connected |

With no scheduler connected the plugin still works: it builds a publish pack (the files plus the caption per platform) for you to upload by hand. With no generator it works up to the concept card, or uses pictures you supply.

## Which scheduler? Free plans compared

Checked on 13 November 2026, mostly from comparison sites rather than the vendors' own pricing pages. Plans change often: read the vendor's pricing page before you rely on a number.

| | Typefully | Buffer | Metricool |
|---|---|---|---|
| Free plan | Yes | Yes | Yes |
| Posts on the free plan | 10 a month | 10 scheduled per channel at a time; the queue refills as posts go out | 20 a month across all channels |
| Accounts on the free plan | 1 social set | 3 channels | 1 brand |
| X | Yes | Yes | Not on the free plan |
| LinkedIn | Yes | Yes | Not on the free plan |
| Facebook, Instagram, TikTok, YouTube | No | Yes | Yes |
| How Claude connects | API key, or sign-in | API key, or sign-in | Sign-in only (its API token needs a paid plan) |
| Extra | — | — | Figures for 5 competitor accounts |

How to choose:

- **Mostly X and LinkedIn, a few posts a month:** Typefully.
- **Facebook, Instagram, TikTok or YouTube, posting often:** Buffer. Its free limit is on the queue, not on the month.
- **You want competitor figures for the morning report:** add Metricool for reading, even if you post with another tool.
- You can combine them, for example Buffer for posting and Metricool for figures.

## How to connect each one

| Add-on | What you enter | Where it comes from |
|---|---|---|
| `connect-typefully` | Your Typefully API key | Typefully account settings, API section |
| `connect-buffer` | Your Buffer API key | Buffer account settings, API, "personal API key" (the organization owner creates it) |
| `connect-metricool` | Nothing: you sign in on Metricool's page | — |

In Claude Code:

```
/plugin install connect-buffer --marketplace moutaz990/Prevaro-Add-ons-for-Claude
```

Claude asks for the key once and keeps it in your computer's secure credential store. Change it later with `/plugin configure connect-buffer@prevaro-addons`.

In the Claude desktop or web app, the simplest way is the app's own connectors page: add the tool there and sign in on its page. The addresses are `https://mcp.typefully.com/mcp`, `https://mcp.buffer.com/mcp` and `https://ai.metricool.com/mcp`; Metricool is also listed in the app's connector directory.

## Keys and sign-in

- An API key is issued by the service for exactly this purpose, and you can revoke it there at any time. Treat it like a password: it lets its holder post from your accounts. Never paste it into a chat.
- The plugin never asks for your social media usernames, passwords or login codes. You connect your social accounts inside the scheduler, on the scheduler's website.
- Why a scheduler and not a direct link to each platform: posting through the platforms' own APIs needs each platform's approval of the app (LinkedIn company pages, public TikTok posting) or is paid per use (X). Scheduling tools already hold those approvals.

## What goes to each service

- **Scheduler:** the captions and media of posts you approved, and reads of your own figures.
- **Image generator:** the prompts and any picture you ask it to edit. Never send customer documents, personal data or photos of real people's faces.
