import os
import re
import time
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright

CHROME_PROFILE_DIR = (
    Path(os.environ["LOCALAPPDATA"]) / "ChromeProfile-Playwright-Nuitka-Deployment"
)


class OttoSync:
    def __init__(self, trans_dict, base_url):
        """Initializes the class with a pre-loaded transaction dictionary."""
        self.trans_dict = trans_dict
        self.base_url = base_url
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
                self.context.pages[0] if self.context.pages else self.context.new_page()
            )
            logging.info(f"Launched Chromium with profile at {CHROME_PROFILE_DIR}.")
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

    def process_file(self, file_path):
        """
        Processes a single file passed from main.py.
        Returns True if successful, False if it fails.
        """
        if not self.trans_dict:
            logging.error("No transactions found in CSV to process.")
            return False

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
            logging.warning(f"No matching invoice found in CSV for file: {file_name}")
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
            self.page.get_by_role("button", name="Add").evaluate("node => node.click()")

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
            self.page.get_by_role("button", name="Save").evaluate(
                "node => node.click()"
            )

            # Wait for the Download link to be visible on the page
            self.page.get_by_role("link", name="Download").wait_for(
                state="visible", timeout=10000
            )

            print(f"\n✅ Attached {file_name} to transaction {transaction_id}")

            logging.info(f"\n✅ Attached {file_name} to transaction {transaction_id}")
            time.sleep(1)  # Short breath between transactions
            return match_type

        except Exception as e:
            logging.error(f"⚠️ Automation failed for {file_name}: {str(e)}")
            return False
