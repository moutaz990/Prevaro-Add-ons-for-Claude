# Connect Buffer

Connects Claude to your Buffer account with **your own API key**. Buffer schedules posts on Facebook, Instagram, TikTok, YouTube, LinkedIn, X and more. It is a companion to the [Content Studio](../../) plugin and can also be used on its own.

يربط Claude بحسابك في Buffer **بمفتاح API خاص بك**. إضافة مرافقة لبلغن Content Studio.

## Setup

1. In Buffer, open your account settings, then **API**, and create a personal API key. Buffer lets the organization owner create keys.
2. Install this plugin:
   `/plugin install connect-buffer --marketplace moutaz990/Prevaro-Add-ons-for-Claude`
3. Paste the key when asked. To change it later: `/plugin configure connect-buffer@prevaro-addons`.

## What you should know

- The key is stored in your computer's secure credential store (on Linux without a keyring, in a file inside your Claude configuration folder). It is sent only to `mcp.buffer.com`.
- A key lets whoever holds it post from your accounts. Never paste it in a chat, and revoke it in Buffer if it leaks.
- Prefer signing in instead of a key? Do not install this plugin; add Buffer as a connector in your Claude app with the address `https://mcp.buffer.com/mcp` and sign in on Buffer's page.
- This plugin contains no code: it only tells Claude where Buffer's own MCP server is and which key to send. The tools you get are Buffer's.

License: MIT. Not affiliated with Buffer.
