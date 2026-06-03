import os
import sys
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any

# Ensure parent directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.indexer import SchemeIndexer

URLS = [
    "https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth",
    "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    "https://groww.in/mutual-funds/hdfc-nifty-50-index-fund-direct-growth"
]

def get_hash(data: Any) -> str:
    """Generates a stable SHA256 hex digest for a JSON-serializable structure."""
    serialized = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

def run_sync() -> bool:
    """Synchronizes mutual fund data.
    
    Returns:
        bool: True if changes were detected and processed, False otherwise.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    schemes_json_path = os.path.join(data_dir, "schemes.json")
    last_sync_path = os.path.join(data_dir, "last_sync.json")
    
    indexer = SchemeIndexer()
    
    # 1. Scrape latest data from target URLs
    print("Initiating Groww scraping for the 5 target mutual fund schemes...")
    new_schemes = []
    for url in URLS:
        try:
            print(f"Scraping: {url}")
            data = indexer.scraper.scrape(url)
            new_schemes.append(data)
        except Exception as e:
            print(f"CRITICAL: Failed scraping {url}: {e}")
            print("Aborting synchronization to prevent corrupt database state.")
            return False
            
    new_hash = get_hash(new_schemes)
    
    # 2. Check for differences against existing schemes file
    has_changes = True
    if os.path.exists(schemes_json_path):
        try:
            with open(schemes_json_path, "r", encoding="utf-8") as f:
                old_schemes = json.load(f)
            old_hash = get_hash(old_schemes)
            if old_hash == new_hash:
                has_changes = False
                print("Synchronization check complete: No changes detected in source data.")
        except Exception as e:
            print(f"WARNING: Error parsing existing schemes.json: {e}. Forcing re-index.")
            
    # 3. Process changes or generate sync files if missing
    sync_date = datetime.now().strftime("%d-%b-%Y")
    
    if has_changes:
        print("Changes detected. Rebuilding files and database index...")
        # Save fresh schemes data
        with open(schemes_json_path, "w", encoding="utf-8") as f:
            json.dump(new_schemes, f, indent=2, ensure_ascii=False)
            
        # Re-index collection inside ChromaDB
        indexer.index_from_file(schemes_json_path)
        
        # Write/Update last_sync.json metadata
        sync_meta = {
            "last_sync": sync_date,
            "checksum": new_hash
        }
        with open(last_sync_path, "w", encoding="utf-8") as f:
            json.dump(sync_meta, f, indent=2)
            
        print(f"Database rebuilt successfully. Central sync date set to: {sync_date}.")
        return True
    else:
        # If files match but last_sync.json metadata is missing, write it out
        if not os.path.exists(last_sync_path):
            sync_meta = {
                "last_sync": sync_date,
                "checksum": new_hash
            }
            with open(last_sync_path, "w", encoding="utf-8") as f:
                json.dump(sync_meta, f, indent=2)
            print(f"Initialized missing last_sync.json config file with date: {sync_date}.")
        else:
            print("No action required. Database is fully up-to-date.")
        return False

if __name__ == "__main__":
    run_sync()
