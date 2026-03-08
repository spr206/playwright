# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
Keep responses brief to answers only and list recommendations or next steps.  Don't proceed with them until asked.


## What this project does

This is a Playwright-based automation tool that attaches vendor invoice PDFs (and .msg files) to purchase order records in a UW AiM (AssetWorks) web application. It connects to an already-open Chrome browser via CDP rather than launching its own browser, which is how it handles UW SSO authentication.

## Running the tool

**Prerequisites:**
- Chrome must be running with remote debugging enabled:
  ```
  chrome.exe --remote-debugging-port=9222
  ```
- `browse.csv` must exist in the project root (columns: Transaction ID, Invoice Number)
- PDF/MSG files to attach must be placed in `I:/groups/fac2/fabs/stores/FSSAP/Done/otto_sync_test/`

**Run:**
```bash
python main.py
```

Logs are written to `./logs/otto_run_<timestamp>.log`.

## Architecture

- **`main.py`** — Orchestrator. Handles directory setup, file discovery, logging init, and post-run cleanup. Calls `OttoSync` in a `with` block so the browser opens once for the entire batch.
- **`otto_sync.py`** — `OttoSync` class (context manager). Connects to Chrome via CDP, reads `browse.csv` into a `trans_dict` mapping `transaction_id → invoice_num`, then for each file: matches filename against invoice numbers, navigates to the AiM invoice URL, and drives the Related Documents upload wizard.
- **`.ignore/working_test_otto_async.py`** — Legacy async prototype (not used). Kept for reference.

## Key file matching logic

`otto_sync.py` matches files by checking `inv.lower() in file_name` — the invoice number must appear as a substring of the PDF filename. This can produce false positives if one invoice number is a substring of another (noted as a known issue in README.md).

## Input/output structure

```
browse.csv                        # Transaction ID, Invoice Number (no header expected after skip)
I:/.../otto_sync_test/            # SOURCE_DIR — input PDFs/MSGs
I:/.../otto_sync_test/MMDDYY/
  processed/                      # Successfully attached files copied here
  error/                          # Failed files copied here
./logs/                           # Local run logs
```

## Known issues (from README.md)

- Invoice edge cases like `728095/1` won't match correctly
- `.msg` files are not yet collected.  Code needs to be modified so that .msg files are treated the same way as .pdf but instead of 'SUPPLIER INVOICE' text should read 'EMAIL ATTACHMENT'.
- Substring matching can cause false positives
- `error_check()` deletes source files once they appear in processed/ or error/ — it does not retry failures.  It should retry each failed one more time.