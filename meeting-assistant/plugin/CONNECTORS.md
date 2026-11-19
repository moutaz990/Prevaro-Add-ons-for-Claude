# Connectors

## How tool references work

The skills in this plugin use `~~category` as a placeholder for whatever tool you connect in that category. For example, `~~meeting notetaker` might be Fathom, Fireflies or the meeting platform's own recorder. The skills describe the work in terms of categories, not specific products.

## Connectors for this plugin

This plugin bundles **no connector**. You add only the ones you use.

| Category | Placeholder | Add-on from this repository | Or connect in your Claude app |
|---|---|---|---|
| Meeting notetaker | `~~meeting notetaker` | `connect-fathom`, `connect-fireflies` | Zoom, Microsoft 365 (Teams), Fathom, Fireflies |
| Cloud storage | `~~cloud storage` | — | Google Drive (where Google Meet saves transcripts) |
| Calendar | `~~calendar` | — | Google Calendar, Microsoft 365 (Outlook) |
| Email | `~~email` | `connect-zoho-mail` | Gmail, Microsoft 365 (Outlook) |

With nothing connected the plugin still works: paste or attach the transcript or your notes, and Claude writes the minutes; for scheduling it gives you the proposed times and the invitation text to send yourself.

## Claude does not join the call

Claude cannot enter a Zoom, Google Meet or Teams call, listen or record. Something else makes the record, and Claude reads it afterwards:

| Who records | How it gets into the meeting | How Claude reads the result |
|---|---|---|
| **Fathom** or **Fireflies** (a notetaker) | Joins your calls on Zoom, Google Meet and Teams as a participant, from your calendar | `connect-fathom` / `connect-fireflies`, or the app's connectors page |
| **Zoom** itself | Zoom's own recording and AI summary, turned on in the meeting | Zoom's official connector, in the app's connectors page |
| **Microsoft Teams** itself | Teams' own transcription, turned on in the meeting | The Microsoft 365 connector. An administrator must allow transcript access first |
| **Google Meet** itself | Meet's own transcription, turned on in the meeting | The transcript is saved as a document in Google Drive; the Google Drive connector reads it |

One notetaker covers all three platforms, which is the simplest setup when your meetings are spread across them.

## Which notetaker? Free plans compared

Checked on 19 November 2026 from comparison sites, not from the vendors' own pricing pages. Plans change often: read the vendor's pricing page before you rely on anything here.

| | Fathom | Fireflies |
|---|---|---|
| Free plan | Yes | Yes |
| Recording on the free plan | Reported as unlimited | Reported as limited; sources disagree on the limit |
| Claude connection on the free plan | Reported as included | Reported as included, with lower limits |
| Joins | Zoom, Google Meet, Teams | Zoom, Google Meet, Teams and others |
| How Claude connects | Sign-in | API key, or sign-in |
| Arabic | **Not confirmed** | **Not confirmed** |

**Arabic matters here.** We could not confirm from either vendor that Arabic, or mixed Arabic and English, is transcribed well. Record one real meeting with each on its free plan and read the transcript before you choose. Whatever the tool, the minutes skill marks unclear passages instead of guessing.

## Recording and consent

- Tell everyone in the meeting that it is being recorded and transcribed, and by which tool. In many places this is a legal requirement, and it is the decent thing everywhere. The scheduler skill adds the notice to invitations.
- A notetaker stores the recording and the transcript on its own servers. For meetings with customers, check that this is acceptable for your organisation and for them.
- Never use any of this to record people without their knowledge.

## Keys and sign-in

- An API key or a personal server address is issued by the service for exactly this purpose, and you can revoke it there. Treat it like a password. Never paste it into a chat.
- The plugin never asks for the passwords or login codes of your accounts.
