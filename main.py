import shutil
import logging
import sys
from pathlib import Path
from datetime import datetime

from otto_sync import OttoSync
from aim_data import fetch_browse_csv, load_transactions


# --- CONFIGURATION ---
TEST_MODE = False  # Set True to use test server + .ignore/test_files/

DATE_STR = datetime.now().strftime("%m%d%y")
SOURCE_DIR = Path(".ignore/test_files") if TEST_MODE else Path("I:/groups/fac2/fabs/stores/FSSAP/Done/otto_sync_test")
DESTINATION_DIR = SOURCE_DIR / DATE_STR
BASE_URL = "https://washingtontest.assetworks.hosting" if TEST_MODE else "https://washington.assetworks.hosting"
CSV_FILE = Path(".ignore/test_files/browse.csv") if TEST_MODE else Path("browse.csv")


def setup_local_logging():
    """Creates the log directory and configures logging to a timestamped file."""
    # 1. Ensure the ./logs directory exists
    Path("./logs").mkdir(exist_ok=True)

    # 2. Generate a timestamp (e.g., 2026-02-25_09-30-00)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = f"./logs/otto_run_{timestamp}.log"

    # 3. Configure the logging module to write to this file
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,  # Change to DEBUG if you need more details
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    return log_file


def setup_environment():
    """Ensure source and destination directories exist."""
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    DESTINATION_DIR.mkdir(parents=True, exist_ok=True)


def pull_released(folder_path=SOURCE_DIR):
    """Pulls valid files from the source directory."""
    if not folder_path.exists():
        return []

    # Return a list of Path objects for all PDFs and MSGs
    return [
        f
        for f in folder_path.iterdir()
        if f.is_file() and f.suffix.lower() in [".pdf", ".msg"]
    ]


def run_otto(trans_dict, base_url):
    logging.info("--- Starting Otto Sync Session ---")
    files = pull_released()

    if not files:
        logging.info("No files found.")
        return

    exact_count = 0
    partial_count = 0
    failed_count = 0

    # Use the context manager to open the browser ONCE
    try:
        with OttoSync(trans_dict, base_url) as otto:
            for file in files:
                if file.suffix.lower() not in [".pdf", ".msg"]:
                    continue

                logging.info(f"Syncing: {file.name}")

                result = otto.process_file(file)

                if result == "exact":
                    exact_count += 1
                    dest = DESTINATION_DIR / file.name
                    shutil.copy2(file, dest)
                    logging.info(f"SUCCESS: {file.name}")
                elif result == "partial":
                    partial_count += 1
                    dest = DESTINATION_DIR / file.name
                    shutil.copy2(file, dest)
                    logging.info(f"SUCCESS (partial match): {file.name}")
                else:
                    failed_count += 1
                    logging.error(f"FAILED: {file.name} — left in source for retry")

        summary = (
            f"\n--- Batch Complete ---\n"
            f"  Exact matches:   {exact_count}\n"
            f"  Partial matches: {partial_count}\n"
            f"  Unsuccessful:    {failed_count}\n"
        )
        print(summary)
        logging.info(summary)

    except Exception as e:
        logging.critical(f"Failed to initialize Playwright: {e}")
        raise  # Pass to the main error handler


def error_check(source_dir=SOURCE_DIR):
    """Cleans up local files if copies exist in destination/error."""
    for file in source_dir.iterdir():
        if not file.is_file():
            continue

        in_processed = (DESTINATION_DIR / file.name).exists()

        if in_processed:
            try:
                file.unlink()
                logging.info(
                    f"CLEANUP: Deleted local source file {file.name} from {source_dir}")
            except Exception as e:
                logging.error(f"Failed to delete {file.name}: {e}")


if __name__ == "__main__":
    # 1. Initialize logging once right at the start
    current_log_file = setup_local_logging()
    logging.info(f"Starting execution. Logging to {current_log_file}")

    try:
        # 2. Set up environment AFTER logging has started
        setup_environment()

        # 3. Fetch and load transaction data
        if not TEST_MODE:
            fetch_browse_csv()
        trans_dict = load_transactions(CSV_FILE)

        # 4. Run the main logic
        run_otto(trans_dict, BASE_URL)
        error_check()
        logging.info("Run completed successfully.")

    except Exception as e:
        error_detail = f"Unexpected Error: {str(e)}"
        logging.critical(error_detail)
        sys.exit(1)
