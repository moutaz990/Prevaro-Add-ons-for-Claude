# Connectors

## How tool references work

The skills in this plugin use `~~category` as a placeholder for whatever tool you connect in that category. For example, `~~social scheduler` might be Typefully, Buffer or another scheduling tool with an MCP server. The skills describe the work in terms of categories, not specific products.

## Connectors for this plugin

| Category | Placeholder | Included servers | Other options |
|---|---|---|---|
| Social scheduler | `~~social scheduler` | Typefully, Buffer | Any scheduling tool that offers an MCP server |
| Image and video generator | `~~image generator` | none (install separately) | Gemini Images & Video extension from this repository, or any image tool you have connected |

Connect only the ones you use. A connector you do not connect is simply ignored: without a scheduler the plugin builds a publish pack (files plus caption) for you to upload by hand, and without a generator it works up to the concept card or uses pictures you supply.

## How accounts are connected

You sign in on the scheduler's own page (OAuth), and connect your social accounts inside the scheduler. Two-step verification happens there, between you and the platform. This plugin never asks for a password or a login code, and none is stored in a chat or a file.

Why a scheduler and not a direct connection to each platform: posting through the platforms' own APIs needs each platform's approval of the app (LinkedIn company pages, TikTok public posting), or is paid per use (X). Scheduling tools already hold those approvals.

## What goes to each service

- **Scheduler:** the captions and media of posts you approved, and reads of your own post analytics.
- **Image generator:** the prompts and any picture you ask it to edit. Never send customer documents, personal data or photos of real people's faces.
