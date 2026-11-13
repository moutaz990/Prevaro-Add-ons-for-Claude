---
name: content-calendar
description: >
  This skill should be used when the user asks to "make a content calendar", "plan the next two weeks of
  posts", "check my calendar", "set my content pillars", "اعمل تقويم محتوى", "حدّد محاور المحتوى", or when a
  post needs to be assigned to a pillar and a date. It keeps the content plan (pillars, shares, platforms,
  weekly pace) and builds and checks a calendar file against it.
metadata:
  version: "0.1.0"
---

# Content plan and calendar

The plan fixes what the brand posts about: the pillars and the share of each, the platforms and the weekly pace. The calendar is one row per post. A script builds the calendar from the plan and checks it, so content does not drift into a different topic every day.

## Files (in the working folder)

- `content-studio/content-plan.json`: the plan. If it is missing, copy `references/content-plan.template.json` there and agree its content with the owner. The template's pillars, pace and posting days are placeholders to discuss, not advice.
- `content-studio/calendar.csv`: the calendar. It opens in Excel or Google Sheets.

## The plan is a proposal until the owner approves it

`status` starts as `proposed`. While it is, ideas and drafts are allowed, and the script refuses any row marked `scheduled` or `published`. Set `status` to `approved`, with the owner's name and the date, only on the owner's explicit approval. Goal, audience and language stay `[TBC]` until the owner states them; never guess them.

## Run

```
python scripts/content_calendar.py new --start 2026-11-16 --weeks 2 --platforms linkedin,instagram --pace min --out content-studio/calendar.csv
python scripts/content_calendar.py check content-studio/calendar.csv
```

- `new` spreads the pillars by their shares over the planned posting days and leaves the hook empty for writing. It never overwrites a file.
- `check` reports errors and warnings: a pillar, platform, format or topic outside the plan; a missing topic on a pillar that needs one; a generated video past the idea stage with no cost estimate; a banned word; an approved post with no hook; more posts in a week than the plan allows; pillar shares drifting from the plan.
- Exit code 1 means errors. Fix them; do not hide them.
- Needs Python 3 only. Where commands cannot run, keep the calendar as a table in the chat and say the check was not run.

## Row statuses, in order

`idea` → `concept_approved` (the owner approved the idea) → `sample_approved` (the owner approved one cheap sample) → `final_approved` → `scheduled` → `published`. `dropped` removes a row from the counts. Move a row forward only on the owner's approval of that row.

## Columns

`date`, `day`, `platform`, `pillar`, `topic` (a product or service line, when the pillar needs one), `format` (image, carousel, video, thread, text), `visual` (generated, real, brand-card), `hook`, `signature` (the closing clip of a video, when the plan uses video endings), `status`, `cost_est_usd`, `notes`.

## Rules

- Content outside the pillars needs the owner's approval and a plan change first.
- Change the plan only on the owner's decision, and say what changed.
- No customer names or personal data in the calendar.
