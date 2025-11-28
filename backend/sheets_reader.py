import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ---- CONFIG ----
SHEET_NAME = "DailyJournal" 
WORKSHEET_NAME = "Journal"  
KEY_FILE = "dailylifeinsights-25eb2f336dd0.json"  

# ---- GOOGLE SHEETS SETUP ----
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    KEY_FILE, scope
)

client = gspread.authorize(creds)


def get_journal_rows():
    """Reads all rows from Google Sheet journal tab"""
    sheet = client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)
    rows = sheet.get_all_values()
    return rows


if __name__ == "__main__":
    # Debug test
    data = get_journal_rows()
    for r in data:
        print(r)
