import os
import re
import json
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from src.database import MutualFundsDB
from src.llm import GeminiClient
from src.sanitizer import PIISanitizer
from src.classifier import IntentClassifier

# Whitelisted Schemes Lookup
SCHEMES_MAP = {
    "defence": ("HDFC Defence Fund Direct Growth", "https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth"),
    "defense": ("HDFC Defence Fund Direct Growth", "https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth"),
    "small cap": ("HDFC Small Cap Fund Direct Growth", "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth"),
    "smallcap": ("HDFC Small Cap Fund Direct Growth", "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth"),
    "silver": ("HDFC Silver ETF FoF Direct Growth", "https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth"),
    "gold": ("HDFC Gold ETF Fund of Fund Direct Plan Growth", "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth"),
    "nifty 50": ("HDFC Nifty 50 Index Fund Direct Growth", "https://groww.in/mutual-funds/hdfc-nifty-50-index-fund-direct-growth"),
    "nifty": ("HDFC Nifty 50 Index Fund Direct Growth", "https://groww.in/mutual-funds/hdfc-nifty-50-index-fund-direct-growth"),
    "index": ("HDFC Nifty 50 Index Fund Direct Growth", "https://groww.in/mutual-funds/hdfc-nifty-50-index-fund-direct-growth")
}

# Competitor AMCs
COMPETITORS = ["sbi", "icici", "axis", "nippon", "quant", "tata", "dsp", "kotak", "mirae", "uti", "motilal", "ppfas", "parag parikh"]

class RAGOrchestrator:
    def __init__(self, db: Optional[MutualFundsDB] = None, llm: Optional[GeminiClient] = None):
        self.db = db or MutualFundsDB()
        self.llm = llm or GeminiClient()
        self.collection = self.db.get_collection()
        self.sanitizer = PIISanitizer()
        self.classifier = IntentClassifier(api_key=self.llm.api_key)

    def detect_competitor(self, query: str) -> Optional[str]:
        """Detects if query targets a competitor AMC."""
        query_lower = query.lower()
        for competitor in COMPETITORS:
            if re.search(r'\b' + re.escape(competitor) + r'\b', query_lower):
                return competitor.upper()
        return None

    def match_target_scheme(self, query: str) -> Tuple[Optional[str], Optional[str]]:
        """Maps query keywords to target scheme name and URL."""
        query_lower = query.lower()
        for kw, (scheme_name, url) in SCHEMES_MAP.items():
            if kw in query_lower:
                return scheme_name, url
        return None, None

    def split_sentences(self, text: str) -> List[str]:
        """Splits text into sentences using punctuation boundaries."""
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s for s in sentences if s.strip()]

    def enforce_formatting_compliance(self, text: str, fallback_url: str, sync_date: str) -> str:
        """Parses output to strictly limit answer text to 3 sentences and structure links/footers."""
        # Clean out footer
        text_clean = re.sub(r'(?i)last updated from sources:.*', '', text).strip()
        
        # Find all markdown links
        links = re.findall(r'(\[([^\]]+)\]\((https?://[^\)]+)\))', text_clean)
        
        # Remove link patterns and preceding labels (e.g. Source: ) from the main answer text body
        answer_body = text_clean
        for full_match, title, url in links:
            answer_body = re.sub(r'(?i)(source|link|citation):\s*' + re.escape(full_match), '', answer_body)
            answer_body = answer_body.replace(full_match, "")

        # Split remaining text into sentences
        sentences = self.split_sentences(answer_body)
        if len(sentences) > 3:
            final_answer = " ".join(sentences[:3])
        else:
            final_answer = " ".join(sentences)
            
        # Clean multiple spaces or trailing punctuation cleanups
        final_answer = re.sub(r'\s+', ' ', final_answer).strip()

        # Format citation link
        if links:
            first_link_label = links[0][1]
            first_link_url = links[0][2]
            citation_link = f"Source: [{first_link_label}]({first_link_url})"
        else:
            citation_link = f"Source: [Groww Mutual Fund Link]({fallback_url})"

        # Assemble compliance output
        compliance_output = (
            f"{final_answer}\n\n"
            f"{citation_link}\n"
            f"Last updated from sources: {sync_date}"
        )
        return compliance_output

    def query(self, user_query: str) -> str:
        """Processes query through sanitizer, competitor blocks, classifier, vector search, and LLM."""
        # 1. PII Sanitization Check
        sanitized_query, has_pii = self.sanitizer.sanitize_query(user_query)
        if has_pii:
            return (
                "Warning: For your privacy and security, please do not share personal details like PAN, "
                "Aadhaar, bank account numbers, phone numbers, or email addresses. Query rejected."
            )

        # 2. Competitor Block Check
        competitor = self.detect_competitor(sanitized_query)
        if competitor:
            return (
                f"I only contain facts about HDFC mutual fund schemes. I do not have access to official information "
                f"regarding {competitor} schemes, and I am prohibited from providing advisory comparisons."
            )

        # 3. Intent Classification Check (Allowed Factual vs. Refused Advisory)
        intent = self.classifier.classify_intent(sanitized_query)
        if intent == "ADVISORY":
            return (
                "I am a facts-only mutual fund FAQ assistant and I am prohibited from providing investment advice, "
                "opinions, or scheme recommendations. For investment guidance and investor education, please refer to the "
                "official [AMFI Investor Education](https://www.amfiindia.com/investor-corner) or [SEBI Investor Education](https://investor.sebi.gov.in/) portals."
            )

        # 4. Pre-routing Target Filter
        target_scheme, target_url = self.match_target_scheme(sanitized_query)
        
        # 5. Retrieve Context
        if target_scheme:
            results = self.collection.query(
                query_texts=[sanitized_query],
                n_results=2
            )
            fallback_url = target_url
        else:
            # Default retrieval fallback
            results = self.collection.query(
                query_texts=[sanitized_query],
                n_results=2
            )
            fallback_url = "https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth"

        # Assemble chunks
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        
        if not documents:
            return (
                f"I do not have access to that information in my current official source database.\n\n"
                f"Source: [HDFC AMC Link]({fallback_url})\n"
                f"Last updated from sources: {datetime.now().strftime('%d-%b-%Y')}"
            )

        context = "\n---\n".join(documents)
        
        # Get sync date from central last_sync.json if available, fallback to chunk metadata
        sync_date = None
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        last_sync_path = os.path.join(base_dir, "data", "last_sync.json")
        if os.path.exists(last_sync_path):
            try:
                with open(last_sync_path, "r", encoding="utf-8") as f:
                    sync_date = json.load(f).get("last_sync")
            except Exception:
                pass

        if not sync_date:
            sync_date = metadatas[0].get("last_updated") if metadatas else datetime.now().strftime("%d-%b-%Y")
        if not sync_date:
            sync_date = datetime.now().strftime("%d-%b-%Y")

        # 6. Generate Answer via LLM
        raw_answer = self.llm.generate_facts_answer(sanitized_query, context, sync_date)
        
        # 7. Enforce compliance formatting
        compliance_answer = self.enforce_formatting_compliance(raw_answer, fallback_url, sync_date)
        return compliance_answer
