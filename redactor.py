"""
Redaction Engine for Screen Sanitization
Author: Abhishek (Privacy + Redaction + Testing Lead)

Fulfills Section 5 Integration Contract:
    redact(image_path: str, dom_json: dict) -> dict

Sanitizes screenshots before they leave the client device:
- Blackout masking on sensitive input fields (passwords, emails, phone, credit card)
- Gaussian blur on detected faces and profile avatars
- Produces sanitized PNG and returns detected PII summary
"""

from typing import Dict, List, Any, Optional
import os
import time
import tempfile
import numpy as np

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from .detector import PrivacyDetector


class RedactionEngine:
    """
    Applies privacy-preserving masks, blackout rectangles, and Gaussian blur to visual contexts.
    """

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or tempfile.gettempdir()
        os.makedirs(self.output_dir, exist_ok=True)
        self.detector = PrivacyDetector()

    def _apply_gaussian_blur_cv2(self, img_bgr: np.ndarray, bbox: List[int]) -> np.ndarray:
        """Applies Gaussian blur to a bounding box region using OpenCV."""
        x, y, w, h = bbox
        ih, iw = img_bgr.shape[:2]
        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(iw, x + w)
        y2 = min(ih, y + h)

        if x2 <= x1 or y2 <= y1:
            return img_bgr

        roi = img_bgr[y1:y2, x1:x2]
        # Kernel size must be odd and proportional to region size
        ksize = (w // 3) * 2 + 1
        ksize = max(15, min(ksize, 99))
        blurred_roi = cv2.GaussianBlur(roi, (ksize, ksize), 30)
        img_bgr[y1:y2, x1:x2] = blurred_roi
        return img_bgr

    def _apply_blackout_cv2(self, img_bgr: np.ndarray, bbox: List[int], label: Optional[str] = None) -> np.ndarray:
        """Draws solid black mask over bounding box using OpenCV."""
        x, y, w, h = bbox
        ih, iw = img_bgr.shape[:2]
        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(iw, x + w)
        y2 = min(ih, y + h)

        if x2 <= x1 or y2 <= y1:
            return img_bgr

        # Draw solid black rectangle
        cv2.rectangle(img_bgr, (x1, y1), (x2, y2), (20, 20, 20), -1)

        # Draw subtle border
        cv2.rectangle(img_bgr, (x1, y1), (x2, y2), (60, 60, 60), 1)

        # Optional label text
        if label:
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.4
            text_size = cv2.getTextSize(label, font, font_scale, 1)[0]
            tx = x1 + max(5, (w - text_size[0]) // 2)
            ty = y1 + (h + text_size[1]) // 2
            cv2.putText(img_bgr, label, (tx, ty), font, font_scale, (200, 200, 200), 1, cv2.LINE_AA)

        return img_bgr

    def _redact_with_cv2(self, image_path: str, detected_pii: List[Dict[str, Any]]) -> str:
        """Redacts image using OpenCV and writes to output."""
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"Cannot load image at {image_path}")

        for pii in detected_pii:
            bbox = pii.get("bbox")
            if not bbox or len(bbox) < 4:
                continue

            pii_type = pii.get("type", "")
            if pii_type == "face":
                img = self._apply_gaussian_blur_cv2(img, bbox)
            else:
                label = "[REDACTED]"
                if "password" in pii_type:
                    label = "[REDACTED: PASSWORD]"
                elif "email" in pii_type:
                    label = "[REDACTED: EMAIL]"
                elif "card" in pii_type:
                    label = "[REDACTED: CARD]"
                img = self._apply_blackout_cv2(img, bbox, label=label)

        timestamp = int(time.time() * 1000)
        output_filename = f"sanitized_{timestamp}.png"
        output_path = os.path.join(self.output_dir, output_filename)
        cv2.imwrite(output_path, img)
        return output_path

    def _redact_with_pil(self, image_path: str, detected_pii: List[Dict[str, Any]]) -> str:
        """Fallback redactor using Pillow if OpenCV is unavailable."""
        img = Image.open(image_path).convert("RGBA")
        draw = ImageDraw.Draw(img)

        for pii in detected_pii:
            bbox = pii.get("bbox")
            if not bbox or len(bbox) < 4:
                continue

            x, y, w, h = bbox
            box = (x, y, x + w, y + h)
            pii_type = pii.get("type", "")

            if pii_type == "face":
                # Crop, blur, paste
                cropped = img.crop(box)
                blurred = cropped.filter(ImageFilter.GaussianBlur(radius=20))
                img.paste(blurred, box)
            else:
                draw.rectangle(box, fill=(20, 20, 20, 255), outline=(60, 60, 60, 255))

        timestamp = int(time.time() * 1000)
        output_filename = f"sanitized_{timestamp}.png"
        output_path = os.path.join(self.output_dir, output_filename)
        img.convert("RGB").save(output_path, "PNG")
        return output_path

    def process(self, image_path: str, dom_json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes complete privacy redaction pipeline on the given image and DOM.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Input image not found: {image_path}")

        # 1. Detect all PII across DOM, vision, and text
        detected_pii = self.detector.detect_all(
            image_path=image_path,
            dom_json=dom_json
        )

        # 2. Apply visual redaction
        if CV2_AVAILABLE:
            sanitized_path = self._redact_with_cv2(image_path, detected_pii)
        elif PIL_AVAILABLE:
            sanitized_path = self._redact_with_pil(image_path, detected_pii)
        else:
            raise RuntimeError("Neither OpenCV nor Pillow is available for image redaction.")

        # 3. Clean up detected_pii structure to match Integration Contract format
        contract_pii: List[Dict[str, Any]] = []
        for item in detected_pii:
            clean_item: Dict[str, Any] = {
                "type": item.get("type"),
                "bbox": item.get("bbox"),
                "source": item.get("source")
            }
            if item.get("value"):
                clean_item["value"] = item.get("value")
            contract_pii.append(clean_item)

        return {
            "sanitized_image_path": sanitized_path,
            "detected_pii": contract_pii
        }


# Global instance for quick calls
_global_engine: Optional[RedactionEngine] = None


def redact(image_path: str, dom_json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Standard Integration Contract function required by Ayush's agent loop.

    Signature:
        redact(image_path: str, dom_json: dict) -> dict

    Returns:
        {
            "sanitized_image_path": "/tmp/sanitized_....png",
            "detected_pii": [
                {"type": "password_field", "bbox": [x, y, w, h], "source": "dom"},
                {"type": "email_field", "bbox": [x, y, w, h], "source": "dom"},
                {"type": "face", "bbox": [x, y, w, h], "source": "mediapipe"},
                {"type": "aadhaar_text", "bbox": None, "source": "regex", "value": "REDACTED"}
            ]
        }
    """
    global _global_engine
    if _global_engine is None:
        _global_engine = RedactionEngine()
    return _global_engine.process(image_path=image_path, dom_json=dom_json)
