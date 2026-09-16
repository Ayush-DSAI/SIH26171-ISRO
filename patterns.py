"""
PII Patterns and Checksum Validation Algorithms
Author: Abhishek (Privacy + Redaction + Testing Lead)

Includes:
- Verhoeff Algorithm for Aadhaar verification (Dihedral Group D5)
- Luhn Algorithm for Credit Card verification
- Regex patterns for Indian & Global PII (Aadhaar, PAN, Phone, Email, Credit Cards)
"""

import re
from typing import List, Dict, Any, Optional

# =====================================================================
# VERHOEFF ALGORITHM (Dihedral Group D5 on digits 0..9)
# Used specifically for Indian UIDAI Aadhaar 12-digit number validation
# =====================================================================

VERHOEFF_D: List[List[int]] = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
    [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
    [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
    [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
    [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
    [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
    [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
    [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
]

VERHOEFF_P: List[List[int]] = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
    [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
    [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
    [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
    [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
    [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
    [7, 0, 4, 6, 9, 1, 3, 2, 5, 8],
]

VERHOEFF_INV: List[int] = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]


def validate_verhoeff(number: str) -> bool:
    """
    Validates a number string using the Verhoeff checksum algorithm.
    Used to eliminate false positives when detecting 12-digit Aadhaar numbers.
    """
    clean_num = re.sub(r"\D", "", str(number))
    if not clean_num:
        return False

    c = 0
    digits = [int(ch) for ch in clean_num]
    for i, digit in enumerate(reversed(digits)):
        c = VERHOEFF_D[c][VERHOEFF_P[i % 8][digit]]
    return c == 0


def generate_verhoeff(number_without_checksum: str) -> str:
    """
    Generates the Verhoeff check digit for a given digit string.
    Returns the check digit character ('0'-'9').
    """
    clean_num = re.sub(r"\D", "", str(number_without_checksum))
    c = 0
    digits = [int(ch) for ch in clean_num]
    for i, digit in enumerate(reversed(digits)):
        c = VERHOEFF_D[c][VERHOEFF_P[(i + 1) % 8][digit]]
    return str(VERHOEFF_INV[c])


# =====================================================================
# LUHN ALGORITHM (Mod 10)
# Used for Credit / Debit Card validation
# =====================================================================

def validate_luhn(card_number: str) -> bool:
    """
    Validates credit/debit card numbers using the Luhn Mod-10 algorithm.
    Supports card lengths from 11 to 19 digits.
    """
    clean_card = re.sub(r"\D", "", str(card_number))
    if len(clean_card) < 11 or len(clean_card) > 19:
        return False

    total = 0
    reverse_digits = [int(d) for d in reversed(clean_card)]
    for i, digit in enumerate(reverse_digits):
        if i % 2 == 1:
            doubled = digit * 2
            total += (doubled - 9) if doubled > 9 else doubled
        else:
            total += digit
    return total % 10 == 0


# =====================================================================
# REGEX PATTERNS (Compiles with boundary guards)
# =====================================================================

# Aadhaar: 12 digits, often formatted as 4-4-4 (e.g. 1234 5678 9012 or 1234-5678-9012 or continuous)
# Note: First digit of Aadhaar cannot be 0 or 1 per UIDAI specification
AADHAAR_PATTERN = re.compile(
    r"\b[2-9]\d{3}[\s-]?[0-9]{4}[\s-]?[0-9]{4}\b"
)

# Indian PAN Card: 5 uppercase letters, 4 digits, 1 uppercase letter (e.g. ABCDE1234F)
# 4th character denotes status (P=Individual, C=Company, H=HUF, etc.)
PAN_PATTERN = re.compile(
    r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b"
)

# Indian Mobile Phone Number: starts with 6, 7, 8, 9, with optional +91, 91, or 0 prefix
# Strictly guarded by negative lookahead and lookbehind for digits
PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:(?:\+91|91|0)[\s-]?)?[6-9]\d{9}(?!\d)"
)

# Standard RFC-compliant Email Address
EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

# Credit Cards: Visa (4xxx), Mastercard (51-55 or 22-27), Amex (34, 37), RuPay (60, 65, 81-82, 353, 356)
CREDIT_CARD_PATTERN = re.compile(
    r"\b(?:\d{4}[\s-]?){3}\d{4}\b|\b\d{13,19}\b"
)

# Masked Password strings (e.g. '••••••••' or '********' or mixed)
PASSWORD_MASK_PATTERN = re.compile(
    r"(?:\*{3,}|•{3,}|[\u2022]{3,})"
)

# Sensitive Field Name / Attribute Keywords
SENSITIVE_FIELD_KEYWORDS = [
    "password", "passwd", "pwd", "secret", "pin", "passcode", "cvv", "cvc",
    "email", "e-mail", "mail",
    "phone", "mobile", "cell", "contact", "tele",
    "aadhaar", "adhar", "uidai", "pan", "ssn",
    "credit_card", "card_number", "debit_card", "account_number",
    "otp", "security_code"
]
