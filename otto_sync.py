import os
import csv
import time
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright


class OttoSync:
    def __init__(self, csv_file='browse.csv'):
        """Initializes the class and loads the transaction dictionary."""
        self.csv_file = csv_file
        self.trans_dict = self._get_transactions()
        self.playwright = None
        self.browser = None
        self.page = None

    def _get_transactions(self):
        """Reads the CSV and maps Transaction IDs to Invoice Numbers."""
        trans_dict = {}
        if os.path.exists(self.csv_file):
            with open(self.csv_file, mode='r') as file:
                reader = csv.reader(file)
                next(reader, None)
                for row in reader:
                    if len(row) >= 2:
                        trans_dict[row[0].strip()] = row[1].strip()
        else:
            logging.error(f"CSV file '{self.csv_file}' not found.")
        return trans_dict

    def __enter__(self):
        """Starts Playwright and connects to the existing Chrome instance."""
        self.playwright = sync_playwright().start()
        try:
            self.browser = self.playwright.chromium.connect_over_cdp(
                "http://localhost:9222", slow_mo=1000)
            context = self.browser.contexts[0]
            self.page = context.pages[0]
            logging.info("Successfully connected to Chrome CDP (Port 9222).")
        except Exception as e:
            logging.error(
                "Could not connect to Chrome. Is it open with --remote-debugging-port=9222?")
            raise e  # Pass the error up so main.py catches it

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensures Playwright closes safely when the 'with' block ends."""
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

        for trans, inv in self.trans_dict.items():

            print(f"\n🔎 Processing Transaction: {transaction_id} (Invoice: {invoice_num})")

            if inv.lower() in file_name:
                transaction_id = trans
                invoice_num = inv
                break

        if not transaction_id:
            logging.warning(
                f"No matching invoice found in CSV for file: {file_name}")
            return False

        # 2. Run the Playwright automation for this specific file
        try:
            logging.info(
                f"Processing Transaction: {transaction_id} (Invoice: {invoice_num})")

            invoice_url = f"https://washington.assetworks.hosting/fmax/screen/PO_INVOICE_VIEW?tranxNo={transaction_id}"
            self.page.goto(invoice_url)

            # --- NAVIGATION STEPS ---
            self.page.get_by_role("link", name="Related Documents").click()
            self.page.get_by_role("button", name="Edit").click()
            self.page.get_by_role("button", name="Add").click()

            # --- UPLOAD STEPS ---
            input_selector = 'input[type="file"]'
            self.page.set_input_files(input_selector, file_path)

            # --- FORM STEPS ---
            self.page.get_by_role("button", name="Next").click()
            
            #Do these need to be self.type_input?
            type_input = self.page.get_by_role("textbox", name="Type")
            type_input.wait_for(state="visible", timeout=10000)
            type_input.fill("VENDOR INVOICE")

            self.page.get_by_role("button", name="Next").click()
            self.page.get_by_role("button", name="Save").click()

            # Wait for the Download link to be visible on the page
            self.page.get_by_role("link", name="Download").wait_for(state="visible", timeout=10000)

            print(f"✅ Successfully attached {os.path.basename(file_path)}")

            logging.info(
                f"✅ Successfully attached {file_name} to transaction {transaction_id}")
            time.sleep(1)  # Short breath between transactions
            return True

        except Exception as e:
            logging.error(f"⚠️ Automation failed for {file_name}: {str(e)}")
            return False
