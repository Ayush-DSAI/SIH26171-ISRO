"""
Regex Engine for Text PII Detection
Author: Abhishek (Privacy + Redaction + Testing Lead)

Scans page text, DOM contents, or extracted OCR text to detect:
- Aadhaar numbers (with Verhoeff algorithm verification)
- Indian PAN card numbers
- Indian Mobile Phone numbers (+91...)
- Email addresses
- Credit / Debit Card numbers (with Luhn algorithm verification)
- Masked password characters (*** or •••)
"""

from typing import List, Dict, Any, Optional
import re
from .patterns import (
    validate_verhoeff,
    validate_luhn,
    AADHAAR_PATTERN,
    PAN_PATTERN,
    PHONE_PATTERN,
    EMAIL_PATTERN,
    CREDIT_CARD_PATTERN,
    PASSWORD_MASK_PATTERN,
)


class RegexEngine:
    """
    Engine to identify PII within raw text strings using regex patterns and checksum validators.
    """

    def __init__(self, mask_pii_in_output: bool = False):
        self.mask_pii_in_output = mask_pii_in_output

    def _mask_value(self, val: str, pii_type: str) -> str:
        """Helper to mask sensitive values for safe logging/telemetry."""
        if not self.mask_pii_in_output:
            return val
        if pii_type == "email":
            parts = val.split("@")
            if len(parts) == 2 and len(parts[0]) > 2:
                return f"{parts[0][:2]}***@{parts[1]}"
            return "***@***"
        elif pii_type in ["aadhaar", "credit_card", "phone"]:
            clean = re.sub(r"\D", "", val)
            if len(clean) >= 4:
                return f"***-***-{clean[-4:]}"
            return "******"
        elif pii_type == "pan":
            return f"{val[:2]}***{val[-1:]}" if len(val) >= 3 else "*****"
        return "REDACTED"

    def scan(self, text: str) -> List[Dict[str, Any]]:
        """
        Scans input text and returns a list of detected PII matches with their locations and types.
        """
        if not text or not isinstance(text, str):
            return []

        results: List[Dict[str, Any]] = []

        # 1. Aadhaar Numbers (Must pass Verhoeff Algorithm check)
        for match in AADHAAR_PATTERN.finditer(text):
            raw_val = match.group(0)
            digits_only = re.sub(r"\D", "", raw_val)
            if len(digits_only) == 12:
                if validate_verhoeff(digits_only):
                    results.append({
                        "type": "aadhaar_text",
                        "value": self._mask_value(raw_val, "aadhaar"),
                        "raw_length": len(raw_val),
                        "start": match.start(),
                        "end": match.end(),
                        "source": "regex",
                        "confidence": 0.99,
                        "checksum_verified": True
                    })

        # 2. PAN Card Numbers
        for match in PAN_PATTERN.finditer(text):
            raw_val = match.group(0)
            # 4th character must be a valid status code in Indian ITD:
            # P=Person, C=Company, H=HUF, A=AOP, B=BOI, G=Govt, J=Artificial Juridical, L=Local, F=Firm, T=Trust
            status_char = raw_val[3]
            is_valid_status = status_char in "PCHABGJLFT"
            results.append({
                "type": "pan_text",
                "value": self._mask_value(raw_val, "pan"),
                "raw_length": len(raw_val),
                "start": match.start(),
                "end": match.end(),
                "source": "regex",
                "confidence": 0.98 if is_valid_status else 0.90,
                "status_code": status_char
            })

        # 3. Email Addresses
        for match in EMAIL_PATTERN.finditer(text):
            raw_val = match.group(0)
            results.append({
                "type": "email_text",
                "value": self._mask_value(raw_val, "email"),
                "raw_length": len(raw_val),
                "start": match.start(),
                "end": match.end(),
                "source": "regex",
                "confidence": 0.99
            })

        # 4. Indian Mobile Phone Numbers
        for match in PHONE_PATTERN.finditer(text):
            raw_val = match.group(0)
            digits_only = re.sub(r"\D", "", raw_val)
            # Valid mobile has 10 digits (excluding 91 or 0 prefix)
            if digits_only.startswith("91") and len(digits_only) == 12:
                core_digits = digits_only[2:]
            elif digits_only.startswith("0") and len(digits_only) == 11:
                core_digits = digits_only[1:]
            else:
                core_digits = digits_only

            if len(core_digits) == 10 and core_digits[0] in "6789":
                results.append({
                    "type": "phone_text",
                    "value": self._mask_value(raw_val, "phone"),
                    "raw_length": len(raw_val),
                    "start": match.start(),
                    "end": match.end(),
                    "source": "regex",
                    "confidence": 0.97
                })

        # 5. Credit Cards (Must pass Luhn check)
        for match in CREDIT_CARD_PATTERN.finditer(text):
            raw_val = match.group(0)
            digits_only = re.sub(r"\D", "", raw_val)
            if 13 <= len(digits_only) <= 19:
                if validate_luhn(digits_only):
                    results.append({
                        "type": "credit_card_text",
                        "value": self._mask_value(raw_val, "credit_card"),
                        "raw_length": len(raw_val),
                        "start": match.start(),
                        "end": match.end(),
                        "source": "regex",
                        "confidence": 0.99,
                        "checksum_verified": True
                    })

        # 6. Masked Passwords (*** or •••)
        for match in PASSWORD_MASK_PATTERN.finditer(text):
            raw_val = match.group(0)
            results.append({
                "type": "password_masked_text",
                "value": "[PASSWORD_MASKED]",
                "raw_length": len(raw_val),
                "start": match.start(),
                "end": match.end(),
                "source": "regex",
                "confidence": 0.95
            })

        return results


def scan_text_for_pii(text: str, mask_pii: bool = False) -> List[Dict[str, Any]]:
    """Convenience function to scan text for PII patterns."""
    engine = RegexEngine(mask_pii_in_output=mask_pii)
    return engine.scan(text)
