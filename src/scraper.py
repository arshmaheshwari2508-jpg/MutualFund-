import requests
from bs4 import BeautifulSoup
import json
import os
from typing import Dict, Any, List

class GrowwScraper:
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def fetch_page_html(self, url: str) -> str:
        """Fetches raw HTML from Groww scheme page."""
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    def extract_next_data(self, html: str) -> Dict[str, Any]:
        """Parses BeautifulSoup and extracts the Next.js __NEXT_DATA__ JSON state."""
        soup = BeautifulSoup(html, "html.parser")
        script_tag = soup.find("script", id="__NEXT_DATA__")
        if not script_tag:
            raise ValueError("Failed to locate __NEXT_DATA__ script hydration tag in HTML.")
        
        try:
            return json.loads(script_tag.string)
        except Exception as e:
            raise ValueError(f"Failed to parse inner Next.js JSON: {e}")

    def parse_scheme_data(self, next_data: Dict[str, Any], source_url: str) -> Dict[str, Any]:
        """Extracts required fields from the Next.js data dict structure."""
        page_props = next_data.get("props", {}).get("pageProps", {})
        mf_data = page_props.get("mfServerSideData", {})
        
        if not mf_data:
            raise ValueError("No mfServerSideData found in page hydration properties.")

        # Extract core fields
        scheme_name = mf_data.get("scheme_name") or mf_data.get("fund_name")
        expense_ratio = mf_data.get("expense_ratio")
        exit_load = mf_data.get("exit_load")
        
        # Validation checks for edge case mitigation
        if not scheme_name:
            raise ValueError("Invalid Groww payload: Missing 'scheme_name'")
        if expense_ratio is None:
            raise ValueError("Invalid Groww payload: Missing 'expense_ratio'")
        if not exit_load:
            raise ValueError("Invalid Groww payload: Missing 'exit_load'")

        # Parse managers
        managers = []
        raw_managers = mf_data.get("fund_manager_details", [])
        for m in raw_managers:
            person_name = m.get("person_name")
            if not person_name:
                continue
            
            funds_managed = []
            for f in m.get("funds_managed", []):
                fname = f.get("scheme_name")
                if fname:
                    funds_managed.append(fname)

            managers.append({
                "name": person_name,
                "education": m.get("education", "N/A"),
                "experience": m.get("experience", "N/A"),
                "funds_managed": funds_managed
            })

        # Assemble clean flat structure
        parsed_data = {
            "scheme_name": scheme_name,
            "fund_house": mf_data.get("fund_house", "HDFC Mutual Fund"),
            "category": mf_data.get("category", "Equity"),
            "sub_category": mf_data.get("sub_category", "N/A"),
            "risk": mf_data.get("nfo_risk") or "Very High",
            "min_sip_investment": mf_data.get("min_sip_investment") or mf_data.get("min_investment_amount") or 100,
            "min_lumpsum_investment": mf_data.get("min_investment_amount") or 100,
            "expense_ratio": f"{expense_ratio}%" if isinstance(expense_ratio, (int, float)) else str(expense_ratio),
            "exit_load": str(exit_load),
            "benchmark_index": mf_data.get("benchmark_name") or "N/A",
            "aum_in_cr": mf_data.get("aum") or 0.0,
            "launch_date": mf_data.get("launch_date") or "N/A",
            "nav": mf_data.get("nav") or 0.0,
            "nav_date": mf_data.get("nav_date") or "N/A",
            "source_url": source_url,
            "managers": managers
        }
        
        return parsed_data

    def scrape(self, url: str) -> Dict[str, Any]:
        """Utility to fetch and parse a single Groww mutual fund page URL."""
        html = self.fetch_page_html(url)
        next_data = self.extract_next_data(html)
        return self.parse_scheme_data(next_data, url)

    def scrape_and_save_to_json(self, urls: List[str], output_path: str) -> List[Dict[str, Any]]:
        """Scrapes multiple URLs and saves the list of cleaned schemes to a JSON data file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        schemes = []
        for url in urls:
            try:
                data = self.scrape(url)
                schemes.append(data)
            except Exception as e:
                raise RuntimeError(f"Failed parsing URL {url}: {e}")
                
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(schemes, f, indent=2, ensure_ascii=False)
            
        print(f"Successfully saved {len(schemes)} scraped schemes to local data file: {output_path}")
        return schemes
