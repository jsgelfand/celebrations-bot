# Celebrations Bot 🎉

A Slack bot that automatically posts birthday and work-anniversary shout-outs to
**#general** every morning at **7:00 AM Eastern**, @-mentioning the person and
(for anniversaries) noting their years of service.

It runs itself on a free GitHub Actions schedule — no server to maintain.

---

## What's in this folder

| File | What it is |
|------|------------|
| `shoutout.py` | The bot. Finds today's birthdays/anniversaries and posts the message. |
| `roster.json` | The 46 employees: name, Slack ID, birthday (month/day), hire date. **Edit this to add/remove people.** |
| `slack-app-manifest.yaml` | Definition of the Slack app, used to create it in one step. |
| `.github/workflows/daily-shoutout.yml` | The daily schedule (GitHub Actions). |
| `README.md` | This file. |

---

## ✅ Already done

- Cleaned the employee data into `roster.json`.
- Matched **all 46** employees to their Slack user IDs for @-mentions.
- Wrote and tested the bot logic (birthdays, anniversaries, years of service, multiple-people-same-day).
- Set the target channel to **#general** (`CBQKAQM39`) and the post time to **7 AM ET**.

## 🔑 Setup — reusing an existing bot token (recommended)

Since you already have a working `xoxb-` bot token (used in 2 other channels), you can
reuse it and skip creating/installing a new app. As long as that token has the
`chat:write` scope, you likely **don't need Jon at all**.

### 1. Add the existing bot to #general (30 sec)
In Slack: **#general** → channel name → **Integrations** → **Add apps** → pick the app
your token belongs to. A bot can only post in channels it's been added to. (#general
is an open channel, so you can do this yourself.)

### 2. Put the code on GitHub and add the token (5 min)
1. Create a new GitHub repo (private is fine) and upload everything in this folder,
   keeping the `.github/workflows/` path intact.
2. In the repo: **Settings → Secrets and variables → Actions → New repository secret**.
   - Name: `SLACK_BOT_TOKEN` — Value: your existing `xoxb-...` token.
   - (Optional) `SLACK_CHANNEL_ID` — only if you want a channel other than #general.
   - (Optional) `CUSTOM_BOT_NAME` = `1` — posts as "Celebrations Bot" with a 🎉 icon.
     **Only set this if the app has the `chat:write.customize` scope**; otherwise leave
     it off and messages post under the app's own name.
3. Open the **Actions** tab and enable workflows if prompted.

### 3. Test it
Run locally to force a real test post (replace with your token):
```bash
SLACK_BOT_TOKEN=xoxb-... python shoutout.py --force --date 2026-04-18
```
That posts April 18's two birthday shout-outs to #general. Or use the **Actions** tab →
**Daily Celebrations Shout-out** → **Run workflow** for a manual trigger.

That's it — from then on it posts on its own every morning at 7 AM ET.

---

## Alternative: create a brand-new "Celebrations Bot" app (needs admin approval)

Only if you'd rather have a dedicated bot than reuse the existing token. This usually
needs Jon to approve the workspace install.
1. <https://api.slack.com/apps> → **Create New App** → **From a manifest** → pick the
   workspace → paste `slack-app-manifest.yaml` → **Create**.
2. **Install to Workspace** → **Allow** (this is the step that may need admin approval).
3. **OAuth & Permissions** → copy the **Bot User OAuth Token** (`xoxb-...`).
4. Then follow steps 1–3 above (add to #general, GitHub repo, secret). This manifest
   already includes `chat:write.customize`, so you can set `CUSTOM_BOT_NAME=1`.

---

## How it behaves

- Posts **only** on days someone has a birthday or anniversary. Silent otherwise.
- Birthdays: `🎂 Happy Birthday @Name! ...`
- Anniversaries: `🎊 Happy work anniversary @Name — N years at Mission Staffing today! ...`
  (Counts from hire year; people hired this year are skipped until their 1-year mark.)
- Multiple people on the same day are all included in one message.

## Maintaining it

Adding, removing, or fixing an employee = edit `roster.json` and commit. Fields:
```json
{
  "name": "First Last",
  "slack_id": "U0XXXXXX",   // null if unknown — bot will use the plain name instead
  "birth_month": 4, "birth_day": 18,
  "hire_month": 1, "hire_day": 13, "hire_year": 2025
}
```
To get someone's Slack ID: click their profile → ••• → **Copy member ID**.

---

## Data notes (resolved)

All three earlier data questions are now fixed in `roster.json`:
- **Carolyn Bienvenu** → mapped to her Slack account "Taylor Bienvenu" (`U0A9UB5C9S6`).
- **Kunal Vyas** → mapped to "Kyle Vyas" (`U0AFNPZ7SN5`).
- **Cindy Lin** → hire year corrected to **2024**.

## Scheduling note
GitHub Actions cron can occasionally be delayed a few minutes under heavy load — normal and harmless for a morning shout-out.
