# Connect Fathom

Connects Claude to your Fathom account. Fathom is a notetaker that joins your Zoom, Google Meet and Microsoft Teams calls, records them and writes a transcript. With this add-on Claude can read those transcripts and summaries. It is a companion to the [Meeting Assistant](../../) plugin and can also be used on its own.

يربط Claude بحسابك في Fathom **بتسجيل الدخول في صفحة Fathom**، بلا مفتاح. إضافة مرافقة لبلغن Meeting Assistant.

## Setup

1. Install this plugin:
   `/plugin install connect-fathom --marketplace moutaz990/Prevaro-Add-ons-for-Claude`
2. In Claude Code run `/mcp`, choose **fathom**, then **Authenticate**. A browser page opens on Fathom: sign in and approve.

In the Claude desktop or web app you do not need this plugin: Fathom is listed in the app's connectors page; search for it there and connect.

## What you should know

- No password or code is typed into Claude: you sign in on Fathom's page.
- Fathom records only the meetings you let it join. Tell the people in the meeting that it is being recorded.
- The recording and transcript are stored by Fathom. If a meeting includes customer or personal data, check that this is acceptable for your organisation before recording it.
- This plugin contains no code: it only tells Claude where Fathom's own MCP server is (`https://api.fathom.ai/mcp`). The tools you get are Fathom's.

License: MIT. Not affiliated with Fathom.
