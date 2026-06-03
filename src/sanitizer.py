import re
from typing import Tuple

# Define regex patterns for sensitive indicators
PAN_PATTERN = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b', re.IGNORECASE)
AADHAAR_PATTERN = re.compile(r'\b[0-9]{4}\s?[0-9]{4}\s?[0-9]{4}\b')
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
PHONE_PATTERN = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
# Detect 9 to 18 digits representing bank account numbers or card details
BANK_PATTERN = re.compile(r'\b[0-9]{9,18}\b')
# Detect typical OTP codes preceded by OTP terms
OTP_PATTERN = re.compile(r'\b(?:otp|one[- ]time[- ]password|verification[- ]code|security[- ]code|pin|passcode)\b[:\s\-=\w]*?\b([0-9]{4,8})\b', re.IGNORECASE)

class PIISanitizer:
    @staticmethod
    def sanitize_query(query: str) -> Tuple[str, bool]:
        """Scans user query for PII and redacts details if found.
        
        Returns:
            Tuple[str, bool]: (sanitized_query_text, has_pii_flag)
        """
        sanitized = query
        has_pii = False

        # 1. PAN Card Check
        if PAN_PATTERN.search(sanitized):
            sanitized = PAN_PATTERN.sub("[REDACTED_PAN]", sanitized)
            has_pii = True

        # 2. Aadhaar Card Check
        if AADHAAR_PATTERN.search(sanitized):
            sanitized = AADHAAR_PATTERN.sub("[REDACTED_AADHAAR]", sanitized)
            has_pii = True

        # 3. Email Check
        if EMAIL_PATTERN.search(sanitized):
            sanitized = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", sanitized)
            has_pii = True

        # 4. Phone Number Check
        if PHONE_PATTERN.search(sanitized):
            sanitized = PHONE_PATTERN.sub("[REDACTED_PHONE]", sanitized)
            has_pii = True

        # 5. Bank Account / Card Check
        # Run only if we haven't already redacted it via Aadhaar or Phone to avoid duplicate labels
        if BANK_PATTERN.search(sanitized):
            # Verify if this sequence is not already inside a redaction placeholder
            if not any(placeholder in sanitized for placeholder in ["[REDACTED_AADHAAR]", "[REDACTED_PHONE]"]):
                sanitized = BANK_PATTERN.sub("[REDACTED_BANK_DETAIL]", sanitized)
                has_pii = True

        # 6. OTP Check
        if OTP_PATTERN.search(sanitized):
            for match in OTP_PATTERN.finditer(sanitized):
                full_match = match.group(0)
                otp_digits = match.group(1)
                redacted_match = full_match.replace(otp_digits, "[REDACTED_OTP]")
                sanitized = sanitized.replace(full_match, redacted_match)
            has_pii = True

        return sanitized, has_pii
