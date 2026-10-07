"""Daily new-listings feed in a Google Sheet.

Setup:
  1. Google Cloud console -> create a service account -> download its JSON key.
  2. Save it as service_account.json next to this file (it is gitignored).
  3. Share your spreadsheet with the service account's email address.

Each run appends homes listed in the last day (`listedWithinDays: 1`) for the
markets you watch, skipping property IDs already in the sheet. Put it on an
Apify schedule or a cron job and the sheet becomes a new-inventory alert board.

Actor: https://apify.com/pro100chok/realtor-com-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=realtor-com-listings-agents-scraper-python
"""
import os
from datetime import datetime, timezone

import gspread
from apify_client import ApifyClient
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

SPREADSHEET = "Realtor.com new listings"
WORKSHEET = "feed"
MARKETS = ["Tampa, FL", "St. Petersburg, FL"]
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
HEADER = ["collected_at", "property_id", "list_date", "address", "city", "zip",
          "price", "beds", "baths", "sqft", "year_built", "agent", "agent_phone",
          "office", "url"]

load_dotenv()
client = ApifyClient(os.environ["APIFY_API_TOKEN"])

run = client.actor("pro100chok/realtor-com-scraper").call(run_input={
    "scrapeType": "search",
    "location": MARKETS,
    "listingType": "for_sale",
    "listedWithinDays": 1,
    "priceMax": 600000,
    "includePermits": False,
    "maxItems": 300,
})

creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPES)
book = gspread.authorize(creds).open(SPREADSHEET)
try:
    ws = book.worksheet(WORKSHEET)
except gspread.WorksheetNotFound:
    ws = book.add_worksheet(WORKSHEET, rows=20000, cols=len(HEADER))
    ws.append_row(HEADER)

seen = set(ws.col_values(2)[1:])
stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
rows = []
for h in client.dataset(run["defaultDatasetId"]).iterate_items():
    pid = str(h.get("propertyId") or "")
    if not pid or pid in seen:
        continue
    seen.add(pid)
    rows.append([stamp, pid, h.get("listDate"), h.get("addressLine"), h.get("city"),
                 h.get("postalCode"), h.get("listPrice"), h.get("beds"), h.get("baths"),
                 h.get("sqft"), h.get("yearBuilt"), h.get("agentName"),
                 h.get("agentPhone"), h.get("officeName"), h.get("url")])

if rows:
    ws.append_rows(rows, value_input_option="USER_ENTERED")
print(f"Appended {len(rows)} new listings to {SPREADSHEET}/{WORKSHEET}")
