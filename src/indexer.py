import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.scraper import GrowwScraper
from src.database import MutualFundsDB
import os

class SchemeIndexer:
    def __init__(self, db: Optional[MutualFundsDB] = None):
        self.db = db or MutualFundsDB()
        self.scraper = GrowwScraper()
        self.collection = self.db.get_collection()

    def generate_chunks(self, scheme: Dict[str, Any], date_str: str) -> List[Dict[str, Any]]:
        """Generates self-contained Markdown sections as logical chunks."""
        scheme_name = scheme["scheme_name"]
        source_url = scheme["source_url"]
        
        chunks = []

        # 1. Fund Overview Section Chunk
        overview_text = (
            f"### Fund Overview: {scheme_name}\n"
            f"The {scheme_name} is an HDFC mutual fund under the category {scheme['category']} "
            f"({scheme['sub_category']}) and is managed by {scheme['fund_house']}.\n"
            f"Key Factual Parameters:\n"
            f"- Riskometer Risk Classification: {scheme['risk']}\n"
            f"- Benchmark Index: {scheme['benchmark_index']}\n"
            f"- Assets Under Management (AUM): {scheme['aum_in_cr']} Crores\n"
            f"- Expense Ratio: {scheme['expense_ratio']}\n"
            f"- Exit Load details: {scheme['exit_load']}\n"
            f"- Minimum SIP Investment: Rs. {scheme['min_sip_investment']}\n"
            f"- Minimum Lumpsum Investment: Rs. {scheme['min_lumpsum_investment']}\n"
            f"- Current NAV: Rs. {scheme['nav']} (as of {scheme['nav_date']})\n"
            f"- Launch Date: {scheme['launch_date']}"
        )
        chunks.append({
            "id": f"{scheme_name.lower().replace(' ', '_')}_overview",
            "document": overview_text,
            "metadata": {
                "scheme_name": scheme_name,
                "source_url": source_url,
                "chunk_type": "overview",
                "last_updated": date_str
            }
        })

        # 2. Fund Manager Section Chunks
        for mgr in scheme.get("managers", []):
            mgr_name = mgr["name"]
            funds_str = ", ".join(mgr.get("funds_managed", [])) or "None"
            mgr_text = (
                f"### Fund Manager: {mgr_name} ({scheme_name})\n"
                f"{mgr_name} is a designated fund manager for {scheme_name}.\n"
                f"Professional Profile details:\n"
                f"- Education details: {mgr['education']}\n"
                f"- Experience details: {mgr['experience']}\n"
                f"- Other managed schemes: {funds_str}"
            )
            chunks.append({
                "id": f"{scheme_name.lower().replace(' ', '_')}_manager_{mgr_name.lower().replace(' ', '_')}",
                "document": mgr_text,
                "metadata": {
                    "scheme_name": scheme_name,
                    "source_url": source_url,
                    "chunk_type": "manager",
                    "manager_name": mgr_name,
                    "last_updated": date_str
                }
            })

        # 3. Documents & Download Procedure Section Chunk
        docs_text = (
            f"### Scheme Documents & Statements: {scheme_name}\n"
            f"To download capital gains reports, account statements, or official regulatory documents "
            f"(including Key Information Memorandum - KIM, Scheme Information Document - SID, and official factsheets) "
            f"for {scheme_name}, please log into your Groww or HDFC Mutual Fund customer dashboard.\n"
            f"Alternatively, official files are directly downloadable via the HDFC Mutual Fund AMC portal."
        )
        chunks.append({
            "id": f"{scheme_name.lower().replace(' ', '_')}_documents",
            "document": docs_text,
            "metadata": {
                "scheme_name": scheme_name,
                "source_url": source_url,
                "chunk_type": "documents",
                "last_updated": date_str
            }
        })

        return chunks

    def index_from_file(self, file_path: str):
        """Loads schemes from a local data file and indexes them into ChromaDB."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Local schemes data file not found at {file_path}")
            
        with open(file_path, "r", encoding="utf-8") as f:
            schemes = json.load(f)
            
        self.db.delete_collection()
        self.collection = self.db.get_collection()

        sync_date = datetime.now().strftime("%d-%b-%Y")
        
        all_documents = []
        all_metadatas = []
        all_ids = []

        for scheme in schemes:
            chunks = self.generate_chunks(scheme, sync_date)
            for chunk in chunks:
                all_documents.append(chunk["document"])
                all_metadatas.append(chunk["metadata"])
                all_ids.append(chunk["id"])

        self.collection.add(
            documents=all_documents,
            metadatas=all_metadatas,
            ids=all_ids
        )
        print(f"Successfully indexed {len(all_ids)} chunks from local data file: {file_path}")

    def index_urls(self, urls: List[str], temp_file_path: str = "data/schemes.json"):
        """Scrapes the URLs, saves to a temp local file, and then indexes from it."""
        # Convert relative path to absolute
        abs_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), temp_file_path))
        self.scraper.scrape_and_save_to_json(urls, abs_path)
        self.index_from_file(abs_path)
