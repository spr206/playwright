import shutil
import logging
import sys
import os
from pathlib import Path
from datetime import datetime

from otto_sync import OttoSync

# --- CONFIGURATION ---
DATE_STR = datetime.now().strftime("%m%d%y")
BASE_DIR = Path(f"done/{DATE_STR}")

def setup_local_logging():
    """Creates the log directory and configures logging to a timestamped file."""
    # 1. Ensure the ./logs directory exists
    os.makedirs("./logs", exist_ok=True)
    
    # 2. Generate a timestamp (e.g., 2026-02-25_09-30-00)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = f"./logs/otto_run_{timestamp}.log"
    
    # 3. Configure the logging module to write to this file
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO, # Change to DEBUG if you need more details
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    return log_file

def setup_environment():
    """Ensure output directories exist."""
    (BASE_DIR / "processed").mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "error").mkdir(parents=True, exist_ok=True)

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
        raise # Pass to the main error handler

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
    
    # Initialize logging once right at the start
    current_log_file = setup_local_logging()
    logging.info(f"Starting execution. Logging to {current_log_file}")
    
    try:
        run_otto()
        error_check()
        logging.info("Run completed successfully.")
    except Exception as e:
        error_detail = f"Unexpected Error: {str(e)}"
        logging.critical(error_detail)
        sys.exit(1)