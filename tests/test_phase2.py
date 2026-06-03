import unittest
import os
import sys
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import MutualFundsDB
from src.llm import GeminiClient
from src.rag import RAGOrchestrator

class TestPhase2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db")
        cls.db = MutualFundsDB(db_path=test_db_path)
        
        # Initialize mock client and orchestrator
        cls.mock_llm = GeminiClient()
        cls.orchestrator = RAGOrchestrator(db=cls.db, llm=cls.mock_llm)
        cls.sync_date = "03-Jun-2026"

    def test_1_competitor_blocking(self):
        """Test that non-HDFC queries are immediately blocked without hitting Vector DB."""
        queries = [
            "What is the expense ratio of SBI Small Cap Fund?",
            "Should I invest in ICICI Prudential Technology?",
            "Compare Kotak Gold Fund and Axis Small Cap."
        ]
        for q in queries:
            response = self.orchestrator.query(q)
            self.assertIn("only contain facts about HDFC", response)
            self.assertNotIn("Mocked", response)

    def test_2_scheme_pre_routing(self):
        """Test target scheme parsing mapping logic."""
        scheme, url = self.orchestrator.match_target_scheme("What are the managers for HDFC Defence Fund?")
        self.assertEqual(scheme, "HDFC Defence Fund Direct Growth")
        self.assertIn("hdfc-defence-fund", url)

        scheme, url = self.orchestrator.match_target_scheme("expense ratio of silver")
        self.assertEqual(scheme, "HDFC Silver ETF FoF Direct Growth")
        
        scheme, url = self.orchestrator.match_target_scheme("lumpsum amount of HDFC Nifty 50")
        self.assertEqual(scheme, "HDFC Nifty 50 Index Fund Direct Growth")

    def test_3_sentence_splitting(self):
        """Test internal sentence parser boundaries."""
        text = "This is sentence one. This is sentence two! Is this sentence three? Yes."
        sentences = self.orchestrator.split_sentences(text)
        self.assertEqual(len(sentences), 4)
        self.assertEqual(sentences[0], "This is sentence one.")
        self.assertEqual(sentences[2], "Is this sentence three?")

    def test_4_compliance_formatter(self):
        """Test formatting wrapper constraints for sentence counts, links, and footers."""
        sync_date = "03-Jun-2026"
        url = "https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth"

        # Case A: Too long (5 sentences) and missing citation link
        long_input = (
            "HDFC Defence Fund has an expense ratio of 0.82%. It has a very high riskmeter rating. "
            "The exit load is 1% if redeemed within a year. It was launched in June 2023. "
            "Priya Ranjan is the designated fund manager."
        )
        output = self.orchestrator.enforce_formatting_compliance(long_input, url, sync_date)
        
        # Verify sentence count (excluding citation and footer lines)
        lines = output.strip().split("\n")
        answer_text = lines[0]
        sentences = self.orchestrator.split_sentences(answer_text)
        self.assertEqual(len(sentences), 3) # Programmatically sliced to 3
        self.assertTrue(answer_text.startswith("HDFC Defence Fund"))
        self.assertTrue(answer_text.endswith("redeemed within a year."))
        
        # Verify exactly one citation line
        self.assertIn(f"Source: [Groww Mutual Fund Link]({url})", output)
        self.assertIn(f"Last updated from sources: {sync_date}", output)

        # Case B: Correct length but LLM returned markdown link inside
        correct_input = (
            "HDFC Defence Fund NAV is 28.44. "
            "Source: [HDFC Defence Fund](https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth)\n"
            "Last updated from sources: 03-Jun-2026"
        )
        output = self.orchestrator.enforce_formatting_compliance(correct_input, url, sync_date)
        lines = output.strip().split("\n")
        
        self.assertEqual(len(self.orchestrator.split_sentences(lines[0])), 1)
        self.assertIn("[HDFC Defence Fund](https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth)", output)
        self.assertIn(f"Last updated from sources: {sync_date}", output)

    @patch("src.llm.GeminiClient.generate_facts_answer")
    def test_5_orchestrator_query_mocked(self, mock_generate):
        """Test RAG query end-to-end execution utilizing mocked LLM outputs."""
        mock_generate.return_value = (
            "HDFC Defence Fund has an assets under management of 9123 Crores. "
            "The fund manager is Dhruv Muchhal.\n"
            "Source: [HDFC Defence](https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth)\n"
            "Last updated from sources: 03-Jun-2026"
        )
        
        response = self.orchestrator.query("Who is managing HDFC Defence?")
        self.assertIn("9123 Crores", response)
        self.assertIn("Dhruv Muchhal", response)
        self.assertIn("Source: [HDFC Defence]", response)
        self.assertTrue(response.endswith("Last updated from sources: 03-Jun-2026"))
        
        # Verify sentence count in answer line
        lines = response.strip().split("\n")
        self.assertEqual(len(self.orchestrator.split_sentences(lines[0])), 2)

if __name__ == "__main__":
    unittest.main()
