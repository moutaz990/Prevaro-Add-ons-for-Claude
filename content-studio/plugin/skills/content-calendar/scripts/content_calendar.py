#!/usr/bin/env python3
"""Build and check a content calendar against the content plan.

The plan (content-studio/content-plan.json in the working folder) fixes the pillars, their shares, the topics, and the weekly
pace per platform. This script keeps every calendar inside it:

  new    builds a calendar skeleton (CSV) for some weeks: dates, platform, pillar, topic, format,
         visual, signature. Hooks are left empty for the writer; every row starts as an idea.
  check  verifies a calendar: only planned pillars, platforms, formats and topics; the weekly pace;
         pillar shares; one ending per video; no banned words; and no row scheduled or published
         while the plan itself is still a proposal.

Examples:
  python content_calendar.py new --start 2026-11-15 --weeks 2 --platforms x,facebook --out content-studio/calendar.csv
  python content_calendar.py check content-studio/calendar.csv
The plan is found at content-studio/content-plan.json, then ./content-plan.json, or with --plan.
Exit code 0 = no errors (warnings may remain); 1 = errors. Deps: none beyond Python 3.
"""
import argparse
import csv
import datetime
import json
import sys
from pathlib import Path

COLUMNS = ["date", "day", "platform", "pillar", "topic", "format", "visual", "hook", "signature",
           "status", "cost_est_usd", "notes"]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]  # datetime.weekday(): Monday = 0
BLOCKED_BEFORE_APPROVAL = ("scheduled", "published")


def load_plan(path):
    cands = [Path(path)] if path else [Path("content-studio/content-plan.json"), Path("content-plan.json")]
    p = next((c for c in cands if c.is_file()), None)
    if not p:
        raise SystemExit("ERROR: content plan not found (" + ", ".join(str(c) for c in cands) + "). Copy "
                         "references/content-plan.template.json there and fill it with the owner, or pass --plan.")
    try:
        plan = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise SystemExit(f"ERROR: {p.name} is not valid JSON: {e}")
    for key in ("pillars", "platforms", "visuals", "statuses"):
        if not plan.get(key):
            raise SystemExit(f"ERROR: {p.name} has no '{key}'.")
    plan.setdefault("topics", {})
    if plan.get("week_starts", "Mon") not in DAYS:
        raise SystemExit(f"ERROR: week_starts must be one of {', '.join(DAYS)}")
    if any(x.get("needs_topic") for x in plan["pillars"]) and not plan["topics"]:
        raise SystemExit(f"ERROR: a pillar needs a topic but {p.name} lists no topics.")
    total = sum(x["share"] for x in plan["pillars"])
    if total != 100:
        raise SystemExit(f"ERROR: pillar shares add up to {total}, not 100. Fix {p.name}.")
    ids = [x["id"] for x in plan["pillars"]]
    if len(ids) != len(set(ids)):
        raise SystemExit("ERROR: duplicate pillar id in the plan.")
    return plan


def week_start(d, plan):
    """First day of d's week. The plan says which weekday a week starts on (week_starts, default Mon)."""
    first = DAYS.index(plan.get("week_starts", "Mon"))
    return d - datetime.timedelta(days=(d.weekday() - first) % 7)


def ending_for(plan, topic):
    """Video ending for a topic. Only used when the plan sets video_endings (a default ending, plus one per topic)."""
    return plan["topics"].get(topic, {}).get("ending") or plan["video_endings"]["default"]


def allocate(pillars, n):
    """Largest-remainder split of n slots by pillar share. Returns {pillar id: count}."""
    exact = {p["id"]: n * p["share"] / 100 for p in pillars}
    counts = {k: int(v) for k, v in exact.items()}
    for k in sorted(exact, key=lambda k: (exact[k] - counts[k], exact[k]), reverse=True)[: n - sum(counts.values())]:
        counts[k] += 1
    return counts


