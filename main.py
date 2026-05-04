import logging
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
    bundled_dir = exe_dir / "playwright" / "driver" / "package" / ".local-browsers"

    if any(bundled_dir.glob("chromium-*")):
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(bundled_dir)
        return

    fallback_dir = exe_dir / "browsers"
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(fallback_dir)

    if not any(fallback_dir.glob("chromium-*")):
        print("Chromium not found. Downloading (requires internet)...")
        fallback_dir.mkdir(parents=True, exist_ok=True)
        node = exe_dir / "playwright" / "driver" / "node.exe"
        cli = exe_dir / "playwright" / "driver" / "package" / "cli.js"
        result = subprocess.run([str(node), str(cli), "install", "chromium"], env=os.environ.copy())
        if result.returncode != 0:
            raise RuntimeError("Chromium install failed — check internet connection.")


DATE_STR = datetime.now().strftime("%m%d%y")
SOURCE_DIR = Path("I:/groups/fac2/fabs/stores/FSSAP/Done/otto_sync_test")
DESTINATION_DIR = SOURCE_DIR / DATE_STR
LOG_DIR = Path("./logs")
BASE_URL = "https://washington.assetworks.hosting"


def setup_environment():
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    DESTINATION_DIR.mkdir(parents=True, exist_ok=True)


def pull_released(folder_path=SOURCE_DIR):
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
                    shutil.copy2(file, DESTINATION_DIR / file.name)
                    print(f"SUCCESS: {file.name}")
                elif result == "partial":
                    partial_count += 1
                    shutil.copy2(file, DESTINATION_DIR / file.name)
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
    for file in source_dir.iterdir():
        if not file.is_file():
            continue

        if (DESTINATION_DIR / file.name).exists():
            try:
                file.unlink()
            except Exception as e:
                print(f"Failed to delete {file.name}: {e}")


if __name__ == "__main__":
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"otto_run_{datetime.now().strftime('%m%d%y_%H%M%S')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(log_path)],
    )

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

    finally:
        if csv_path and csv_path.exists():
            csv_path.unlink()
        for handler in logging.getLogger().handlers:
            handler.flush()
        if DESTINATION_DIR.exists():
            try:
                shutil.copy2(log_path, DESTINATION_DIR / log_path.name)
            except Exception:
                pass

    input("\nPress Enter to exit...")
