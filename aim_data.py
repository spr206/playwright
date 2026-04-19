import csv
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
from otto_sync import CHROME_PROFILE_DIR

WORKDESK_URL = "https://washington.assetworks.hosting/fmax/screen/WORKDESK"


def fetch_browse_csv():
    """
    Uses Playwright to retrieve today's PO invoices from AiM and saves them
    to a temporary CSV file. Returns the Path to that file.
    """
    tmp_path = Path(tempfile.gettempdir()) / "otto_browse_temp.csv"

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(CHROME_PROFILE_DIR),
            headless=False,
            slow_mo=1000,
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(WORKDESK_URL)
        page.get_by_role("link", name="Accounts Payable ~ Purchase Order Invoice ~ All Released Today").click()

        with page.expect_download() as download_info:
            page.get_by_role("link", name="Export").click()

        download_info.value.save_as(str(tmp_path))
        context.close()

    return tmp_path


def load_transactions(csv_file):
    """Reads a CSV file and returns a dict mapping Transaction ID -> Invoice Number."""
    trans_dict = {}
    csv_path = Path(csv_file)
    if csv_path.exists():
        with open(csv_path, mode="r") as file:
            reader = csv.reader(file)
            next(reader, None)  # skip header
            for row in reader:
                if len(row) >= 2:
                    trans_dict[row[0].strip()] = row[1].strip()
    else:
        print(f"CSV file '{csv_file}' not found.")
    return trans_dict
