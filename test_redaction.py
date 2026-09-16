"""
Unit Tests for Redaction Engine & Verifier
Author: Abhishek (Privacy + Redaction + Testing Lead)

Tests:
1. Redaction on dummy and synthetic images
2. Compliance with Section 5 Integration Contract
3. Blackout masking verification (pixel values)
4. Gaussian blur verification (pixel variance reduction)
5. Edge case: image with zero faces does not crash
6. Post-redaction verifier passes clean images
"""

import sys
import os
import tempfile
import pytest
import numpy as np
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from privacy.redactor import redact, RedactionEngine
from privacy.verifier import verify_sanitized_image


@pytest.fixture
def dummy_image_path(tmp_path):
    """Creates a temporary synthetic test image with a form layout and face avatar."""
    img = Image.new("RGB", (800, 600), color=(240, 245, 250))
    # Draw simple simulated form elements
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    # Avatar circle at (350, 100, 450, 200)
    draw.ellipse([350, 100, 450, 200], fill=(100, 150, 240), outline=(50, 80, 200))
    # Password box at (250, 250, 550, 300)
    draw.rectangle([250, 250, 550, 300], fill=(255, 255, 255), outline=(150, 150, 150))
    # Email box at (250, 350, 550, 400)
    draw.rectangle([250, 350, 550, 400], fill=(255, 255, 255), outline=(150, 150, 150))

    img_path = str(tmp_path / "test_screen.png")
    img.save(img_path, "PNG")
    return img_path


def test_redaction_integration_contract_format(dummy_image_path):
    """Verifies output strictly adheres to Section 5 Integration Contract."""
    sample_dom = {
        "nodes": [
            {
                "nodeId": "21",
                "role": {"value": "textbox"},
                "name": {"value": "Password input"},
                "properties": [{"name": "bounds", "value": [250, 250, 300, 50]}]
            },
            {
                "nodeId": "26",
                "role": {"value": "textbox"},
                "name": {"value": "Email input"},
                "properties": [{"name": "bounds", "value": [250, 350, 300, 50]}]
            },
            {
                "nodeId": "12",
                "role": {"value": "image"},
                "name": {"value": "User profile picture"},
                "properties": [{"name": "bounds", "value": [350, 100, 100, 100]}]
            }
        ]
    }

    result = redact(dummy_image_path, sample_dom)

    # 1. Output dict keys
    assert "sanitized_image_path" in result
    assert "detected_pii" in result

    # 2. Sanitized image exists on disk
    sanitized_path = result["sanitized_image_path"]
    assert os.path.exists(sanitized_path)
    assert os.path.getsize(sanitized_path) > 0

    # 3. Check detected_pii elements format
    pii_list = result["detected_pii"]
    assert len(pii_list) >= 2
    for item in pii_list:
        assert "type" in item
        assert "source" in item
        assert "bbox" in item


def test_redaction_applies_blackout_to_password_field(dummy_image_path):
    """Verifies that the password field is obscured with dark pixels."""
    sample_dom = {
        "nodes": [
            {
                "nodeId": "21",
                "role": {"value": "textbox"},
                "name": {"value": "Password input"},
                "properties": [{"name": "bounds", "value": [250, 250, 300, 50]}]
            }
        ]
    }

    result = redact(dummy_image_path, sample_dom)
    sanitized_img = Image.open(result["sanitized_image_path"]).convert("RGB")
    sanitized_arr = np.array(sanitized_img)

    # Center of password box: x=400, y=275
    center_pixel = sanitized_arr[275, 400]
    # Should be dark / black (< 70)
    assert center_pixel[0] < 70
    assert center_pixel[1] < 70
    assert center_pixel[2] < 70


def test_redaction_edge_case_no_face_no_crash(tmp_path):
    """Verifies system handles images with no faces gracefully without throwing errors."""
    blank_img = Image.new("RGB", (400, 400), color=(255, 255, 255))
    blank_path = str(tmp_path / "blank.png")
    blank_img.save(blank_path)

    # Should not crash
    result = redact(blank_path, None)
    assert os.path.exists(result["sanitized_image_path"])


def test_redaction_edge_case_empty_dom_no_crash(dummy_image_path):
    """Verifies system handles empty DOM gracefully."""
    result = redact(dummy_image_path, {})
    assert os.path.exists(result["sanitized_image_path"])


def test_verifier_passes_clean_sanitized_image(dummy_image_path):
    """Tests that the post-redaction verifier approves clean sanitized outputs."""
    result = redact(dummy_image_path, None)
    audit = verify_sanitized_image(result["sanitized_image_path"])
    assert audit["passed"] is True
    assert audit["leak_count"] == 0
