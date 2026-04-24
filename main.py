import os
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime

from otto_sync import OttoSync
from aim_data import fetch_browse_csv, load_transactions


def setup_playwright():
    try:
        __compiled__
    except NameError:
        return

    exe_dir = Path(sys.executable).parent
    browsers_dir = exe_dir / "browsers"
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(browsers_dir)

    if not any(browsers_dir.glob("chromium-*")):
        print("First run: downloading Chromium (requires internet)...")
        driver = exe_dir / "playwright" / "driver" / "playwright.exe"
        result = subprocess.run([str(driver), "install", "chromium"], env=os.environ.copy())
        if result.returncode != 0:
            raise RuntimeError("Chromium install failed — check internet connection.")


DATE_STR = datetime.now().strftime("%m%d%y")
SOURCE_DIR = Path("I:/groups/fac2/fabs/stores/FSSAP/Done/otto_sync_test")
DESTINATION_DIR = SOURCE_DIR / DATE_STR
BASE_URL = "https://washington.assetworks.hosting"


def setup_environment():
    """Ensure source and destination directories exist."""
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    (DESTINATION_DIR / "processed").mkdir(parents=True, exist_ok=True)


def pull_released(folder_path=SOURCE_DIR):
    """Pulls valid files from the source directory."""
    if not folder_path.exists():
        return []

    return [
        f
        for f in folder_path.iterdir()
        if f.is_file() and f.suffix.lower() in [".pdf", ".msg"]
    ]


def run_otto(trans_dict, base_url):
    print("--- Starting Otto Sync Session ---")
    files = pull_released()

    if not files:
        print("No files found.")
        return

    exact_count = 0
    partial_count = 0
    failed_count = 0

    try:
        with OttoSync(trans_dict, base_url) as otto:
            for file in files:
                print(f"Syncing: {file.name}")

                result = otto.process_file(file)

                if result == "exact":
                    exact_count += 1
                    dest = DESTINATION_DIR / "processed" / file.name
                    shutil.copy2(file, dest)
                    print(f"SUCCESS: {file.name}")
                elif result == "partial":
                    partial_count += 1
                    dest = DESTINATION_DIR / "processed" / file.name
                    shutil.copy2(file, dest)
                    print(f"SUCCESS (partial match): {file.name}")
                else:
                    failed_count += 1
                    print(f"FAILED: {file.name} — left in source for retry")

    except Exception as e:
        print(f"Batch error: {e}")
        raise

    finally:
        print(
            f"\n--- Batch Complete ---\n"
            f"  Exact matches:   {exact_count}\n"
            f"  Partial matches: {partial_count}\n"
            f"  Unsuccessful:    {failed_count}\n"
        )


def error_check(source_dir=SOURCE_DIR):
    """Cleans up source files once they appear in processed/."""
    processed_dir = DESTINATION_DIR / "processed"

    for file in source_dir.iterdir():
        if not file.is_file():
            continue

        if (processed_dir / file.name).exists():
            try:
                file.unlink()
                print(f"CLEANUP: Deleted {file.name} from source")
            except Exception as e:
                print(f"Failed to delete {file.name}: {e}")


if __name__ == "__main__":
    csv_path = None
    try:
        setup_playwright()
        setup_environment()
        csv_path = fetch_browse_csv()
        trans_dict = load_transactions(csv_path)
        run_otto(trans_dict, BASE_URL)
        error_check()
        print("Run completed successfully.")

    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        sys.exit(1)

    finally:
        if csv_path and csv_path.exists():
            csv_path.unlink()
