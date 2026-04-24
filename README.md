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
main.py
aim_data.py
otto_sync.py
```
Playwright recorder
```
playwright codegen --user-data-dir="C:\ChromeDebugProfile" http://targeturl.com/url
```

uv run python -m nuitka --standalone --mingw64 --playwright-include-browser=chromium-1208 main.py

uv run python -m nuitka --clean-cache=all


uv run python -m nuitka --onefile --mingw64 --playwright-include-browser=chromium-1208 main.py


python -m nuitka --standalone ^
  --include-data-dir=.venv\Lib\site-packages\playwright\driver=playwright\driver ^
  main.py



C:\Users\spr\pyStuff\playwright>uv run python -m nuitka --onefile --mingw64 --playwright-include-browser=chromium-1208 main.py
Nuitka-Options: Used command line options:
Nuitka-Options:   --onefile --mingw64 --playwright-include-browser=chromium-1208 main.py
Nuitka: Starting Python compilation with:
Nuitka:   Version '4.0.8' on Python 3.12 (flavor 'CPython Official') commercial grade 'not installed'.
Nuitka-Onefile:WARNING: Onefile mode cannot compress without 'zstandard' package installed You probably should depend on
Nuitka-Onefile:WARNING: 'Nuitka[onefile]' rather than 'Nuitka' which among other things depends on it.
Nuitka-Plugins:playwright: Including browsers: chromium-1208
Nuitka-Plugins:playwright: Including 'ffmpeg' for chromium-based browser. It is required by playwright.
Nuitka-Plugins:playwright: Including 'chromium-1208' from 'C:\Users\spr\AppData\Local\ms-playwright\chromium-1208'.
Nuitka-Plugins:playwright: Including 'ffmpeg-1011' from 'C:\Users\spr\AppData\Local\ms-playwright\ffmpeg-1011'.
Nuitka-Plugins:dll-files: Found 1 file DLLs from playwright installation.
Nuitka-Inclusion:WARNING: The following Visual C++ Redistributable DLLs were not found: msvcp140.dll. For a fully
Nuitka-Inclusion:WARNING: portable standalone distribution, these DLLs must be available either by installing the
Nuitka-Inclusion:WARNING: Microsoft Visual C++ Redistributable for Visual Studio 2015-2022 on the target system or by
Nuitka-Inclusion:WARNING: bundling them with the application. To bundle them, Visual Studio must be installed on the
Nuitka-Inclusion:WARNING: build machine.
Nuitka: Completed Python level compilation and optimization.
Nuitka: Generating source code for C backend compiler.
Nuitka: Running data composer tool for optimal constant value handling.
Nuitka: Running C compilation via Scons.
Nuitka-Scons: Backend C compiler: gcc (gcc 14.2.0).
Nuitka-Scons: Backend C linking with 67 files (no progress information available for this stage).
Nuitka-Scons: Compiled 67 C files using ccache.
Nuitka-Scons: Cached C files (using ccache) with result 'cache miss': 67
Nuitka-Plugins:data-files: Included 337 data files due to package data for 'playwright'.
Nuitka-Plugins:playwright: Included 310 data files due to Playwright browser 'chromium-1208'.
Nuitka-Plugins:playwright: Included data file 'playwright\driver\package\.local-browsers\ffmpeg-1011\COPYING.LGPLv2.1'
Nuitka-Plugins:playwright: due to Playwright browser 'ffmpeg-1011'.
Nuitka-Plugins:playwright: Included data file
Nuitka-Plugins:playwright: 'playwright\driver\package\.local-browsers\ffmpeg-1011\DEPENDENCIES_VALIDATED' due to
Nuitka-Plugins:playwright: Playwright browser 'ffmpeg-1011'.
Nuitka-Plugins:playwright: Included data file
Nuitka-Plugins:playwright: 'playwright\driver\package\.local-browsers\ffmpeg-1011\INSTALLATION_COMPLETE' due to
Nuitka-Plugins:playwright: Playwright browser 'ffmpeg-1011'.
Nuitka-Plugins:playwright: Included data file 'playwright\driver\package\.local-browsers\ffmpeg-1011\ffmpeg-win64.exe'
Nuitka-Plugins:playwright: due to Playwright browser 'ffmpeg-1011'.
Nuitka-Onefile: Creating single file from dist folder, this may take a while.
Nuitka-Onefile: Running bootstrap binary compilation via Scons.
Nuitka-Onefile:WARNING: Onefile mode cannot compress without 'zstandard' package installed You probably should depend on
Nuitka-Onefile:WARNING: 'Nuitka[onefile]' rather than 'Nuitka' which among other things depends on it.
Nuitka-Inclusion:WARNING: Cannot find Windows Runtime DLLs to include, requiring them to be installed on target systems.
Nuitka-Scons: Onefile C compiler: gcc (gcc 14.2.0).
Nuitka-Scons: Onefile C linking.
Nuitka-Scons: Compiled 1 C files using ccache.
Nuitka-Scons: Cached C files (using ccache) with result 'cache miss': 1
Nuitka-Onefile: Keeping onefile build directory 'main.onefile-build'.
Nuitka: Keeping dist folder 'main.dist' for inspection, no need to use it.
Nuitka: Keeping build directory 'main.build'.
Nuitka: Successfully created '~\pyStuff\playwright\main.exe'.



Detected: Trojan.Win32/Wacatac.B!ml
Status: Quarantined
Quarantined files are in a restricted area where they can't harm your device.
They will be removed automatically.
Date: 4/19/2026 9:41 PM
Details: This program is dangerous and executes commands from an
attacker.
Affected items:
file: C:\Users\spr\AppData\Local\Temp\onefile_43332_134211336450645729\main.dll