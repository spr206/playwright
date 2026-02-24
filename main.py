# Notes for your Environment:
# CrowdStrike Tip: If the script gets blocked, it’s usually because of "Suspicious Process Tree" (Python spawning Outlook). You might need to ask your IT team to whitelist the specific folder where you keep this script.

# Outlook State: This script requires Outlook to be open (or at least the profile to be initialized). Since you're running this while logged in, that shouldn't be an issue.

# Would you like me to help you refine the pull_released() logic so it only picks up specific filenames or looks in a certain network drive?


import shutil
import logging
import sys
import win32com.client as win32
from pathlib import Path
from datetime import datetime

from otto_sync import OttoSync

# --- CONFIGURATION ---
TARGET_EMAIL = "fssacct@uw.com"
DATE_STR = datetime.now().strftime("%m%d%y")
BASE_DIR = Path(f"done/{DATE_STR}")
LOG_FILE = BASE_DIR / f"{DATE_STR}.log"

def setup_environment():
    """Ensure directories exist and logging is ready."""
    (BASE_DIR / "processed").mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "error").mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s'
    )

def email_log(error_msg=None):
    """Sends log via Outlook. If error_msg is provided, sends as a failure alert."""
    try:
        outlook = win32.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)
        mail.To = TARGET_EMAIL
        
        if error_msg:
            mail.Subject = f"CRITICAL FAILURE: Otto Sync - {DATE_STR}"
            status_text = f"<p style='color:red;'><b>The script crashed during execution:</b><br>{error_msg}</p>"
        else:
            mail.Subject = f"Otto Sync Report - {DATE_STR}"
            status_text = "<p>The daily sync completed successfully. See attached log for details.</p>"

        mail.HTMLBody = f"""
        <h3>Otto Sync System: {DATE_STR}</h3>
        {status_text}
        <hr>
        <p><small>Automated notification from workstation: {Path.home().name}</small></p>
        """

        if LOG_FILE.exists():
            mail.Attachments.Add(str(LOG_FILE.absolute()))
        
        mail.Send()
        print("Notification sent via Outlook.")
    except Exception as e:
        # If Outlook is blocked by CrowdStrike or closed, we log to console as last resort
        print(f"Failed to send Outlook notification: {e}")

def pull_released():
    """Mock for your file discovery logic."""
    # Assuming files are in the current working directory for this example
    return list(Path(".").glob("*.pdf")) + list(Path(".").glob("*.msg"))

def run_otto():
    logging.info("--- Starting Otto Sync Session ---")
    files = pull_released()
    
    if not files:
        logging.info("No files found.")
        return

    # Use the context manager to open the browser ONCE
    try:
        with OttoSync() as otto:
            for file in files:
                if file.suffix.lower() not in ['.pdf', '.msg']:
                    continue
                
                logging.info(f"Syncing: {file.name}")
                
                # Call the method from the imported class
                success = otto.process_file(file)
                
                if success:
                    dest = BASE_DIR / "processed" / file.name
                    shutil.copy2(file, dest)
                    logging.info(f"SUCCESS: {file.name}")
                else:
                    dest = BASE_DIR / "error" / file.name
                    shutil.copy2(file, dest)
                    logging.error(f"FAILED: {file.name}")
                    
    except Exception as e:
        logging.critical(f"Failed to initialize Playwright: {e}")
        raise # Pass to the main error handler for the email log

def error_check():
    """Cleans up local files if copies exist in processed/error."""
    processed_dir = BASE_DIR / "processed"
    error_dir = BASE_DIR / "error"
    
    # Check root directory for files that were successfully moved
    for file in Path(".").iterdir():
        if not file.is_file(): continue
        
        in_processed = (processed_dir / file.name).exists()
        in_error = (error_dir / file.name).exists()
        
        if in_processed or in_error:
            file.unlink()
            logging.info(f"CLEANUP: Deleted local source file {file.name}")

if __name__ == "__main__":
    setup_environment()
    try:
        run_otto()
        error_check()
        email_log() # Send success email
    except Exception as e:
        error_detail = f"Unexpected Error: {str(e)}"
        logging.critical(error_detail)
        email_log(error_msg=error_detail) # Send crash email
        sys.exit(1)