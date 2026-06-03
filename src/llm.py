import os
import google.generativeai as genai
from typing import Optional

class GeminiClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            # We raise a clear message, but do not crash immediately so tests can run/be mocked if needed
            print("WARNING: GEMINI_API_KEY environment variable not set. Gemini client will fail on queries.")
        else:
            genai.configure(api_key=self.api_key)
            
        # Initialize Gemini 1.5 Flash model
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={"temperature": 0.0}
        )

    def generate_facts_answer(self, query: str, context: str, sync_date: str) -> str:
        """Queries Gemini with strict facts-only formatting instructions."""
        if not self.api_key:
            return f"Mocked Response: Here are details about the scheme.\nSource: [HDFC Scheme](https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth)\nLast updated from sources: {sync_date}"

        system_instruction = (
            "You are a compliant, facts-only mutual fund FAQ assistant. Your core directive is to answer the user query based ONLY on the factual text provided in the Context below. Do not use outside knowledge or speculate.\n\n"
            "Strict Compliance Rules:\n"
            "1. Answer length: Maximum of 3 sentences. Be extremely brief, concise, and direct.\n"
            "2. Objective tone: Under no circumstances provide investment suggestions, buy/sell recommendations, opinions, or advice. If the user asks for advice or recommendations, politely refuse and state you only provide factual details.\n"
            "3. Source Citation: Include exactly one citation link from the Context formatted as a standard markdown link: [Source Title](URL). Choose the URL matching the fund in question.\n"
            f"4. Footer: You must end your response with a blank line, followed by the exact text: 'Last updated from sources: {sync_date}'\n"
            "5. Refusal: If the context does not contain the answer, politely state: 'I do not have access to that information in my current official source database.' and provide the source citation if a matching scheme is known."
        )

        prompt = (
            f"Context Chunks:\n---\n{context}\n---\n\n"
            f"User Query: {query}\n\n"
            f"Factual Response:"
        )

        response = self.model.generate_content(
            contents=prompt,
            generation_config={"temperature": 0.0},
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
        )
        
        return response.text.strip()