def cmd_new(a):
    plan = load_plan(a.plan)
    out = Path(a.out)
    if out.exists():
        raise SystemExit(f"ERROR: {out} already exists; choose another name (this script never overwrites a calendar).")
    try:
        start = datetime.date.fromisoformat(a.start)
    except ValueError:
        raise SystemExit("ERROR: --start must be YYYY-MM-DD")
    platforms = [p.strip() for p in a.platforms.split(",") if p.strip()]
    unknown = [p for p in platforms if p not in plan["platforms"]]
    if unknown or not platforms:
        raise SystemExit("ERROR: unknown platform: " + ", ".join(unknown or ["(none)"]) + ". Planned: " + ", ".join(plan["platforms"]))

    first = week_start(start, plan)
    first_day = DAYS.index(plan.get("week_starts", "Mon"))
    slots = []  # (date, platform)
    for w in range(a.weeks):
        for name in platforms:
            p = plan["platforms"][name]
            n = p["per_week"][0 if a.pace == "min" else 1]
            if n == 0:
                continue
            days = p.get("days", {}).get(str(n))
            if not days:
                raise SystemExit(f"ERROR: the plan has no posting days for {name} at {n} per week.")
            for day in days:
                d = first + datetime.timedelta(days=7 * w + (DAYS.index(day) - first_day) % 7)
                if d >= start:
                    slots.append((d, name))
    slots.sort(key=lambda s: (s[0], platforms.index(s[1])))
    if not slots:
        raise SystemExit("ERROR: no posting slots: the chosen platforms have a pace of 0 per week in the plan.")

    by_id = {p["id"]: p for p in plan["pillars"]}
    remaining = allocate(plan["pillars"], len(slots))
    topics = list(plan["topics"])
    topic_i = 0
    last = {}  # platform -> last pillar used there
    rows = []
    for d, name in slots:
        allowed = set(plan["platforms"][name]["formats"])
        # Most under-served pillar first; avoid the same pillar twice in a row on one platform when possible.
        order = sorted((k for k, v in remaining.items() if v > 0 and allowed & set(by_id[k]["formats"])),
                       key=lambda k: (-remaining[k] / by_id[k]["share"], [p["id"] for p in plan["pillars"]].index(k)))
        if not order:
            order = [k for k, v in remaining.items() if v > 0] or [plan["pillars"][0]["id"]]
        pick = next((k for k in order if last.get(name) != k), order[0])
        remaining[pick] = remaining.get(pick, 0) - 1
        last[name] = pick
        pillar = by_id[pick]
        fmt = next(f for f in plan["platforms"][name]["formats"] if f in pillar["formats"]) if allowed & set(pillar["formats"]) else plan["platforms"][name]["formats"][0]
        topic = ""
        if pillar.get("needs_topic"):
            topic = topics[topic_i % len(topics)]
            topic_i += 1
        visual = plan["platforms"][name].get("visual_must_be") or pillar["visual"]
        rows.append({"date": d.isoformat(), "day": DAYS[d.weekday()], "platform": name, "pillar": pick, "topic": topic,
                     "format": fmt, "visual": visual, "hook": "",
                     "signature": ending_for(plan, topic) if fmt == "video" and plan.get("video_endings") else "", "status": "idea",
                     "cost_est_usd": "", "notes": ""})
    with open(out, "w", newline="", encoding="utf-8-sig") as f:  # BOM so Excel shows Arabic correctly
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} rows -> {out}")
    if plan.get("status") != "approved":
        print("NOTE: the content plan is still a PROPOSAL (not approved by the owner). Rows are ideas only.")
    return 0


