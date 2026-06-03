import unittest
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import MutualFundsDB
from src.sanitizer import PIISanitizer
from src.classifier import IntentClassifier
from src.rag import RAGOrchestrator

class TestPhase3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db")
        cls.db = MutualFundsDB(db_path=test_db_path)
        cls.sanitizer = PIISanitizer()
        cls.classifier = IntentClassifier()
        cls.orchestrator = RAGOrchestrator(db=cls.db)

    def test_1_pii_sanitizer(self):
        """Test regex sanitization of PAN, Aadhaar, email, phone, bank numbers, and OTPs."""
        # Email
        clean, flagged = self.sanitizer.sanitize_query("My email is contact@domain.com")
        self.assertTrue(flagged)
        self.assertIn("[REDACTED_EMAIL]", clean)

        # Phone
        clean, flagged = self.sanitizer.sanitize_query("Phone is +91-9999999999")
        self.assertTrue(flagged)
        self.assertIn("[REDACTED_PHONE]", clean)

        # PAN Card
        clean, flagged = self.sanitizer.sanitize_query("My PAN is ABCDE1234F")
        self.assertTrue(flagged)
        self.assertIn("[REDACTED_PAN]", clean)

        # Aadhaar
        clean, flagged = self.sanitizer.sanitize_query("Aadhaar: 1234 5678 9012")
        self.assertTrue(flagged)
        self.assertIn("[REDACTED_AADHAAR]", clean)

        # Bank Card/Account
        clean, flagged = self.sanitizer.sanitize_query("Account: 123456789012345")
        self.assertTrue(flagged)
        self.assertIn("[REDACTED_BANK_DETAIL]", clean)

        # OTP / Passcode
        clean, flagged = self.sanitizer.sanitize_query("My OTP is 482910")
        self.assertTrue(flagged)
        self.assertIn("[REDACTED_OTP]", clean)
        self.assertNotIn("482910", clean)

    def test_2_intent_classifier(self):
        """Test Factual vs Advisory classification rules (using local fallback logic)."""
        factuals = [
            "What is the exit load for HDFC Defence?",
            "Who is the fund manager of HDFC Small Cap?",
            "How can I download the KIM statement for HDFC Gold?"
        ]
        advisories = [
            "Should I invest in HDFC Nifty 50?",
            "Do you recommend HDFC Silver ETF?",
            "Compare HDFC Small Cap and tell me which fund is a better buy."
        ]

        for q in factuals:
            self.assertEqual(self.classifier.classify_intent_local(q), "FACTUAL")

        for q in advisories:
            self.assertEqual(self.classifier.classify_intent_local(q), "ADVISORY")

    def test_3_integrated_pii_blocking(self):
        """Verify that any PII query is blocked in orchestrator pipeline."""
        query = "What is the NAV of HDFC Defence? My phone is 9999999999"
        response = self.orchestrator.query(query)
        self.assertIn("Warning: For your privacy and security", response)

    def test_4_integrated_advisory_refusal(self):
        """Verify that advisory query results trigger Refusal Engine answers and SEBI/AMFI links."""
        query = "Do you suggest that I buy HDFC Small Cap Fund?"
        response = self.orchestrator.query(query)
        self.assertIn("prohibited from providing investment advice", response)
        self.assertIn("AMFI Investor Education", response)
        self.assertIn("SEBI Investor Education", response)

if __name__ == "__main__":
    unittest.main()
