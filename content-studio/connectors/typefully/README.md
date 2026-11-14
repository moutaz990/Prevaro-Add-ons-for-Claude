# Connect Typefully

Connects Claude to your Typefully account with **your own API key**. Typefully schedules posts on X, LinkedIn, Threads, Bluesky and Mastodon. It is a companion to the [Content Studio](../../) plugin and can also be used on its own.

يربط Claude بحسابك في Typefully **بمفتاح API خاص بك**. إضافة مرافقة لبلغن Content Studio.

## Setup

1. In Typefully, open your account settings, find the API section, and create an API key.
2. Install this plugin:
   `/plugin install connect-typefully --marketplace moutaz990/Prevaro-Add-ons-for-Claude`
3. Paste the key when asked. To change it later: `/plugin configure connect-typefully@prevaro-addons`.

## What you should know

- The key is stored in your computer's secure credential store (on Linux without a keyring, in a file inside your Claude configuration folder). It is sent only to `mcp.typefully.com`.
- A key lets whoever holds it post from your accounts. Never paste it in a chat, and revoke it in Typefully if it leaks.
- Prefer signing in instead of a key? Do not install this plugin; add Typefully as a connector in your Claude app with the address `https://mcp.typefully.com/mcp` and sign in on Typefully's page.
- This plugin contains no code: it only tells Claude where Typefully's own MCP server is and which key to send. The tools you get are Typefully's.

License: MIT. Not affiliated with Typefully.
