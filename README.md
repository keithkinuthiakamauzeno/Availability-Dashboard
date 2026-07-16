# Zeno Availability Dashboard — Setup Guide

Live dashboard that auto-refreshes from two private Google Sheets every hour.

---

## What you need before starting

- A Google account with access to both sheets
- A GitHub account (free)
- 30–45 minutes

---

## Step 1 — Create a Google Cloud service account

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click **Select a project** → **New Project** → name it anything (e.g. `zeno-dashboard`) → **Create**
3. In the left menu go to **APIs & Services → Library**
4. Search for **Google Sheets API** → click it → **Enable**
5. In the left menu go to **APIs & Services → Credentials**
6. Click **+ Create Credentials → Service Account**
   - Name: `zeno-dashboard` (anything)
   - Click **Create and Continue** → **Done** (skip the optional steps)
7. Click the service account you just created → go to the **Keys** tab
8. **Add Key → Create new key → JSON → Create**
9. A `.json` file downloads — **keep this safe, treat it like a password**

Your service account has an email like:
```
zeno-dashboard@your-project-id.iam.gserviceaccount.com
```
You'll see it on the Credentials page. Copy it.

---

## Step 2 — Share both Google Sheets with the service account

1. Open your **State Changes** Google Sheet
2. Click **Share** (top right)
3. Paste the service account email → set role to **Viewer** → **Send**
4. Repeat for your **Station Master** sheet

---

## Step 3 — Get your Sheet IDs

Your Sheet ID is the long string in the URL:
```
https://docs.google.com/spreadsheets/d/THIS_IS_YOUR_SHEET_ID/edit
```

Note down both IDs — you'll need them in Step 5.

If your data is not on the first tab (Sheet1), also note the **tab name** exactly as it appears.

---

## Step 4 — Create a GitHub repository

1. Go to [github.com](https://github.com) → **New repository**
2. Name it anything (e.g. `zeno-dashboard`)
3. Set visibility to **Public** (required for free GitHub Pages)
4. Click **Create repository**
5. Upload all the files from this folder into the repo
   - You can drag-and-drop them in the GitHub web interface
   - Or use `git push` if you're comfortable with git

---

## Step 5 — Add secrets to GitHub

Your credentials must never be in the code. GitHub encrypts secrets and injects them at runtime.

1. In your GitHub repo → **Settings → Secrets and variables → Actions**
2. Click **New repository secret** for each of these:

| Secret name | Value |
|---|---|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | The **entire contents** of the `.json` file from Step 1 (open it in a text editor, copy everything) |
| `STATE_SHEET_ID` | Your state changes sheet ID from Step 3 |
| `MASTER_SHEET_ID` | Your station master sheet ID from Step 3 |

If your tabs aren't named `Sheet1`, also add:

| Secret name | Value |
|---|---|
| `STATE_TAB` | Exact tab name in your state changes sheet |
| `MASTER_TAB` | Exact tab name in your station master sheet |

---

## Step 6 — Enable GitHub Pages

1. In your repo → **Settings → Pages**
2. Under **Source** → select **Deploy from a branch**
3. Branch: **main** · Folder: **/ (root)**
4. Click **Save**

After a minute, GitHub shows your live URL:
```
https://yourusername.github.io/zeno-dashboard/
```

---

## Step 7 — Run the Action manually to test

1. In your repo → **Actions** tab
2. Click **Refresh dashboard data** in the left list
3. Click **Run workflow → Run workflow**
4. Watch it run — should take about 30 seconds
5. Check that `data/state_changes.csv` and `data/station_master.csv` now have real data (click them in the repo)
6. Open your GitHub Pages URL — the dashboard should load automatically

---

## How it works after setup

```
Every hour (automatic):
  GitHub Action runs fetch_sheets.py
      ↓
  Pulls both private sheets using service account
      ↓
  Writes data/state_changes.csv and data/station_master.csv
      ↓
  Commits and pushes to repo
      ↓
  GitHub Pages serves updated files instantly

When someone visits the dashboard URL:
  Browser fetches data/state_changes.csv and data/station_master.csv
      ↓
  Parses and renders everything client-side
      ↓
  Auto-refreshes every 10 minutes while the tab is open
```

---

## Changing the refresh frequency

Edit `.github/workflows/refresh-data.yml`, line with `cron:`:

| Schedule | Cron expression | Actions minutes/month |
|---|---|---|
| Every hour | `0 * * * *` | ~1,440 ✅ free |
| Every 30 min | `*/30 * * * *` | ~2,880 ⚠ slightly over free tier |
| Every 15 min | `*/15 * * * *` | ~5,760 ❌ needs paid plan |

GitHub's free tier includes 2,000 minutes/month. Hourly is comfortably free.

Note: the dashboard also auto-refreshes in the browser every 10 minutes regardless of the cron schedule. So if someone has the tab open they'll see data at most 10 minutes stale even on an hourly cron.

---

## Troubleshooting

**Action fails with "GOOGLE_SERVICE_ACCOUNT_JSON not set"**
→ Check the secret name matches exactly (case-sensitive)

**Action fails with "403 Forbidden" or "The caller does not have permission"**
→ You haven't shared the sheet with the service account email (Step 2)

**Action fails with "Worksheet not found"**
→ Your tab isn't named Sheet1 — add STATE_TAB / MASTER_TAB secrets with the correct names

**Dashboard shows "Auto-load failed"**
→ The Action hasn't run yet, or the CSVs are still empty placeholders — run it manually (Step 7)

**Dashboard loads but shows no data**
→ Open browser DevTools (F12) → Console — check for errors. Most likely the column names in your sheet don't match expected format.
