"""
fetch_sheets.py
───────────────
Pulls two private Google Sheets using a service account and writes them
as CSVs into data/. Run by GitHub Actions on a schedule.

Required environment variables (set as GitHub Actions secrets):
  GOOGLE_SERVICE_ACCOUNT_JSON  — the full contents of your service account key.json
  STATE_SHEET_ID               — Google Sheet ID for the state changes log
  MASTER_SHEET_ID              — Google Sheet ID for the station master

Sheet IDs are the long string in the URL:
  https://docs.google.com/spreadsheets/d/THIS_IS_THE_ID/edit
"""

import os, json, csv, sys
from pathlib import Path

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    print("Missing dependencies. Run: pip install gspread google-auth")
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────────────────────

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

STATE_SHEET_ID  = os.environ['STATE_SHEET_ID']
MASTER_SHEET_ID = os.environ['MASTER_SHEET_ID']

# Tab names inside each sheet — change if yours differ
STATE_TAB   = os.environ.get('STATE_TAB',  'Battery State Changes')
MASTER_TAB  = os.environ.get('MASTER_TAB', 'SS Locs')

OUTPUT_DIR  = Path('data')
OUTPUT_DIR.mkdir(exist_ok=True)

# ── Auth ──────────────────────────────────────────────────────────────────────

def get_client():
    key_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
    if not key_json:
        raise EnvironmentError('GOOGLE_SERVICE_ACCOUNT_JSON not set')
    info = json.loads(key_json)
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    return gspread.authorize(creds)

# ── Fetch & write ─────────────────────────────────────────────────────────────

def sheet_to_csv(gc, sheet_id, tab_name, out_path):
    print(f'  Fetching {sheet_id} / {tab_name} …')
    ws = gc.open_by_key(sheet_id).worksheet(tab_name)
    rows = ws.get_all_values()          # list of lists, first row is headers
    if not rows:
        print(f'  ⚠  No data returned from {tab_name}')
        return 0
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print(f'  ✓  {len(rows)-1} data rows → {out_path}')
    return len(rows) - 1

def main():
    print('Authenticating with Google Sheets …')
    gc = get_client()

    state_rows  = sheet_to_csv(gc, STATE_SHEET_ID,  STATE_TAB,
                                OUTPUT_DIR / 'state_changes.csv')
    master_rows = sheet_to_csv(gc, MASTER_SHEET_ID, MASTER_TAB,
                                OUTPUT_DIR / 'station_master.csv')

    print(f'\nDone — {state_rows} state events, {master_rows} stations written.')

if __name__ == '__main__':
    main()
