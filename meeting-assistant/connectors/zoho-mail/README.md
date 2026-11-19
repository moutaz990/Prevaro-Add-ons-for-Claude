# Connect Zoho Mail

Connects Claude to your Zoho Mail through **Zoho's own MCP service**, so Claude can read, search and draft email in your mailbox. It can be used on its own, or with the [Meeting Assistant](../../) plugin to draft the follow-up message after a meeting.

يربط Claude ببريدك في Zoho Mail عبر **خدمة MCP من Zoho نفسها**. تنشئ عنوان الخادم الخاص بك في لوحة Zoho وتلصقه مرة واحدة.

## Why you paste an address, not a key

Zoho does not have one address for everybody. Each person creates their own MCP server in Zoho's console, chooses which Zoho Mail actions it may perform, and gets a personal address for it. That address is what this plugin asks for.

## Setup

1. Sign in at **mcp.zoho.com** with your Zoho account. Zoho runs separate consoles per region; use the one for the data centre your account is in.
2. Create an MCP server and add the Zoho Mail tools you want Claude to have. Add only what you need: reading and searching are enough for most work, and sending can be left out.
3. Copy the address shown under **Connect**.
4. Install this plugin:
   `/plugin install connect-zoho-mail --marketplace moutaz990/Prevaro-Add-ons-for-Claude`
5. Paste the address when asked. The first time Claude uses a Zoho tool, Zoho may open a page asking you to authorise it.

In the Claude desktop or web app you do not need this plugin: paste the same address in the app's connectors page as a custom connector.

## What you should know

- Treat the address like a password. It is stored in your computer's secure credential store (on Linux without a keyring, in a file inside your Claude configuration folder). It also appears in the output of `claude mcp list`.
- To cut access, delete or regenerate the server in Zoho's console.
- Claude drafts; you send. Keep sending out of the tools you enable unless you really want Claude to send on its own, and never let a message leave without reading it.
- Email often contains customer and personal data. It is read by Claude through Zoho's service and goes nowhere else through this plugin.
- This plugin contains no code: it only tells Claude the address you gave it. The tools you get are Zoho's.

License: MIT. Not affiliated with Zoho.
