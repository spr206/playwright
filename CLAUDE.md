# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
Keep responses brief to answers only and list recommendations or next steps.  Don't proceed with them until asked.


## What this project does

This is a Playwright-based automation tool that attaches vendor invoice PDFs and .msg files to purchase order records in a UW AiM (AssetWorks) web application. It launches its own Chromium instance using a persistent profile to preserve UW SSO authentication across runs. It is designed to be compiled to a standalone Windows executable via Nuitka.

## Running the tool

**Prerequisites:**
- PDF/MSG files to attach must be placed in `I:/groups/fac2/fabs/stores/FSSAP/Done/otto_sync_test/`
- A valid UW SSO session must exist in the Chromium persistent profile (first run will prompt for login)

**Run:**
```bash
python main.py
```

Or run the compiled `otto.exe` directly. The tool auto-fetches today's released PO invoice list from AiM at startup — no manual `browse.csv` needed.

Logs are written to `./logs/otto_run_<timestamp>.log`.

## Architecture

- **`main.py`** — Orchestrator. Detects Nuitka compiled context and sets `PLAYWRIGHT_BROWSERS_PATH` accordingly (`setup_playwright()`). Calls `fetch_browse_csv()` / `load_transactions()` to get today's transactions, then runs the batch via `OttoSync`. Deletes the temp CSV in `finally`. Calls `error_check()` to clean up source files after processing.
- **`aim_data.py`** — Fetches today's PO invoice CSV from AiM. `fetch_browse_csv()` navigates to the WORKDESK, clicks "Accounts Payable ~ Purchase Order Invoice ~ All Released Today", exports the CSV, and saves it to a temp file. `load_transactions()` reads that CSV into a `transaction_id → invoice_num` dict.
- **`otto_sync.py`** — `OttoSync` class (context manager). Launches Chromium via `launch_persistent_context` using `CHROME_PROFILE_DIR` (location differs between compiled and dev modes). For each file: runs two-pass matching against the transaction dict, navigates to the AiM invoice URL, and drives the Related Documents upload wizard. Sets doc type to `"EMAIL ATTACHMENT"` for `.msg` files and `"VENDOR INVOICE"` for PDFs. Returns `"exact"`, `"partial"`, or `False`.
- **`.ignore/working_test_otto_async.py`** — Legacy async prototype (not used). Kept for reference.

## Key file matching logic

`otto_sync.py` uses two passes:
1. **Exact**: `inv.lower() in file_name` — invoice number as a direct substring of the filename.
2. **Partial**: strips non-alphanumeric characters from the invoice number, then checks for that cleaned string in the filename. Picks the longest match.

False positives are still possible if one invoice number is a substring of another.

## Nuitka deployment

Nuitka is a dev dependency (`pyproject.toml`). When compiled, `__compiled__` is defined at runtime. `setup_playwright()` in `main.py` checks for this and sets `PLAYWRIGHT_BROWSERS_PATH` to the bundled Chromium inside the exe directory, or downloads Chromium to a `browsers/` fallback folder if not found. `CHROME_PROFILE_DIR` in `otto_sync.py` is similarly set to a path relative to the exe when compiled.

## Input/output structure

```
I:/.../otto_sync_test/            # SOURCE_DIR — input PDFs/MSGs
I:/.../otto_sync_test/MMDDYY/
  processed/                      # Successfully attached files copied here
./logs/                           # Local run logs
```

## Known issues

- Invoice edge cases like `728095/1` won't match correctly (slash stripped in partial pass, but exact pass fails)
- Substring matching can cause false positives
- `error_check()` deletes source files once they appear in `processed/` — failed files are left in source but not automatically retried
