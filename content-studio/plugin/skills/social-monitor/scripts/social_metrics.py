#!/usr/bin/env python3
"""Social media numbers for the daily report: engagement rates, top posts, own averages, paid-campaign candidates.

Every figure in the report comes from this script, never from estimation. Input is the running log (CSV) that the
skill appends to each morning; only numbers actually seen on a page go in it. An empty cell means "not visible".

  social_metrics.py init  social-log.csv                      create an empty log with the right columns
  social_metrics.py check social-log.csv                      validate the log
  social_metrics.py report social-log.csv --date 2026-11-15   figures for the daily report (JSON on stdout)

Log columns:
  seen_on     date the numbers were read (YYYY-MM-DD)
  owner       ours | competitor
  account     handle
  platform    instagram | tiktok | x | linkedin | facebook | youtube
  url         link to the post (required; every post in the report is linked)
  posted_on   date the post was published (YYYY-MM-DD)
  format      reel | carousel | photo | video | thread | text
  views, likes, comments, shares, saves, followers   integers, or empty when not visible
  sells       yes | no   (ours only: does the post show something we sell)
  note        free text (hook, topic)

Rules (from the daily-intelligence brief):
  engagement = likes + comments + shares + saves (empty counts as not visible, at least one must be visible)
  rate = engagement / views; when views are not visible, engagement / followers, and the basis is reported
  competitors: posts published in the last 72 hours; ours: the last 7 days against our 30-day average
  paid candidate: ours, published within 48 hours, sells = yes, and rate >= 1.5 x our 30-day average rate
                  OR views >= 2 x our 30-day median views
A post read on several days is counted once, with its most recent reading.
Standard library only.
"""
import argparse
import csv
import datetime
import json
import statistics
import sys

COLUMNS = ["seen_on", "owner", "account", "platform", "url", "posted_on", "format", "views", "likes", "comments",
           "shares", "saves", "followers", "sells", "note"]
NUMS = ["views", "likes", "comments", "shares", "saves", "followers"]
PLATFORMS = {"instagram", "tiktok", "x", "linkedin", "facebook", "youtube"}
FORMATS = {"reel", "carousel", "photo", "video", "thread", "text"}


def parse_date(s, where, errors):
    try:
        return datetime.date.fromisoformat(s.strip())
    except ValueError:
        errors.append(f"{where}: bad date '{s}' (use YYYY-MM-DD)")
        return None


def load(path):
    """Returns (rows, errors). Numbers become int or None (not visible)."""
    errors, rows = [], []
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            return [], [f"missing columns: {', '.join(missing)}"]
        for i, r in enumerate(reader, start=2):
            where = f"line {i}"
            if not any((v or "").strip() for v in r.values()):
                continue
            row = {k: (r.get(k) or "").strip() for k in COLUMNS}
            row["line"] = i
            row["seen"] = parse_date(row["seen_on"], where, errors)
            row["posted"] = parse_date(row["posted_on"], where, errors)
            if row["owner"] not in ("ours", "competitor"):
                errors.append(f"{where}: owner must be 'ours' or 'competitor'")
            if row["platform"] not in PLATFORMS:
                errors.append(f"{where}: unknown platform '{row['platform']}'")
            if row["format"] and row["format"] not in FORMATS:
                errors.append(f"{where}: unknown format '{row['format']}'")
            if not row["url"].startswith("https://"):
                errors.append(f"{where}: every post needs its https link")
            if not row["account"]:
                errors.append(f"{where}: account is empty")
            for n in NUMS:
                v = row[n].replace(",", "")
                if v == "":
                    row[n] = None
                elif v.isdigit():
                    row[n] = int(v)
                else:
                    errors.append(f"{where}: {n} must be a whole number or empty, got '{row[n]}' "
                                  "(write 12500, not 12.5K; leave empty if not visible)")
                    row[n] = None
            if row["sells"] not in ("", "yes", "no"):
                errors.append(f"{where}: sells must be yes, no or empty")
            if row["seen"] and row["posted"] and row["posted"] > row["seen"]:
                errors.append(f"{where}: posted_on is after seen_on")
            rows.append(row)
    return rows, errors


def latest(rows):
    """One reading per post: the most recent one."""
    best = {}
    for r in rows:
        if r["seen"] and (r["url"] not in best or r["seen"] >= best[r["url"]]["seen"]):
            best[r["url"]] = r
    return list(best.values())


