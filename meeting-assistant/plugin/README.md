# Meeting Assistant

Minutes of meeting and scheduling for Claude. It turns the record of a meeting into minutes with decisions and action items, drafts the follow-up message, and schedules meetings on your calendar.

**The rule: Claude prepares, you approve.** No message is sent and no event is created, changed or cancelled until you say yes to that specific thing.

**Claude does not join calls.** A notetaker or the meeting platform records the meeting; Claude reads the transcript afterwards. `CONNECTORS.md` explains the options.

## Components

| Skill | What it does | Ask for it like this |
|---|---|---|
| `meeting-minutes` | Minutes from a transcript or your notes: decisions, action items with owners and dates, open questions, and a follow-up draft | "Write the minutes of today's meeting with the supplier" |
| `meeting-scheduler` | Finds a time on your calendar, drafts the invitation with an agenda, creates the event after your yes | "Schedule the follow-up for next week" |

**Connectors** (see `CONNECTORS.md`): none is bundled. Add what you use: `connect-fathom` or `connect-fireflies` for a notetaker that joins Zoom, Google Meet and Teams; `connect-zoho-mail` for Zoho Mail. Zoom, Microsoft 365 (Teams, Outlook), Google Drive, Google Calendar and Gmail are connected from your Claude app's own connectors page.

## Setup

1. Install the plugin.
   - Claude Code: `/plugin install meeting-assistant --marketplace moutaz990/Prevaro-Add-ons-for-Claude`
   - Claude Desktop (Cowork): open the `meeting-assistant-0.1.0.plugin` file and accept it.
2. Connect a source for transcripts, a calendar and, if you want follow-up drafts, your email.
3. Say "write the minutes of my last meeting" or "schedule a meeting with …".

This plugin itself needs no keys and no environment variables.

## Usage

- With no connector at all: paste or attach the transcript or your notes.
- The minutes are written in the language you ask for; headings are provided in English and Arabic.
- An owner or a date that was not said in the meeting is written `[TBC]`, never guessed.

## Privacy

- This plugin stores nothing and sends nothing anywhere by itself.
- A notetaker keeps recordings and transcripts on its own servers; an email or calendar connector reads your mailbox or calendar. Each service's own privacy policy applies; read it on that service's website before connecting.
- Tell the people in a meeting that it is being recorded. Never record anyone without their knowledge.

## Customization

Tool categories are written as `~~meeting notetaker`, `~~calendar`, `~~email` and `~~cloud storage` in the skills; `CONNECTORS.md` lists them. To use your organisation's own minutes layout, replace `skills/meeting-minutes/references/minutes-template.md`.

## Limits

- Minutes are only as good as the record. Automatic transcription of Arabic, and of mixed Arabic and English, is often wrong on names, numbers and dates; the skill marks what is unclear and asks.
- Not yet tried inside a real Claude Desktop install, nor with real notetaker, calendar or email accounts.

License: MIT.
