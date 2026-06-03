import os
import google.generativeai as genai
from typing import Optional

class IntentClassifier:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-2.5-flash")

    def classify_intent(self, query: str) -> str:
        """Classifies a user query as FACTUAL or ADVISORY.
        
        Returns 'FACTUAL' or 'ADVISORY' exclusively.
        """
        if not self.api_key:
            # Local keyword fallback for offline testing/mocking
            query_lower = query.lower()
            advisory_keywords = [
                "should i", "better", "recommend", "advice", "suggest", 
                "opinion", "worth investing", "which fund", "compare performance", 
                "make money", "buy", "sell", "good investment"
            ]
            if any(kw in query_lower for kw in advisory_keywords):
                return "ADVISORY"
            return "FACTUAL"

        prompt = (
            "You are a classification system for a mutual fund database query router.\n"
            "Your job is to classify the user query into one of two categories: 'FACTUAL' or 'ADVISORY'.\n\n"
            "Classification Rules:\n"
            "1. 'FACTUAL': Requests for objective, verifiable details (e.g. expense ratios, exit loads, fund manager name/bio/experience, min SIP/lumpsum amounts, launch date, assets under management - AUM, current NAV or NAV dates, download steps for statement/KIM/SID/factsheets).\n"
            "2. 'ADVISORY': Requests seeking investment advice, opinions, recommendations, or planning guidance. This includes comparative queries (e.g., 'which fund is better', 'should I invest in X', 'is this fund good for retirement', 'compare HDFC Small Cap and HDFC Defence to tell me which to buy', 'do you recommend HDFC Gold').\n\n"
            "Instructions:\n"
            "Output ONLY the single word 'FACTUAL' or 'ADVISORY'. Do not output any other text or explanation.\n\n"
            f"User Query: {query}\n"
            "Category:"
        )

        try:
            response = self.model.generate_content(
                contents=prompt,
                generation_config={"temperature": 0.0}
            )
            category = response.text.strip().upper()
            if "ADVISORY" in category:
                return "ADVISORY"
            return "FACTUAL"
        except Exception:
            # Fallback to local routing if API call fails
            return self.classify_intent_local(query)

    def classify_intent_local(self, query: str) -> str:
        query_lower = query.lower()
        advisory_keywords = [
            "should i", "better", "recommend", "advice", "suggest", 
            "opinion", "worth investing", "which fund", "compare performance", 
            "make money", "buy", "sell", "good investment"
        ]
        if any(kw in query_lower for kw in advisory_keywords):
            return "ADVISORY"
        return "FACTUAL"
