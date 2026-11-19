---
name: meeting-minutes
description: >
  This skill should be used when the user asks to "write the minutes", "write the MOM", "summarise this meeting",
  "what were the action items", "send the minutes to the attendees", "اكتب محضر الاجتماع", "لخّص الاجتماع",
  "ما المهام المتفق عليها", or shares a meeting transcript, recording summary or raw notes. It turns a transcript
  from a connected notetaker (or pasted notes) into minutes of meeting: decisions, action items with owners and
  dates, open questions, and a follow-up message as a draft. It does not join or record a call itself.
metadata:
  version: "0.1.0"
---

# Meeting minutes (MOM)

Turn what was said in a meeting into minutes the attendees can act on. Claude does not join the call: a notetaker or the meeting platform records it, and this skill works from that record. Write in the language the user asks for; if they do not say, use the language of the meeting.

## Where the record comes from

Use the first source that is available, and say which one was used:

1. ~~meeting notetaker, if connected (Fathom, Fireflies, or the platform's own: Zoom, Microsoft Teams through Microsoft 365). Find the meeting by date, title or attendee, and read its transcript, not only its automatic summary.
2. A transcript or notes file in ~~cloud storage (Google Meet saves its transcripts as documents in Google Drive).
3. Text or a file the user pastes or attaches.

If none is available, say so and ask for the transcript or the notes. Never write minutes from memory or from the invitation alone.

## Before writing: the recording question

If the record is a recording or transcript, ask once whether the attendees were told the meeting was being recorded. If the user does not know, say so at the top of the minutes and do not circulate the transcript itself. Never help record people without their knowledge.

## What goes in the minutes

Use `references/minutes-template.md`. The parts, in order:

1. **Header:** title, date, time and time zone, platform, who attended and who was absent, who prepared the minutes, and the source of the record.
2. **Agenda:** the topics actually discussed, in order.
3. **Discussion:** two to four lines per topic. What was raised and where it ended, not a replay.
4. **Decisions:** numbered, each one sentence, each traceable to the record.
5. **Action items:** a table of action, owner, due date, status. One owner per action.
6. **Open questions:** raised and not settled.
7. **Next meeting:** only if one was agreed.

## Rules

- **Only what the record supports.** Every decision and every action item must be traceable to the transcript or notes. If the user asks where something came from, quote the passage.
- **Nothing invented.** An owner or a date that was not said is written `[TBC]` and listed under open questions. Never guess who will do something or by when.
- **Names as in the invitation.** Spell attendees' names as the calendar event or the user gives them. A speaker the notetaker could not identify stays "unidentified speaker"; never assign a line to a person by guessing.
- **Flag weak passages.** Where the transcript is garbled, in mixed languages, or clearly misheard (names, numbers, amounts, dates), mark it `[unclear in the recording]` and ask. Automatic transcription of Arabic and of mixed Arabic and English is often wrong on names and figures.
- **Numbers and commitments exactly.** Prices, quantities, dates and promises are copied as said, with who said them. A commitment to an outside party is flagged for the owner's confirmation.
- **Neutral tone.** Record outcomes, not who won an argument. Leave out small talk and personal remarks.
- **Private content stays private.** The minutes and the transcript may contain customer or personal data. Keep them in the user's own files and tools; do not paste them into any other service.
- **A draft until approved.** The minutes are a draft for the user. Never send them to anyone without the user's explicit yes for that message.

## Steps

1. Find the record and say which source it is. If a calendar is connected, read the event for the title, time and invited names.
2. Read the whole transcript. For a long one, work through it in order rather than relying on the automatic summary.
3. Write the minutes from the template. Keep them to one or two pages.
4. List at the end what needs the user's confirmation: `[TBC]` items, unclear passages, commitments to outside parties.
5. Ask: approve, change, or drop?
6. After approval, and only if asked: draft the follow-up message with the minutes to the attendees through ~~email as a **draft**, and offer to schedule what was agreed with the meeting-scheduler skill. Send or create nothing without a yes to that specific thing.

## If something is missing

- No transcript, only an automatic summary: say the minutes rest on the tool's summary, not on the full record.
- The meeting was not recorded: work from the user's notes and say so in the header.
- A connector is not set up: say which one, and point to `CONNECTORS.md`.
