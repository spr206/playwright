import asyncio
import os
import csv
import re
import time
from playwright.async_api import Playwright, async_playwright, expect

#get login info
with open('loginInfo.txt', 'r', encoding='utf-8') as file:
    login_info = file.readlines()

username = login_info[0].strip()
password = login_info[1].strip()

def create_dictionary_from_csv(csv_file):
    result_dict = {}
    with open(csv_file, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 2:  # Assuming only two columns in each row
                key, value = row
                result_dict[key] = value
    return result_dict

# Path to the CSV file
csv_file = 'transactions.csv'
# Create dictionary from CSV
transDict = create_dictionary_from_csv(csv_file)

async def authenticate(playwright: Playwright) -> None:
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()

    #Login
    await page.goto("https://washingtontest.assetworks.hosting/fmax/screen/WORKDESK")
    # await page.goto("https://washingtontest.assetworks.hosting/fmax/screen/PO_INVOICE_VIEW?tranxNo=259474")

    await page.get_by_placeholder("UW NetID").fill(username)
    await page.get_by_placeholder("UW NetID").press("Tab")
    await page.get_by_placeholder("Password").fill(password)
    # await page.get_by_role("button", name="Sign in").click()
    await page.get_by_placeholder("Password").press("Enter")
    await page.get_by_role("button", name="Yes, this is my device").click()

    storage = await context.storage_state(path="state.json")


async def attach2(playwright: Playwright) -> None:
    browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
    default_context = browser.contexts[0]
    page = default_context.pages[0]
    for key, value in transDict.items():
        transaction = key
        invoice = value
        await page.goto("https://washingtontest.assetworks.hosting/fmax/screen/PO_INVOICE_VIEW?tranxNo=" + transaction)

        #Wait for page to load
        await page.wait_for_load_state("networkidle")

        if page.url == "https://idp.u.washington.edu/idp/profile/SAML2/Redirect/SSO?execution=e1s1":
            await page.get_by_placeholder("UW NetID").fill(username)
            await page.get_by_placeholder("UW NetID").press("Tab")
            await page.get_by_placeholder("Password").fill(password)
            time.sleep(5)
        await page.get_by_role("link", name="Related Documents").click()
        await page.get_by_role("button", name="Edit").click()
        await page.get_by_role("button", name="Add").click()
        await page.get_by_role("textbox", name="File").click()

        # Find PDF file in ./pdf_in with filename containing invoice number
        matching_files = []
        folder_path = "./pdf_in"
        for filename in os.listdir(folder_path):
            if filename.lower().endswith('.pdf') and invoice in filename.lower():
                matching_files.append(os.path.join(folder_path, filename))

        # Check if any matching file is found
        if matching_files:
            # Choose the first matching file
            pdf_file_path = matching_files[0]
            
            # Upload the file
            await page.get_by_role("textbox", name="File").fill(pdf_file_path)
            await page.get_by_role("button", name="Upload").click()
            await page.get_by_role("button", name="Next").click()
            await page.get_by_role("textbox", name="Type").fill("VENDOR INVOICE")
            await page.get_by_role("button", name="Next").click()
            await page.get_by_role("button", name="Save").click()
            print(f"Attached Invoice: {invoice}")

        else:
            print(f"No matching file found for invoice: {invoice}")

    print("Done!")

async def attach(playwright: Playwright) -> None:
    brower = await playwright.chromium.launch(headless=False)
    context = await brower.new_context(storage_state="state.json")
    page = await context.new_page()
    for key, value in transDict.items():
        transaction = key
        invoice = value
        await page.goto("https://washingtontest.assetworks.hosting/fmax/screen/PO_INVOICE_VIEW?tranxNo=" + transaction)

        #Wait for page to load
        await page.wait_for_load_state("networkidle")
        
        if page.url == "https://idp.u.washington.edu/idp/profile/SAML2/Redirect/SSO?execution=e1s1":
            await authenticate(playwright)
        else:
            await page.get_by_role("link", name="Related Documents").click()
            await page.get_by_role("button", name="Edit").click()
            await page.get_by_role("button", name="Add").click()
            await page.get_by_role("textbox", name="File").click()

        # Find PDF file in ./pdf_in with filename containing invoice number
        matching_files = []
        folder_path = "./pdf_in"
        for filename in os.listdir(folder_path):
            if filename.lower().endswith('.pdf') and invoice in filename.lower():
                matching_files.append(os.path.join(folder_path, filename))

        # Check if any matching file is found
        if matching_files:
            # Choose the first matching file
            pdf_file_path = matching_files[0]
            
            # Upload the file
            await page.get_by_role("textbox", name="File").fill(pdf_file_path)
            await page.get_by_role("button", name="Upload").click()
            await page.get_by_role("button", name="Next").click()
            await page.get_by_role("textbox", name="Type").fill("VENDOR INVOICE")
            await page.get_by_role("button", name="Next").click()
            await page.get_by_role("button", name="Save").click()
            print(f"Attached Invoice: {invoice}")

        else:
            print(f"No matching file found for invoice: {invoice}")

    print("Done!")



    # ---------------------
    # await context.close()
    # await browser.close()


async def main() -> None:
    async with async_playwright() as playwright:
        await authenticate(playwright)
        await attach(playwright)




# await page.goto("https://washingtontest.assetworks.hosting/fmax/screen/WORKDESK")

#if page is redirected to "https://idp.u.washington.edu/idp/profile/SAML2/Redirect/SSO?execution=e1s1"

asyncio.run(main())
