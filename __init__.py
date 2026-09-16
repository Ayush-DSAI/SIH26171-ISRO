"""
Privacy & Redaction Subsystem
SIH 2026 - On-device Visual Perception for Lightweight Browser Agents
Author: Abhishek (Privacy + Redaction + Testing Lead)
"""

from .patterns import (
    validate_verhoeff,
    generate_verhoeff,
    validate_luhn,
    AADHAAR_PATTERN,
    PAN_PATTERN,
    PHONE_PATTERN,
    EMAIL_PATTERN,
    CREDIT_CARD_PATTERN,
)
from .dom_scanner import DOMScanner, scan_dom_for_pii
from .face_detector import FaceDetector, detect_faces
from .regex_engine import RegexEngine, scan_text_for_pii
from .detector import PrivacyDetector
from .redactor import redact, RedactionEngine
from .verifier import RedactionVerifier, verify_sanitized_image

__all__ = [
    "validate_verhoeff",
    "generate_verhoeff",
    "validate_luhn",
    "AADHAAR_PATTERN",
    "PAN_PATTERN",
    "PHONE_PATTERN",
    "EMAIL_PATTERN",
    "CREDIT_CARD_PATTERN",
    "DOMScanner",
    "scan_dom_for_pii",
    "FaceDetector",
    "detect_faces",
    "RegexEngine",
    "scan_text_for_pii",
    "PrivacyDetector",
    "redact",
    "RedactionEngine",
    "RedactionVerifier",
    "verify_sanitized_image",
]
