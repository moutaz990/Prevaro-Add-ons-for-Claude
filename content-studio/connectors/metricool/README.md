# Connect Metricool

Connects Claude to your Metricool account. Metricool gives figures for your accounts and for competitor accounts, and schedules posts on Facebook, Instagram, TikTok and YouTube. It is a companion to the [Content Studio](../../) plugin and can also be used on its own.

يربط Claude بحسابك في Metricool **بتسجيل الدخول في صفحة Metricool**، بلا مفتاح. إضافة مرافقة لبلغن Content Studio.

## Why there is no API key here

Metricool's connection for AI assistants works by signing in on Metricool's own page, on every plan including the free one. Metricool's separate API, the one that uses a token, is offered on its Advanced and Custom plans only. So a key would cost money, and signing in does not.

## Setup

1. Install this plugin:
   `/plugin install connect-metricool --marketplace moutaz990/Prevaro-Add-ons-for-Claude`
2. In Claude Code run `/mcp`, choose **metricool**, then **Authenticate**. A browser page opens on Metricool: sign in and approve.

In the Claude desktop or web app you do not need this plugin: Metricool is listed in the app's connectors page; search for it there and connect.

## What you should know

- No password or code is typed into Claude: you sign in on Metricool's page, and two-step verification happens there.
- This plugin contains no code: it only tells Claude where Metricool's own MCP server is (`https://ai.metricool.com/mcp`). The tools you get are Metricool's.
- Connecting does not raise your Metricool plan's limits.

License: MIT. Not affiliated with Metricool.