def measure(r):
    """Adds engagement, rate and its basis. A rate is None when it cannot be computed from visible numbers."""
    parts = [r[k] for k in ("likes", "comments", "shares", "saves") if r[k] is not None]
    r["engagement"] = sum(parts) if parts else None
    r["rate"], r["basis"] = None, "غير متاح"
    if r["engagement"] is not None:
        if r["views"]:
            r["rate"], r["basis"] = r["engagement"] / r["views"], "views"
        elif r["followers"]:
            r["rate"], r["basis"] = r["engagement"] / r["followers"], "followers"
    return r


def brief(r):
    return {"account": r["account"], "platform": r["platform"], "url": r["url"], "posted_on": r["posted_on"],
            "format": r["format"] or "غير متاح", "views": r["views"] if r["views"] is not None else "غير متاح",
            "engagement": r["engagement"] if r["engagement"] is not None else "غير متاح",
            "rate_pct": round(r["rate"] * 100, 2) if r["rate"] is not None else "غير متاح", "rate_basis": r["basis"],
            "note": r["note"]}


def report(rows, day):
    posts = [measure(r) for r in latest([r for r in rows if r["seen"] and r["seen"] <= day])]
    age = lambda r: (day - r["posted"]).days  # noqa: E731
    comp = [r for r in posts if r["owner"] == "competitor" and 0 <= age(r) <= 3]
    ours30 = [r for r in posts if r["owner"] == "ours" and 0 <= age(r) <= 30]
    ours7 = [r for r in ours30 if age(r) <= 7]
    rates = [r["rate"] for r in ours30 if r["rate"] is not None and r["basis"] == "views"]
    views = [r["views"] for r in ours30 if r["views"] is not None]
    avg_rate = sum(rates) / len(rates) if rates else None
    med_views = statistics.median(views) if views else None

    candidates = []
    for r in ours7:
        if age(r) > 2 or r["sells"] != "yes":
            continue
        by_rate = avg_rate and r["rate"] is not None and r["basis"] == "views" and r["rate"] >= 1.5 * avg_rate
        by_views = med_views and r["views"] is not None and r["views"] >= 2 * med_views
        if by_rate or by_views:
            c = brief(r)
            c["why"] = " and ".join(x for x in (
                f"rate {r['rate'] * 100:.2f}% >= 1.5 x average {avg_rate * 100:.2f}%" if by_rate else "",
                f"views {r['views']} >= 2 x median {med_views:g}" if by_views else "") if x)
            candidates.append(c)

    return {
        "date": day.isoformat(),
        "method": {"engagement": "likes + comments + shares + saves (visible ones only)",
                   "rate": "engagement / views; engagement / followers when views are not visible",
                   "competitor_window": "posts published in the last 72 hours",
                   "own_window": "last 7 days against our 30-day figures",
                   "paid_candidate": "ours, within 48 hours, sells = yes, and rate >= 1.5 x our 30-day average rate "
                                     "(views basis) or views >= 2 x our 30-day median views"},
        "competitors": {
            "posts_in_window": len(comp),
            "top_by_views": [brief(r) for r in sorted((r for r in comp if r["views"] is not None),
                                                      key=lambda r: -r["views"])[:5]],
            "top_by_rate": [brief(r) for r in sorted((r for r in comp if r["rate"] is not None),
                                                     key=lambda r: -r["rate"])[:5]],
        },
        "ours": {
            "posts_last_7_days": [brief(r) for r in sorted(ours7, key=lambda r: r["posted_on"], reverse=True)],
            "average_rate_pct_30d": round(avg_rate * 100, 2) if avg_rate is not None else "غير متاح",
            "average_rate_from_posts": len(rates),
            "median_views_30d": med_views if med_views is not None else "غير متاح",
            "paid_campaign_candidates": candidates,
            "paid_note": "Recommendation only. Never launch ads or spend money.",
        },
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("init", "check", "report"):
        p = sub.add_parser(name)
        p.add_argument("log")
        if name == "report":
            p.add_argument("--date", help="report day, YYYY-MM-DD (default: today)")
    a = ap.parse_args()

    if a.cmd == "init":
        try:
            with open(a.log, "x", encoding="utf-8-sig", newline="") as f:
                csv.writer(f).writerow(COLUMNS)
        except FileExistsError:
            raise SystemExit(f"ERROR: {a.log} already exists; it is never overwritten.")
        print(f"created {a.log}")
        return 0

    rows, errors = load(a.log)
    if errors:
        print("\n".join("ERROR: " + e for e in errors), file=sys.stderr)
        return 1
    if a.cmd == "check":
        print(f"{a.log}: {len(rows)} readings, {len(latest(rows))} posts, 0 errors")
        return 0
    try:
        day = datetime.date.fromisoformat(a.date) if a.date else datetime.date.today()
    except ValueError:
        raise SystemExit("ERROR: --date must be YYYY-MM-DD")
    print(json.dumps(report(rows, day), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
