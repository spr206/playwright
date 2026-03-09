import os
import csv
import logging
from playwright.sync_api import sync_playwright

CSV_FILE = "browse.csv"
workdesk = "https://washington.assetworks.hosting/fmax/screen/WORKDESK" 

def fetch_browse_csv():
    """
    Uses Playwright to retrieve yesterday's PO invoices from AiM
    and writes them to browse.csv (columns: Transaction ID, Invoice Number).
    """
    with sync_playwright() as p:
        page = None
        page.goto(workdesk)
        page.get_by_role("link", name="Accounts Payable ~ Purchase Order Invoice ~ All Released Today").click()
            
        # Wait for the download to start
        with page.expect_download() as download_info:
            page.get_by_role("link", name="Export").click()

        # Grab the download object
        download = download_info.value

        # Save it to your specific directory
        # Note the 'r' before the string to handle Windows backslashes properly
        download.save_as(r"c:\\users\\spr206\\python\\playwright\\browse.csv")


def load_transactions(csv_file=CSV_FILE):
    """Reads browse.csv and returns a dict mapping Transaction ID -> Invoice Number."""
    trans_dict = {}
    if os.path.exists(csv_file):
        with open(csv_file, mode="r") as file:
            reader = csv.reader(file)
            next(reader, None)  # skip header
            for row in reader:
                if len(row) >= 2:
                    trans_dict[row[0].strip()] = row[1].strip()
    else:
        logging.error(f"CSV file '{csv_file}' not found.")
    return trans_dict
