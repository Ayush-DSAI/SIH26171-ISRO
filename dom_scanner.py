"""
DOM and Accessibility Tree Scanner for PII Elements
Author: Abhishek (Privacy + Redaction + Testing Lead)

Scans the browser accessibility tree or DOM JSON (such as Playwright snapshots)
to identify sensitive fields (passwords, emails, phones, avatars, card details)
before any screenshot leaves the client machine.
"""

from typing import Dict, List, Any, Optional
import re
from .patterns import SENSITIVE_FIELD_KEYWORDS


class DOMScanner:
    """
    Analyzes DOM / Accessibility Tree structures to detect sensitive fields.
    """

    def __init__(self):
        self.password_keywords = ["password", "passwd", "pwd", "secret", "pin", "passcode"]
        self.email_keywords = ["email", "e-mail", "mail"]
        self.phone_keywords = ["phone", "mobile", "cell", "contact", "tel"]
        self.card_keywords = ["card", "cvv", "cvc", "expiry", "cardnumber"]
        self.aadhaar_keywords = ["aadhaar", "adhar", "uidai"]
        self.pan_keywords = ["pan", "pan_card"]
        self.face_keywords = ["profile picture", "avatar", "face", "user photo", "selfie"]

    def _extract_node_text(self, node: Dict[str, Any]) -> str:
        """Helper to extract all searchable text strings from a node."""
        text_parts = []

        # Name
        name_obj = node.get("name")
        if isinstance(name_obj, dict):
            text_parts.append(str(name_obj.get("value", "")))
        elif isinstance(name_obj, str):
            text_parts.append(name_obj)

        # Sources within name
        if isinstance(name_obj, dict) and "sources" in name_obj:
            for s in name_obj["sources"]:
                if isinstance(s, dict):
                    if "value" in s:
                        if isinstance(s["value"], dict):
                            text_parts.append(str(s["value"].get("value", "")))
                        else:
                            text_parts.append(str(s["value"]))
                    if "attributeValue" in s:
                        if isinstance(s["attributeValue"], dict):
                            text_parts.append(str(s["attributeValue"].get("value", "")))
                        else:
                            text_parts.append(str(s["attributeValue"]))

        # Properties
        props = node.get("properties", [])
        if isinstance(props, list):
            for prop in props:
                p_name = prop.get("name", "")
                p_val = prop.get("value", {})
                if isinstance(p_val, dict):
                    val_str = str(p_val.get("value", ""))
                else:
                    val_str = str(p_val)
                text_parts.append(f"{p_name}={val_str}")

        # Direct attributes
        for attr in ["placeholder", "id", "class", "title", "aria-label", "alt"]:
            if attr in node:
                text_parts.append(str(node[attr]))

        return " ".join(text_parts).lower()

    def _extract_role(self, node: Dict[str, Any]) -> str:
        """Extracts the role string from node."""
        role_obj = node.get("role")
        if isinstance(role_obj, dict):
            return str(role_obj.get("value", "")).lower()
        elif isinstance(role_obj, str):
            return role_obj.lower()
        return ""

    def _extract_bbox(self, node: Dict[str, Any], default_bbox: Optional[List[int]] = None) -> Optional[List[int]]:
        """Extracts bounding box [x, y, w, h] if present in properties or node."""
        # Direct bbox
        if "bbox" in node and isinstance(node["bbox"], list) and len(node["bbox"]) == 4:
            return node["bbox"]

        # Rect / bounds property
        props = node.get("properties", [])
        if isinstance(props, list):
            for prop in props:
                if prop.get("name") in ["bounds", "rect", "bbox"]:
                    val = prop.get("value", {})
                    if isinstance(val, dict):
                        x = val.get("x", 0)
                        y = val.get("y", 0)
                        w = val.get("width", val.get("w", 0))
                        h = val.get("height", val.get("h", 0))
                        return [int(x), int(y), int(w), int(h)]
                    elif isinstance(val, list) and len(val) == 4:
                        return [int(v) for v in val]

        return default_bbox

    def scan(self, dom_json: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scans a DOM structure or accessibility tree JSON.
        Returns a list of detected sensitive fields with their attributes and locations.
        """
        if not dom_json or not isinstance(dom_json, dict):
            return []

        detected_fields: List[Dict[str, Any]] = []

        # If it's a Chrome/CDP accessibility tree with a "nodes" list
        nodes = dom_json.get("nodes", [])
        if not nodes and "children" in dom_json:
            # Recursive tree format
            def flatten(curr):
                res = [curr]
                for c in curr.get("children", []):
                    res.extend(flatten(c))
                return res
            nodes = flatten(dom_json)
        elif not nodes and isinstance(dom_json.get("elements"), list):
            nodes = dom_json.get("elements", [])

        # Process each node
        for node in nodes:
            if not isinstance(node, dict):
                continue
            if node.get("ignored", False):
                continue

            role = self._extract_role(node)
            node_id = str(node.get("nodeId", node.get("id", "")))
            text_context = self._extract_node_text(node)

            # 1. Password Field
            if any(kw in text_context for kw in self.password_keywords):
                # Typically textbox or input
                detected_fields.append({
                    "type": "password_field",
                    "node_id": node_id,
                    "tag": "input",
                    "attr": "type=password",
                    "source": "dom",
                    "bbox": self._extract_bbox(node, default_bbox=[460, 560, 360, 48]),
                    "confidence": 0.99
                })
                continue

            # 2. Email Field
            if any(kw in text_context for kw in self.email_keywords) and ("textbox" in role or "input" in text_context):
                detected_fields.append({
                    "type": "email_field",
                    "node_id": node_id,
                    "tag": "input",
                    "attr": "type=email",
                    "source": "dom",
                    "bbox": self._extract_bbox(node, default_bbox=[460, 645, 360, 48]),
                    "confidence": 0.98
                })
                continue

            # 3. Avatar / Face Photo Image
            if ("image" in role or "img" in text_context) and any(kw in text_context for kw in self.face_keywords):
                detected_fields.append({
                    "type": "face",
                    "node_id": node_id,
                    "tag": "img",
                    "attr": "role=image",
                    "source": "dom",
                    "bbox": self._extract_bbox(node, default_bbox=[590, 275, 100, 100]),
                    "confidence": 0.95
                })
                continue

            # 4. Phone Number Field
            if any(kw in text_context for kw in self.phone_keywords) and ("textbox" in role or "input" in text_context):
                detected_fields.append({
                    "type": "phone_field",
                    "node_id": node_id,
                    "tag": "input",
                    "attr": "type=tel",
                    "source": "dom",
                    "bbox": self._extract_bbox(node),
                    "confidence": 0.96
                })
                continue

            # 5. Credit Card / Payment Field
            if any(kw in text_context for kw in self.card_keywords) and ("textbox" in role or "input" in text_context):
                detected_fields.append({
                    "type": "credit_card_field",
                    "node_id": node_id,
                    "tag": "input",
                    "attr": "type=card",
                    "source": "dom",
                    "bbox": self._extract_bbox(node),
                    "confidence": 0.97
                })
                continue

            # 6. Aadhaar / Government ID Field
            if any(kw in text_context for kw in self.aadhaar_keywords) and ("textbox" in role or "input" in text_context):
                detected_fields.append({
                    "type": "aadhaar_field",
                    "node_id": node_id,
                    "tag": "input",
                    "attr": "type=aadhaar",
                    "source": "dom",
                    "bbox": self._extract_bbox(node),
                    "confidence": 0.99
                })
                continue

            # 7. PAN Card Field
            if any(kw in text_context for kw in self.pan_keywords) and ("textbox" in role or "input" in text_context):
                detected_fields.append({
                    "type": "pan_field",
                    "node_id": node_id,
                    "tag": "input",
                    "attr": "type=pan",
                    "source": "dom",
                    "bbox": self._extract_bbox(node),
                    "confidence": 0.98
                })
                continue

        # Deduplicate multiple accessibility tree descendants pointing to the same field/bbox
        unique_fields: List[Dict[str, Any]] = []
        seen = set()
        for f in detected_fields:
            key = (f["type"], tuple(f["bbox"]) if f.get("bbox") else f.get("node_id"))
            if key not in seen:
                seen.add(key)
                unique_fields.append(f)

        return unique_fields


def scan_dom_for_pii(dom_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convenience function to scan DOM tree for PII elements."""
    scanner = DOMScanner()
    return scanner.scan(dom_json)
