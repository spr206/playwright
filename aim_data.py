import os
import csv
import logging
from playwright.sync_api import sync_playwright

CSV_FILE = "browse.csv"


def fetch_browse_csv():
    """
    Uses Playwright to retrieve yesterday's PO invoices from AiM
    and writes them to browse.csv (columns: Transaction ID, Invoice Number).
    """
    with sync_playwright() as p:
        # --- PLAYWRIGHT STEPS (to be implemented) ---
        pass


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
