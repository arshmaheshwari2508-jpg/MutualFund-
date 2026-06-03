import unittest
import os
import sys
import json

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.scraper import GrowwScraper
from src.database import MutualFundsDB
from src.indexer import SchemeIndexer

class TestPhase1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.urls = [
            "https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth",
            "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
            "https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth",
            "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
            "https://groww.in/mutual-funds/hdfc-nifty-50-index-fund-direct-growth"
        ]
        # Initialize indexer using a test database path
        cls.test_dir = os.path.dirname(os.path.abspath(__file__))
        cls.test_db_path = os.path.join(cls.test_dir, "test_db")
        cls.test_json_path = os.path.join(cls.test_dir, "test_schemes.json")
        
        cls.db = MutualFundsDB(db_path=cls.test_db_path)
        cls.indexer = SchemeIndexer(db=cls.db)

    def test_1_scraper_and_json_file(self):
        """Test scraping and saving to a local JSON data file."""
        # Clean old file if exists
        if os.path.exists(self.test_json_path):
            os.remove(self.test_json_path)
            
        # Run scraper and verify file creation
        self.indexer.scraper.scrape_and_save_to_json(self.urls, self.test_json_path)
        self.assertTrue(os.path.exists(self.test_json_path), "JSON data file was not generated.")

        # Load file and assert layout structure
        with open(self.test_json_path, "r", encoding="utf-8") as f:
            schemes = json.load(f)
            
        self.assertEqual(len(schemes), 5, "Expected 5 scraped schemes in the JSON file.")
        
        # Verify a scheme has necessary keys
        hdfc_defence = next((s for s in schemes if "Defence" in s["scheme_name"]), None)
        self.assertIsNotNone(hdfc_defence, "HDFC Defence Fund was not found in the scraped data.")
        self.assertEqual(hdfc_defence["fund_house"], "HDFC Mutual Fund")
        self.assertIsNotNone(hdfc_defence["expense_ratio"])
        self.assertIsNotNone(hdfc_defence["exit_load"])
        self.assertGreater(len(hdfc_defence["managers"]), 0)

    def test_2_indexing_from_file(self):
        """Test indexing from the generated local JSON file into the database."""
        # Make sure the file exists from test 1
        self.assertTrue(os.path.exists(self.test_json_path), "Run test_1 first to generate test_schemes.json")
        
        # Index collection using the file path
        self.indexer.index_from_file(self.test_json_path)
        
        # Verify collection contents
        collection = self.db.get_collection()
        results = collection.get()
        
        self.assertGreater(len(results["ids"]), 0)
        # Should have at least 15 chunks (5 schemes * (1 overview + 1 manager + 1 documents))
        self.assertGreaterEqual(len(results["ids"]), 15)
        
        # Test semantic query retrieval
        query_results = collection.query(
            query_texts=["Who manages the HDFC Defence Fund?"],
            n_results=2
        )
        
        # Ensure we got results
        self.assertGreater(len(query_results["documents"][0]), 0)
        
        # Check that retrieved content contains relevant manager info
        found_manager_context = False
        for doc in query_results["documents"][0]:
            if "manager" in doc.lower() or "dhruv" in doc.lower() or "priya" in doc.lower():
                found_manager_context = True
                break
        self.assertTrue(found_manager_context, "Manager query failed to retrieve manager information.")

    @classmethod
    def tearDownClass(cls):
        # Clean up test output file
        if os.path.exists(cls.test_json_path):
            os.remove(cls.test_json_path)
        # We can leave the ChromaDB folders or clean them up. Clean them up to be tidy.
        import shutil
        if os.path.exists(cls.test_db_path):
            shutil.rmtree(cls.test_db_path)
            
if __name__ == "__main__":
    unittest.main()
