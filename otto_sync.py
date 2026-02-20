import os
import csv
import time
from playwright.sync_api import sync_playwright

# 1. Load configuration
def get_transactions(csv_file):
    trans_dict = {}
    if os.path.exists(csv_file):
        with open(csv_file, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2:
                    trans_dict[row[0].strip()] = row[1].strip()
    return trans_dict

def find_pdf(invoice_num, folder="./pdf_in"):
    for filename in os.listdir(folder):
        if filename.lower().endswith('.pdf') and invoice_num.lower() in filename.lower():
            return os.path.abspath(os.path.join(folder, filename))
    return None

def run_automation():
    trans_dict = get_transactions('browse_test.csv')
    if not trans_dict:
        print("❌ No transactions found in CSV.")
        return

    with sync_playwright() as p:
        # Connect to your 'Debug' Chrome shortcut (Port 9222)
       
        try:
            # browser = p.chromium.connect_over_cdp("http://localhost:9222")
            # Added slow_mo
            browser = p.chromium.connect_over_cdp("http://localhost:9222", slow_mo=1000)
            context = browser.contexts[0]
            page = context.pages[0] 
        except Exception as e:
            print("❌ Could not connect to Chrome. Is it open with --remote-debugging-port=9222?")
            return

        for transaction, invoice in trans_dict.items():
            print(f"🔎 Processing Transaction: {transaction} (Invoice: {invoice})")
            
            # Find the file first
            file_path = find_pdf(invoice)
            if not file_path:
                print(f"⚠️ Skipping: No PDF found containing '{invoice}'")
                continue

            # Navigate to the specific invoice
            invoice_url = f"https://washingtontest.assetworks.hosting/fmax/screen/PO_INVOICE_VIEW?tranxNo={transaction}"
            page.goto(invoice_url)

            #Added timeout
            page.set_default_timeout(10000)

            # --- NAVIGATION STEPS ---
            # Using 'wait_for_selector' is faster than 'time.sleep'
            page.get_by_role("link", name="Related Documents").click()
            page.get_by_role("button", name="Edit").click()
            page.get_by_role("button", name="Add").click()

            # --- UPLOAD STEPS ---
            # We target the ID you found in your previous code
            input_selector = 'input[type="file"]' # Or '#mainForm\\:DOC_LOADER_WIZARD_STEP1_content\\:newFileUploadWidget'
            page.set_input_files(input_selector, file_path)

            # --- FORM STEPS ---
            page.get_by_role("button", name="Next").click()
            
            # AssetWorks can be slow; we wait for the field to appear
            type_input = page.get_by_role("textbox", name="Type")
            type_input.wait_for(state="visible")
            type_input.fill("VENDOR INVOICE")
            
            page.get_by_role("button", name="Next").click()
            page.get_by_role("button", name="Save").click()

            print(f"✅ Successfully attached {os.path.basename(file_path)}")
            time.sleep(1) # Short breath between transactions

        print("🏁 All transactions processed.")

if __name__ == "__main__":
    run_automation()