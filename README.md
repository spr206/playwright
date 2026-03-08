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
