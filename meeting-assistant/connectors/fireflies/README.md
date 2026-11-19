# Connect Fireflies

Connects Claude to your Fireflies account with **your own API key**. Fireflies is a notetaker that joins your Zoom, Google Meet, Microsoft Teams and other calls, records them and writes a transcript. With this add-on Claude can read those transcripts and summaries. It is a companion to the [Meeting Assistant](../../) plugin and can also be used on its own.

يربط Claude بحسابك في Fireflies **بمفتاح API خاص بك**. إضافة مرافقة لبلغن Meeting Assistant.

## Setup

1. In Fireflies open **Settings**, then **Developer Settings**, and copy your API key.
2. Install this plugin:
   `/plugin install connect-fireflies --marketplace moutaz990/Prevaro-Add-ons-for-Claude`
3. Paste the key when asked. To change it later: `/plugin configure connect-fireflies@prevaro-addons`.

## What you should know

- The key is stored in your computer's secure credential store (on Linux without a keyring, in a file inside your Claude configuration folder). It is sent only to `api.fireflies.ai`.
- A key lets whoever holds it read your meeting transcripts. Never paste it in a chat, and regenerate it in Fireflies if it leaks.
- Prefer signing in instead of a key? Do not install this plugin; add Fireflies as a connector in your Claude app with the address `https://api.fireflies.ai/mcp` and sign in on Fireflies' page.
- Fireflies records only the meetings you let it join. Tell the people in the meeting that it is being recorded.
- The recording and transcript are stored by Fireflies. If a meeting includes customer or personal data, check that this is acceptable for your organisation before recording it.
- This plugin contains no code: it only tells Claude where Fireflies' own MCP server is and which key to send. The tools you get are Fireflies'.

License: MIT. Not affiliated with Fireflies.
