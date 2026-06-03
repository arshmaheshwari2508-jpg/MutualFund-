import unittest
import os
import json
from unittest.mock import MagicMock, patch

# Add project root to path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.sync import run_sync, get_hash
from src.database import MutualFundsDB
from src.indexer import SchemeIndexer

class TestPhase4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.data_dir = os.path.join(cls.base_dir, "data")
        cls.schemes_json_path = os.path.join(cls.data_dir, "schemes.json")
        cls.last_sync_path = os.path.join(cls.data_dir, "last_sync.json")
        
        # Backup original files
        cls.backup_schemes = None
        cls.backup_sync = None
        if os.path.exists(cls.schemes_json_path):
            with open(cls.schemes_json_path, "r", encoding="utf-8") as f:
                cls.backup_schemes = f.read()
        if os.path.exists(cls.last_sync_path):
            with open(cls.last_sync_path, "r", encoding="utf-8") as f:
                cls.backup_sync = f.read()

        # Clean environment for testing
        if os.path.exists(cls.schemes_json_path):
            os.remove(cls.schemes_json_path)
        if os.path.exists(cls.last_sync_path):
            os.remove(cls.last_sync_path)

        cls.mock_base = {
            "fund_house": "HDFC Mutual Fund",
            "category": "Equity",
            "sub_category": "Large Cap",
            "risk": "High",
            "min_sip_investment": 500,
            "min_lumpsum_investment": 500,
            "expense_ratio": "0.5%",
            "exit_load": "1%",
            "benchmark_index": "Nifty 50",
            "aum_in_cr": 1000.0,
            "launch_date": "01-Jan-2020",
            "nav": 10.0,
            "nav_date": "03-Jun-2026",
            "managers": [
                {
                    "name": "Test Manager",
                    "education": "MBA",
                    "experience": "10 Years",
                    "funds_managed": ["Test Fund"]
                }
            ]
        }

    @classmethod
    def tearDownClass(cls):
        # Restore backups
        if cls.backup_schemes is not None:
            with open(cls.schemes_json_path, "w", encoding="utf-8") as f:
                f.write(cls.backup_schemes)
        elif os.path.exists(cls.schemes_json_path):
            os.remove(cls.schemes_json_path)
            
        if cls.backup_sync is not None:
            with open(cls.last_sync_path, "w", encoding="utf-8") as f:
                f.write(cls.backup_sync)
        elif os.path.exists(cls.last_sync_path):
            os.remove(cls.last_sync_path)
            
        # Clean up test database path if created
        test_db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_db_p4")
        if os.path.exists(test_db_dir):
            import shutil
            shutil.rmtree(test_db_dir)

    @patch('src.sync.SchemeIndexer')
    @patch('src.scraper.GrowwScraper.scrape')
    def test_sync_pipeline(self, mock_scrape, mock_indexer_class):
        """Test full sync pipeline: initial indexing, skip on match, and update on diff."""
        test_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_db_p4")
        
        # Instantiate SchemeIndexer with a test database
        db = MutualFundsDB(db_path=test_db_path)
        test_indexer = SchemeIndexer(db=db)
        mock_indexer_class.return_value = test_indexer

        # Helper to generate unique mock data per URL
        def get_mock_scheme_1(url):
            suffix = url.split('/')[-1].replace('-', ' ').title()
            return dict(self.mock_base, scheme_name=suffix, source_url=url)

        def get_mock_scheme_2(url):
            suffix = url.split('/')[-1].replace('-', ' ').title()
            # Modify AUM to trigger hash change
            return dict(self.mock_base, scheme_name=suffix, source_url=url, aum_in_cr=1200.0)

        # --- TEST 1: Initial Sync ---
        mock_scrape.side_effect = get_mock_scheme_1
        
        updated = run_sync()
        self.assertTrue(updated, "Initial sync should run indexing.")
        self.assertTrue(os.path.exists(self.schemes_json_path))
        self.assertTrue(os.path.exists(self.last_sync_path))
        
        # Verify database is populated
        collection = db.get_collection()
        self.assertGreater(len(collection.get()["ids"]), 0)
        
        # --- TEST 2: No Changes Sync ---
        # Run sync again with same mock generator
        mock_scrape.side_effect = get_mock_scheme_1
        
        updated = run_sync()
        self.assertFalse(updated, "Sync with identical content should skip indexing.")
        
        # --- TEST 3: Content Changed Sync ---
        # Run sync with modified dataset generator
        mock_scrape.side_effect = get_mock_scheme_2
        
        updated = run_sync()
        self.assertTrue(updated, "Sync with changed content should update database and files.")
        
        # Verify change reflected in json file
        with open(self.schemes_json_path, "r", encoding="utf-8") as f:
            content = json.load(f)
        self.assertEqual(content[0]["aum_in_cr"], 1200.0)

if __name__ == "__main__":
    unittest.main()
