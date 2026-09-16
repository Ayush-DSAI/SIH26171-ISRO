"""
Multi-Layer PII Detection Orchestrator
Author: Abhishek (Privacy + Redaction + Testing Lead)

Combines:
1. DOM Scanning (Layer 1: Structural Inspection)
2. Face Detection (Layer 2: Computer Vision / MediaPipe)
3. Regex Engine (Layer 3: Text & Checksum Validation)
"""

from typing import List, Dict, Any, Optional
from .dom_scanner import DOMScanner
from .face_detector import FaceDetector
from .regex_engine import RegexEngine


class PrivacyDetector:
    """
    Coordinates multi-layered PII detection across visual and structural representations.
    """

    def __init__(self):
        self.dom_scanner = DOMScanner()
        self.face_detector = FaceDetector()
        self.regex_engine = RegexEngine()

    def _bboxes_overlap(self, b1: List[int], b2: List[int], threshold: float = 0.4) -> bool:
        """Calculates IoU between two bounding boxes [x, y, w, h]."""
        if not b1 or not b2 or len(b1) < 4 or len(b2) < 4:
            return False

        x1 = max(b1[0], b2[0])
        y1 = max(b1[1], b2[1])
        x2 = min(b1[0] + b1[2], b2[0] + b2[2])
        y2 = min(b1[1] + b1[3], b2[1] + b2[3])

        intersection_w = max(0, x2 - x1)
        intersection_h = max(0, y2 - y1)
        intersection_area = intersection_w * intersection_h

        area1 = b1[2] * b1[3]
        area2 = b2[2] * b2[3]
        union_area = area1 + area2 - intersection_area

        if union_area <= 0:
            return False
        return (intersection_area / union_area) >= threshold

    def detect_all(
        self,
        image_path: Optional[str] = None,
        dom_json: Optional[Dict[str, Any]] = None,
        page_text: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes multi-layer detection and merges detected PII items.
        """
        all_detections: List[Dict[str, Any]] = []

        # 1. DOM Scan
        dom_findings = []
        if dom_json:
            dom_findings = self.dom_scanner.scan(dom_json)
            all_detections.extend(dom_findings)

        # 2. Face Detection
        if image_path:
            face_findings = self.face_detector.detect(image_path)
            for face in face_findings:
                face_box = face.get("bbox")
                # Check if DOM already detected this face/avatar at overlapping coordinates
                is_duplicate = False
                for existing in all_detections:
                    if existing.get("type") in ["face", "avatar_image"] and existing.get("bbox"):
                        if self._bboxes_overlap(face_box, existing["bbox"]):
                            # Update with higher precision vision coordinates
                            existing["bbox"] = face_box
                            existing["source"] = face.get("source", "mediapipe")
                            is_duplicate = True
                            break
                if not is_duplicate:
                    all_detections.append({
                        "type": "face",
                        "bbox": face_box,
                        "source": face.get("source", "mediapipe"),
                        "confidence": face.get("confidence", 0.95)
                    })

        # 3. Regex Engine Scan (on explicit text or extracted DOM strings)
        text_to_scan = page_text or ""
        if dom_json and not text_to_scan:
            # Flatten textual strings from DOM for regex scan
            text_fragments = []
            for node in dom_json.get("nodes", []):
                name_val = node.get("name", {})
                if isinstance(name_val, dict) and "value" in name_val:
                    text_fragments.append(str(name_val["value"]))
                elif isinstance(name_val, str):
                    text_fragments.append(name_val)
            text_to_scan = " ".join(text_fragments)

        if text_to_scan:
            regex_findings = self.regex_engine.scan(text_to_scan)
            for r_item in regex_findings:
                all_detections.append({
                    "type": r_item["type"],
                    "bbox": None,
                    "source": "regex",
                    "value": "REDACTED",
                    "confidence": r_item.get("confidence", 0.98)
                })

        return all_detections
