1.  Invoice-Retriever
    -set ignore rules
    -'uwconnect\*'
    - Copy attachments to ./pdf-staging/mmddyy
      - Automation Options
        - Pull via Exchangelib
        - Using the exising Automate workflow that copies fssacct attachement to OneDrive
          - Pull via a Playwright workflow on Windows Explorer
          - Pull via Automate (subscription?) directly from OneDrive
    - File handling
      - Send to File-Renamer
        - pdf
      - Send directly to New\
        - xls\*?
      - Ignore
        - All other file types
          - no_extension,eml,htm\*,mhtml,mp3,wav,p7m,pages,jpg,jpeg,gif,png,rtf,tiff,txt,xml,zip
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
          - fastapi
          - sqlite?
          - redis
        - no zipping
        - accomodate statements
        - ui for editing normalized Co names
        - log to ui
3.  AiM-Data-Retriever
    - aim_data.py
4.  Invoice-Attacher
    - otto_sync.py
      - Todo
        - Rerun failed attachments once
          - Move failed pdfs from done/mmddyy/error to the input folder and restart from the top
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
          - Add a try/except block around directory creation logic to catch permissions errors or disconnections.
        - Reliability
          - The current matching logic (inv.lower() in file_name) might cause false positives if one invoice number is a substring of another.

```
logs/
main.py
aim_data.py
  browse.csv
otto_sync.py
```

Playwright recorder

```
playwright codegen --user-data-dir="C:\ChromeDebugProfile" http://targeturl.com/url
```


python -m nuitka --standalone ^
  --include-data-dir=.venv\Lib\site-packages\playwright\driver=playwright\driver ^
  main.py


  - Utilize the existing open browser session from the csv grab for the batch
  - Keep cli open after batch completion
  - Don't list 'deleted....' during cleanup
  - Refine the CLI output
  - Place session log in Done\logs
  - Place finished pdfs into mmddyy instead of mmddyy\processed
