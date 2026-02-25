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
            next(reader, None)
            for row in reader:
                if len(row) >= 2:
                    trans_dict[row[0].strip()] = row[1].strip()
    return trans_dict

def find_pdf(invoice_num, folder="I:\\groups\\fac2\\fabs\\stores\\FSSAP\\test_ignore\\donetest"):
    for filename in os.listdir(folder):
        if filename.lower().endswith('.pdf') and invoice_num.lower() in filename.lower():
            return os.path.abspath(os.path.join(folder, filename))
    return None

def run_automation():
    trans_dict = get_transactions('browse.csv')
    if not trans_dict:
        print("❌ No transactions found in CSV.")
        return

    with sync_playwright() as p:
        try:
            # Connect to your 'Debug' Chrome shortcut
            browser = p.chromium.connect_over_cdp("http://localhost:9222", slow_mo=1000)
            context = browser.contexts[0]
            
            # Create a fresh, dedicated tab for our automation to avoid hidden background processes
            page = context.new_page() 
        except Exception as e:
            print("❌ Could not connect to Chrome. Is it open with --remote-debugging-port=9222?")
            print(f"Error details: {e}")
            return

        for transaction, invoice in trans_dict.items():
            print(f"\n🔎 Processing Transaction: {transaction} (Invoice: {invoice})")
            
            # Find the file first
            file_path = find_pdf(invoice)
            if not file_path:
                print(f"⚠️ Skipping: No PDF found containing '{invoice}'")
                continue

            # Navigate to the specific invoice
            invoice_url = f"https://washington.assetworks.hosting/fmax/screen/PO_INVOICE_VIEW?tranxNo={transaction}"
            
            try:
                # wait_until="domcontentloaded" stops waiting once the core HTML is ready
                page.goto(invoice_url, wait_until="domcontentloaded", timeout=30000)
            except Exception as e:
                print(f"⚠️ Failed to load invoice page for {transaction}: {e}")
                continue

            try:
                # Wait for the specific 'moreMenu' element to prove the page is ready
                page.wait_for_selector('a[id="mainForm:sideButtonPanel:moreMenu_4"]', timeout=15000)
            except Exception as e:
                print(f"⚠️ The 'moreMenu' button never appeared for {transaction}. Skipping.")
                continue

            # --- INTERACTION STEPS ---
            try:
                # Navigation Steps
                page.get_by_role("link", name="Related Documents").click()
                page.get_by_role("button", name="Edit").click()
                page.get_by_role("button", name="Add").click()

                # Upload Steps
                input_selector = 'input[type="file"]' 
                page.set_input_files(input_selector, file_path)

                # Form Steps
                page.get_by_role("button", name="Next").click()
                
                # AssetWorks can be slow; we wait for the field to appear
                type_input = page.get_by_role("textbox", name="Type")
                type_input.wait_for(state="visible", timeout=10000)
                type_input.fill("VENDOR INVOICE")
                
                page.get_by_role("button", name="Next").click()
                page.get_by_role("button", name="Save").click()

                # Wait for the Download link to be visible on the page
                page.get_by_role("link", name="Download").wait_for(state="visible", timeout=10000)

                print(f"✅ Successfully attached {os.path.basename(file_path)}")
                
            except Exception as e:
                print(f"⚠️ Error during interaction steps for {transaction}: {e}")
                continue
            
            time.sleep(1) # Short breath between transactions

        # Close the dedicated tab when finished
        page.close()
        print("\n🏁 All transactions processed.")

if __name__ == "__main__":
    run_automation()