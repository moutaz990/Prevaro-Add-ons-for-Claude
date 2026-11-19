---
name: meeting-scheduler
description: >
  This skill should be used when the user asks to "schedule a meeting", "find a time", "set up a call",
  "book the follow-up meeting", "reschedule", "send the invitation", "plan my meetings this week",
  "جدوِل اجتماعاً", "دبّر موعداً", "أرسل الدعوة", "رتّب اجتماعات الأسبوع". It checks the calendar, proposes
  times, drafts the invitation with an agenda, and creates the event only after the user's explicit yes.
metadata:
  version: "0.1.0"
---

# Meeting scheduler

Find a time, write a clear invitation, and put the meeting on the calendar after the user has approved it. Talk to the user in their language.

## What is needed

- ~~calendar, if connected (Google Calendar, Outlook through Microsoft 365, Zoho Calendar). Without one, give the user the proposed times and the invitation text to send themselves, and say that nothing was put on a calendar.
- From the user, only what is missing: purpose, who must attend and who is optional, length, the window of days, the platform (Zoom, Google Meet, Teams, in person), and each party's time zone when they are not all in one place.

## Proposing times

1. Read the user's calendar for the window. Read other attendees' free and busy times only where the calendar actually shows them; never assume someone is free.
2. Propose **three** slots. Give each with the day, date, start and end, and the time zone, and repeat it in the other party's time zone when it differs.
3. Respect the user's working days and hours. If they are not known, ask once and remember them for this conversation. Do not assume a Monday to Friday week.
4. Leave room around existing meetings and avoid prayer times, lunch and the end of the day when the user says they matter.
5. If no common slot exists, say so and show the two nearest options with who would have to move.

## The invitation

Draft it for approval before anything is created:

- **Title:** specific, not "Meeting".
- **Purpose:** one sentence.
- **Agenda:** three to five points, each with the outcome wanted.
- **What to prepare**, and who brings what.
- **Length and link:** let the calendar or the meeting platform create the link. Never invent a meeting link or a dial-in number.
- **Recording notice:** if a notetaker or a recording will be used, add a plain line saying the meeting will be recorded and transcribed and by which tool, so attendees can object.

## Rules

- **Nothing is created, changed or cancelled without a yes** to that specific event. One approval covers one event or one named series.
- **Outside attendees need a second look.** Before inviting anyone outside the user's organisation, show the full attendee list and the exact text they will receive.
- **No commitments on the user's behalf.** Proposing times is not confirming them. Do not accept, decline or reply to an invitation unless asked for that invitation.
- **Rescheduling:** show what moves, who is affected and the message they will get, then wait.
- **Recurring series:** state the pattern and the end date in words before creating it.
- **Privacy:** do not put customer details, prices or personal data in a title or description that all invitees and their assistants can read.

## After a meeting

When the meeting-minutes skill has produced action items, offer to turn them into calendar entries: a follow-up meeting if one was agreed, and a reminder on the due date of each action for its owner. Each one needs its own approval.

## Planning a week

On request, list the coming week's meetings with a one-line purpose each, point out clashes, back-to-back runs and meetings with no agenda, and propose changes. Change nothing without a yes.
