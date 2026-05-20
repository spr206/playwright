import csv
import os
import re
import sys
import tempfile
import time
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright

if "__compiled__" in globals():
    CHROME_PROFILE_DIR = Path(sys.executable).parent / "chrome_profile"
else:
    CHROME_PROFILE_DIR = Path(os.environ["LOCALAPPDATA"]) / "ChromeProfile-Playwright-Nuitka-Deployment"


class OttoSync:
    def __init__(self, base_url):
        self.base_url = base_url
        self.trans_dict = None
        self.playwright = None
        self.context = None
        self.page = None

    def __enter__(self):
        """Starts Playwright and launches Chromium with a persistent profile."""
        self.playwright = sync_playwright().start()
        try:
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(CHROME_PROFILE_DIR),
                headless=False,
                slow_mo=1000,
            )
            self.page = (
                self.context.pages[0] if self.context.pages else self.context.new_page(
                )
            )
            logging.info(
                f"Launched Chromium with profile at {CHROME_PROFILE_DIR}.")
        except Exception as e:
            logging.error(f"Could not launch Chromium: {e}")
            raise e

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensures Playwright closes safely when the 'with' block ends."""
        if self.context:
            self.context.close()
        if self.playwright:
            self.playwright.stop()
            logging.info("Playwright session closed.")

    def fetch_transactions(self):
        """Downloads today's released PO invoices from AiM and loads them into trans_dict."""
        workdesk_url = f"{self.base_url}/fmax/screen/WORKDESK"
        self.page.goto(workdesk_url, timeout=90000)
        self.page.get_by_role(
            "link",
            name="Accounts Payable ~ Purchase Order Invoice ~ All Released Today",
        ).click()

        tmp_path = Path(tempfile.gettempdir()) / "otto_browse_temp.csv"
        with self.page.expect_download() as download_info:
            self.page.get_by_role("link", name="Export").click()
        download_info.value.save_as(str(tmp_path))

        self.trans_dict = {}
        with open(tmp_path, mode="r") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) >= 2:
                    self.trans_dict[row[0].strip()] = row[1].strip()

        tmp_path.unlink(missing_ok=True)
        logging.info(f"Loaded {len(self.trans_dict)} transactions from AiM.")

    def process_file(self, file_path):
        """Processes a single file. Returns 'exact', 'partial', or False."""
        file_name = Path(file_path).name.lower()

        # 1. Match the file to a transaction in the CSV
        transaction_id = None
        invoice_num = None
        match_type = None

        # Pass 1 — exact substring
        for trans, inv in self.trans_dict.items():
            if inv.lower() in file_name:
                transaction_id = trans
                invoice_num = inv
                match_type = "exact"
                break

        # Pass 2 — partial (strip non-alphanumeric chars from invoice number)
        if not transaction_id:
            best_len = 0
            for trans, inv in self.trans_dict.items():
                cleaned = re.sub(r"[^a-z0-9]", "", inv.lower())
                if cleaned and cleaned in file_name and len(cleaned) > best_len:
                    transaction_id = trans
                    invoice_num = inv
                    match_type = "partial"
                    best_len = len(cleaned)

        if not transaction_id:
            logging.warning(
                f"No matching invoice found in CSV for file: {file_name}")
            return False

        if match_type == "partial":
            logging.warning(
                f"Partial match used for {file_name}: invoice '{invoice_num}'"
            )

        print(
            f"\n🔎 [{match_type.upper()} MATCH] Transaction: {transaction_id} (Invoice: {invoice_num})"
        )

        # 2. Run the Playwright automation for this specific file
        try:
            logging.info(
                f"Processing Transaction: {transaction_id} (Invoice: {invoice_num})"
            )

            invoice_url = (
                f"{self.base_url}/fmax/screen/PO_INVOICE_VIEW?tranxNo={transaction_id}"
            )
            self.page.goto(invoice_url)

            # --- NAVIGATION STEPS ---
            # self.page.get_by_role("link", name="Related Documents").click()
            self.page.get_by_role("link", name="Related Documents").evaluate(
                "node => node.click()"
            )
            self.page.get_by_role("button", name="Edit").evaluate(
                "node => node.click()"
            )
            self.page.get_by_role("button", name="Add").evaluate(
                "node => node.click()")

            # --- UPLOAD STEPS ---
            input_selector = 'input[type="file"]'
            self.page.set_input_files(input_selector, file_path)

            # --- FORM STEPS ---
            self.page.get_by_role("button", name="Next").evaluate(
                "node => node.click()"
            )

            type_input = self.page.get_by_role("textbox", name="Type")
            type_input.wait_for(state="visible", timeout=10000)
            doc_type = (
                "EMAIL ATTACHMENT"
                if Path(file_path).suffix.lower() == ".msg"
                else "VENDOR INVOICE"
            )
            type_input.fill(doc_type)

            self.page.get_by_role("button", name="Next").evaluate(
                "node => node.click()"
            )


    # Failing here
            self.page.get_by_role("button", name="Save").evaluate(
                "node => node.click()"
            )

    
    # # Try this instead
    #         # 1. Wait for the page reload that happens after saving.
    #         # Added a 30s timeout here just in case the server is chugging.
    #         with self.page.expect_navigation(timeout=30000):
    #             self.page.get_by_role("button", name="Save").evaluate("node => node.click()")

    #         # 2. Wait for the Download link.
    #         # Bumped to 30 seconds (30000ms) to account for legacy SaaS processing times.
    #         self.page.get_by_role("link", name="Download").wait_for(
    #             state="visible", timeout=30000
    #         )

    # This isn't working and sometimes timing out here
            # Wait for the Download link to be visible on the page
            self.page.get_by_role("link", name="Download").wait_for(
                state="visible", timeout=10000
            )

            print(f"\n✅ Attached {file_name} to transaction {transaction_id}")

            logging.info(
                f"\n✅ Attached {file_name} to transaction {transaction_id}")
            time.sleep(1)  # Short breath between transactions
            return match_type

        except Exception as e:
            logging.error(f"⚠️ Automation failed for {file_name}: {str(e)}")
            return False
