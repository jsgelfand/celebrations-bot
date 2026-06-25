#!/usr/bin/env python3
"""
Celebrations Bot — posts daily birthday & work-anniversary shout-outs to Slack.

Runs once per morning (07:00 America/New_York). Reads roster.json, finds whose
birthday or work anniversary is today, builds a message that @-mentions each
person, and posts it to the configured Slack channel as "Celebrations Bot".

Environment variables:
  SLACK_BOT_TOKEN   (required to post)  Slack bot token, starts with "xoxb-"
  SLACK_CHANNEL_ID  (optional)          Channel to post in. Default: #general.
  CUSTOM_BOT_NAME   (optional)          Set to "1"/"true" to post as "Celebrations
                                        Bot" with a 🎉 icon. Requires the app to have
                                        the chat:write.customize scope. Leave unset to
                                        post under the app's own name (works with any
                                        chat:write token).

Useful flags:
  --dry-run            Print the message instead of posting (no token needed).
  --date YYYY-MM-DD    Pretend today is this date (for testing).
  --force              Skip the "only run at 7am ET" time guard.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
except ImportError:  # Python < 3.9 fallback
    ZoneInfo = None

EASTERN = ZoneInfo("America/New_York") if ZoneInfo else None
DEFAULT_CHANNEL = "CBQKAQM39"  # #general
ROSTER_PATH = Path(__file__).with_name("roster.json")


def now_eastern():
    return datetime.now(EASTERN) if EASTERN else datetime.now()


def load_roster():
    with open(ROSTER_PATH) as f:
        return json.load(f)


def mention(person):
    """Return a Slack mention if we have an ID, otherwise the bold plain name."""
    sid = person.get("slack_id")
    return f"<@{sid}>" if sid else f"*{person['name']}*"


def find_celebrations(roster, today):
    birthdays = [
        p for p in roster
        if p["birth_month"] == today.month and p["birth_day"] == today.day
    ]
    anniversaries = []
    for p in roster:
        if p["hire_month"] == today.month and p["hire_day"] == today.day:
            years = today.year - p["hire_year"]
            if years >= 1:
                anniversaries.append((p, years))
    return birthdays, anniversaries


def build_message(birthdays, anniversaries):
    if not birthdays and not anniversaries:
        return None
    blocks = []
    if birthdays:
        lines = [
            f"🎂 Happy Birthday {mention(p)}! Hope you have a great day! 🎉"
            for p in birthdays
        ]
        blocks.append("\n".join(lines))
    if anniversaries:
        lines = []
        for p, years in anniversaries:
            unit = "year" if years == 1 else "years"
            lines.append(
                f"🎊 Happy work anniversary {mention(p)} — {years} {unit} at "
                f"Mission Staffing today! Thank you for all you do! 🙌"
            )
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def post_to_slack(token, channel, text):
    body = {
        "channel": channel,
        "text": text,
        "link_names": True,
    }
    # Custom name/icon only works if the app has the chat:write.customize scope.
    # Off by default so any chat:write token works; opt in with CUSTOM_BOT_NAME=1.
    if os.environ.get("CUSTOM_BOT_NAME", "").lower() in ("1", "true", "yes"):
        body["username"] = "Celebrations Bot"
        body["icon_emoji"] = ":tada:"
    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        "https://slack.com/api/chat.postMessage",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    if not result.get("ok"):
        raise RuntimeError(f"Slack API error: {result.get('error')} ({result})")
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--date")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if args.date:
        today = datetime.strptime(args.date, "%Y-%m-%d")
    else:
        today = now_eastern()

    # Time guard: GitHub Actions fires this at both 11:00 and 12:00 UTC so that
    # exactly one run lands on 07:00 Eastern year-round (handles DST). We only
    # proceed when it is actually the 7 o'clock hour in Eastern time.
    if not args.force and not args.date:
        if now_eastern().hour != 7:
            print(f"Not 7am Eastern (currently {now_eastern():%H:%M %Z}); exiting.")
            return

    roster = load_roster()
    birthdays, anniversaries = find_celebrations(roster, today)
    message = build_message(birthdays, anniversaries)

    if message is None:
        print(f"No birthdays or anniversaries on {today:%Y-%m-%d}. Nothing to post.")
        return

    print("---- Message ----")
    print(message)
    print("-----------------")

    if args.dry_run:
        print("(dry run — not posted)")
        return

    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        print("ERROR: SLACK_BOT_TOKEN not set. Cannot post.", file=sys.stderr)
        sys.exit(1)
    channel = os.environ.get("SLACK_CHANNEL_ID", DEFAULT_CHANNEL)
    post_to_slack(token, channel, message)
    print(f"Posted to channel {channel}.")


if __name__ == "__main__":
    main()