def cmd_check(a):
    plan = load_plan(a.plan)
    path = Path(a.calendar)
    if not path.exists():
        raise SystemExit(f"ERROR: calendar not found: {path}")
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = [c for c in COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit("ERROR: missing columns: " + ", ".join(missing))
        rows = list(reader)
    by_id = {p["id"]: p for p in plan["pillars"]}
    errors, warnings = [], []
    approved = plan.get("status") == "approved"
    seen = {}
    per_week = {}
    counted = []
    for i, r in enumerate(rows, start=2):  # line 1 is the header
        r = {k: (v or "").strip() for k, v in r.items()}
        where = f"line {i} ({r['date']} {r['platform']})"
        try:
            d = datetime.date.fromisoformat(r["date"])
        except ValueError:
            errors.append(f"{where}: date is not YYYY-MM-DD")
            continue
        if r["day"] and r["day"] != DAYS[d.weekday()]:
            errors.append(f"{where}: {r['date']} is a {DAYS[d.weekday()]}, not {r['day']}")
        if r["status"] not in plan["statuses"]:
            errors.append(f"{where}: unknown status '{r['status']}'. Use: {', '.join(plan['statuses'])}")
        if r["status"] == "dropped":
            continue
        platform = plan["platforms"].get(r["platform"])
        if not platform:
            errors.append(f"{where}: platform is not in the plan")
            continue
        pillar = by_id.get(r["pillar"])
        if not pillar:
            errors.append(f"{where}: pillar '{r['pillar']}' is not in the plan. Content outside the pillars needs the owner's approval and a plan change")
            continue
        if r["format"] not in platform["formats"]:
            errors.append(f"{where}: format '{r['format']}' is not planned for {r['platform']} ({', '.join(platform['formats'])})")
        elif r["format"] not in pillar["formats"]:
            errors.append(f"{where}: format '{r['format']}' is not planned for pillar {r['pillar']}")
        if r["topic"] and r["topic"] not in plan["topics"]:
            errors.append(f"{where}: topic '{r['topic']}' is not in the plan ({', '.join(plan['topics'])})")
        if pillar.get("needs_topic") and not r["topic"]:
            errors.append(f"{where}: pillar {r['pillar']} needs a topic")
        if r["visual"] not in plan["visuals"]:
            errors.append(f"{where}: visual must be one of {', '.join(plan['visuals'])}")
        must = platform.get("visual_must_be")
        if must and r["visual"] != must:
            errors.append(f"{where}: {r['platform']} takes {must} footage only")
        if r["format"] == "video" and r["visual"] == "generated" and not r["cost_est_usd"] and r["status"] != "idea":
            errors.append(f"{where}: a generated video past the idea stage needs cost_est_usd, and the owner's yes to that cost")
        if r["format"] == "video" and plan.get("video_endings"):
            expected = ending_for(plan, r["topic"])
            if not r["signature"]:
                errors.append(f"{where}: a video needs its ending in 'signature' (expected: {expected})")
            elif "+" in r["signature"] or "," in r["signature"]:
                errors.append(f"{where}: one video, one ending")
            elif r["signature"] != expected:
                errors.append(f"{where}: ending '{r['signature']}' does not match the plan (expected: {expected})")
            pending = plan["topics"].get(r["topic"], {}).get("ending_pending")
            if pending and r["signature"] == plan["video_endings"]["default"]:
                warnings.append(f"{where}: the ending '{pending}' is not built yet; the default ending is used for now")
        elif r["signature"] and r["format"] != "video":
            warnings.append(f"{where}: 'signature' is only for videos")
        if r["cost_est_usd"]:
            try:
                if float(r["cost_est_usd"]) < 0:
                    raise ValueError
            except ValueError:
                errors.append(f"{where}: cost_est_usd is not a number")
        text = " ".join((r["hook"], r["notes"])).lower()
        hits = [w for w in plan.get("banned_words", []) if w.lower() in text]
        if hits:
            errors.append(f"{where}: banned word or claim: {', '.join(hits)} (banned_words in the plan)")
        if not approved and r["status"] in BLOCKED_BEFORE_APPROVAL:
            errors.append(f"{where}: status '{r['status']}' is not allowed while the content plan is still a proposal")
        if r["status"] in ("final_approved", "scheduled", "published") and not r["hook"]:
            errors.append(f"{where}: an approved post needs its hook written in the calendar")
        key = (r["date"], r["platform"])
        if key in seen:
            warnings.append(f"{where}: second post on the same day and platform (first at line {seen[key]})")
        seen[key] = i
        per_week.setdefault((week_start(d, plan), r["platform"]), 0)
        per_week[(week_start(d, plan), r["platform"])] += 1
        counted.append(r["pillar"])

    for (ws, name), n in sorted(per_week.items()):
        lo, hi = plan["platforms"][name]["per_week"]
        if n > hi:
            errors.append(f"week of {ws} {name}: {n} posts, the plan allows at most {hi}")
        elif n < lo:
            warnings.append(f"week of {ws} {name}: {n} posts, the plan asks for at least {lo}")
    total = len(counted)
    print(f"{path.name}: {total} planned posts, {len(rows) - total} dropped or unreadable")
    if total:
        tol = plan.get("share_tolerance", 15)
        print("pillar            planned  target")
        for p in plan["pillars"]:
            share = round(100 * counted.count(p["id"]) / total)
            flag = ""
            if total >= 8 and abs(share - p["share"]) > tol:
                flag = "  <-- off plan"
                warnings.append(f"pillar {p['id']}: {share}% of the calendar, the plan says {p['share']}% (tolerance {tol})")
            print(f"  {p['id']:16} {share:>5}%  {p['share']:>5}%{flag}")
    if not approved:
        warnings.append("the content plan is still a PROPOSAL: the owner has not approved the pillars, shares and pace")
    for w in warnings:
        print("WARNING:", w)
    for e in errors:
        print("ERROR:", e)
    print(f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new", help="build a calendar skeleton")
    n.add_argument("--start", required=True, help="first day to plan, YYYY-MM-DD")
    n.add_argument("--weeks", type=int, default=2, choices=range(1, 9), metavar="1-8", help="how many weeks (default 2)")
    n.add_argument("--platforms", required=True, help="comma list of the platforms that are live today")
    n.add_argument("--pace", choices=("min", "max"), default="min", help="low or high end of the planned weekly pace (default min)")
    n.add_argument("--out", required=True, help="CSV file to create (never overwritten)")
    n.add_argument("--plan", help="content-plan.json (default: content-studio/content-plan.json)")
    n.set_defaults(fn=cmd_new)
    c = sub.add_parser("check", help="verify a calendar against the plan")
    c.add_argument("calendar", help="CSV file made by 'new' and edited since")
    c.add_argument("--plan", help="content-plan.json (default: content-studio/content-plan.json)")
    c.set_defaults(fn=cmd_check)
    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
