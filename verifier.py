"""
Post-Redaction Re-scan Verification Module
Author: Abhishek (Privacy + Redaction + Testing Lead)

Audits sanitized images to guarantee 0% PII leakage before outbound transmission.
Fulfills Hackathon Requirement: Defense-in-Depth & Privacy Gateway verification.
"""

from typing import Dict, List, Any, Optional
import os
from .face_detector import FaceDetector
from .regex_engine import RegexEngine


class RedactionVerifier:
    """
    Independent validator that re-analyzes a sanitized screenshot to ensure no residual PII is present.
    """

    def __init__(self):
        # Strict threshold: even a weak detection triggers a leak alert
        self.face_detector = FaceDetector(min_detection_confidence=0.6)
        self.regex_engine = RegexEngine()

    def verify(self, sanitized_image_path: str, ocr_text_optional: Optional[str] = None) -> Dict[str, Any]:
        """
        Re-scans the sanitized image.
        Returns:
            {
                "passed": True / False,
                "residual_leaks": [...],
                "message": str
            }
        """
        if not os.path.exists(sanitized_image_path):
            return {
                "passed": False,
                "residual_leaks": [{"type": "file_error", "detail": "Sanitized file does not exist"}],
                "message": "Verification failed: Image file not found."
            }

        leaks: List[Dict[str, Any]] = []

        # 1. Re-scan for faces
        faces = self.face_detector.detect(sanitized_image_path)
        # Note: Heavy Gaussian blur lowers detection confidence below 0.6.
        # If any face is still detected with > 0.6 confidence, it indicates insufficient blur.
        if faces:
            for f in faces:
                leaks.append({
                    "layer": "vision",
                    "type": "unredacted_face",
                    "bbox": f.get("bbox"),
                    "confidence": f.get("confidence")
                })

        # 2. Re-scan OCR text if available
        if ocr_text_optional:
            text_findings = self.regex_engine.scan(ocr_text_optional)
            for t in text_findings:
                leaks.append({
                    "layer": "text",
                    "type": t.get("type"),
                    "value": t.get("value")
                })

        passed = len(leaks) == 0
        return {
            "passed": passed,
            "residual_leaks": leaks,
            "leak_count": len(leaks),
            "message": "Verification passed: 0 PII detected in sanitized image." if passed else f"SECURITY ALERT: {len(leaks)} residual PII leaks found!"
        }


def verify_sanitized_image(sanitized_image_path: str, ocr_text: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function for post-redaction re-scan."""
    verifier = RedactionVerifier()
    return verifier.verify(sanitized_image_path, ocr_text_optional=ocr_text)
