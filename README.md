1.  Invoice-Retriever
    - Copy attachments to ./pdf-staging/mmddyy
      - Automation Options
        - Using the exising Automate workflow that copies fssacct attachement to OneDrive
          - Pull via a Playwright workflow on Windows Explorer
          - Pull via Automate (subscription?) directly from OneDrive
        - Pull via Exchangelib
    - Remove non-pdf files
2.  File-Renamer
    - Pdf-proc
      - V.1
        - Still requires manual error checking of invoice numbers prior to moving files into ./New
          - Zip
          - Spin up Render
          - Upload
          - Click unzip
          - Click start
          - Wait
          - Click download
          - Unzip
      - V.2
        - Magic
3.  AiM-Data-Retriever
    - aim_data.py
      - Playwright workflow
4.  Invoice-Attacher
    - otto_sync.py
      - Todo
        - Rerun failed attachments once
          -  Move failed pdfs from done/mmddyy/error to the input folder and restart from the top
        - Accomodate
          - Invoice format edge cases
            - '728095/1'
              - WARNING - No matching invoice found in CSV for file: safetyspc 265406ps 728095.pdf
              - ERROR - FAILED: SafetySPC 265406ps 728095.pdf
            - WO Closed error that pops up after clicking SAVE
              - Error Code: 7210 Cannot reopen PO 266034, WO 1131795 Phase 001 is **closed**
          - .msg files to be attached as EMAIL ATTACHMENT
        - Error Handling
          - The print statement in otto_sync.py uses uninitialized variables transaction_id and invoice_num inside the loop before they are assigned.
          - Add a try/except block around your directory creation logic to catch permissions errors or disconnections.
        - Reliability
          - The current matching logic (inv.lower() in file_name) might cause false positives if one invoice number is a substring of another.


##### Test CC commits
- Build out the playwright steps for aim_data.py then run that shit.
- Done: Move the CSV loading logic into main.py to keep otto_sync.py focused purely on browser interaction.
- Done: os replaced by pathlib

```
./logs/
main.py
otto_sync.py
browse.csv
```


Playwright browser recording                                                                                                               

```
playwright codegen https://washington.assetworks.hosting/fmax/screen/WORKDESK 
```
It opens a browser, records your actions, and outputs Playwright code in real time. You can then paste the relevant steps into fetch_browse_csv() in aim_data.py.

"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\Users\spr\pyStuff\playwright\chrome_test"

playwright codegen http://localhost:9222 https://washington.assetworks.hosting/fmax/screen/WORKDESK


playwright codegen --user-data-dir="C:\Users\spr\pyStuff\playwright\chrome_test" https://washington.assetworks.hosting/fmax/screen/WORKDESK


```
# old
  page.get_by_role("link", name="Accounts Payable ~ Purchase Order Invoice ~ All Released Today").click()
  with page.expect_download() as download_info:
      page.get_by_role("link", name="Export").click()
  download = download_info.value


# new
  page.get_by_role("link", name="Accounts Payable ~ Purchase Order Invoice ~ All Released Today").click()
      
  # Wait for the download to start
  with page.expect_download() as download_info:
      page.get_by_role("link", name="Export").click()

  # Grab the download object
  download = download_info.value

  # Save it to your specific directory
  # Note the 'r' before the string to handle Windows backslashes properly
  download.save_as(r"c:\users\spr\pystuff\playwright\browse.csv")
```