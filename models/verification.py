"""Action verification: did the click actually change the page? (Module N, Day 4 task)

    from models.verification import verify_action
    result = verify_action("before.png", "after.png")
    # {'changed': True, 'changed_fraction': 0.184, 'ssim': 0.71,
    #  'changed_bbox': [310, 250, 420, 160], 'target_changed': None, 'ms': 38.2}

Give `target_bbox=[x, y, w, h]` (the box you clicked) to also learn whether the
area around the target reacted (`target_changed`).

Two tests are combined:
  * pixel difference - how many pixels changed by more than a small amount
  * SSIM (structural similarity) - 1.0 means identical, lower means more different
Tiny changes (a blinking text cursor, anti-aliasing) are ignored on purpose.
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Optional, Sequence, Union

import numpy as np
from PIL import Image

ImageLike = Union[str, Path, bytes, Image.Image]

PIXEL_THRESHOLD = 25          # 0-255: a pixel must change by more than this to count
MIN_CHANGED_FRACTION = 0.002  # 0.2 % of the screen must change for "changed"
SSIM_CHANGED_BELOW = 0.985    # ...or the structure must differ this much
COMPARE_WIDTH = 640           # images are shrunk to this width first (fast + ignores noise)


def _load(image: ImageLike) -> Image.Image:
    if isinstance(image, Image.Image):
        return image
    if isinstance(image, (bytes, bytearray)):
        import io
        return Image.open(io.BytesIO(image))
    return Image.open(image)


def _gray_small(img: Image.Image, size: tuple[int, int]) -> np.ndarray:
    return np.asarray(img.convert("L").resize(size, Image.BILINEAR), dtype=np.float64)


def _ssim(a: np.ndarray, b: np.ndarray) -> float:
    try:
        from skimage.metrics import structural_similarity
        return float(structural_similarity(a, b, data_range=255))
    except ImportError:  # simple global SSIM if scikit-image is missing
        c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
        mu_a, mu_b = a.mean(), b.mean()
        cov = ((a - mu_a) * (b - mu_b)).mean()
        return float(((2 * mu_a * mu_b + c1) * (2 * cov + c2)) /
                     ((mu_a ** 2 + mu_b ** 2 + c1) * (a.var() + b.var() + c2)))


def verify_action(before: ImageLike, after: ImageLike,
                  target_bbox: Optional[Sequence[float]] = None) -> dict:
    start = time.perf_counter()
    img_a, img_b = _load(before), _load(after)
    orig_w, orig_h = img_a.size
    scale = COMPARE_WIDTH / orig_w if orig_w > COMPARE_WIDTH else 1.0
    size = (max(1, int(orig_w * scale)), max(1, int(orig_h * scale)))
    a, b = _gray_small(img_a, size), _gray_small(img_b, size)   # "after" is resized to "before"

    diff_mask = np.abs(a - b) > PIXEL_THRESHOLD
    changed_fraction = float(diff_mask.mean())
    ssim = _ssim(a, b)
    changed = changed_fraction >= MIN_CHANGED_FRACTION or ssim < SSIM_CHANGED_BELOW

    changed_bbox = None
    if diff_mask.any():
        ys, xs = np.nonzero(diff_mask)
        x0, x1, y0, y1 = xs.min() / scale, (xs.max() + 1) / scale, ys.min() / scale, (ys.max() + 1) / scale
        changed_bbox = [int(x0), int(y0), int(x1 - x0), int(y1 - y0)]

    target_changed = None
    if target_bbox is not None:
        x, y, w, h = target_bbox
        pad = 20  # look a little around the element too
        x0 = max(0, int((x - pad) * scale)); y0 = max(0, int((y - pad) * scale))
        x1 = min(size[0], int((x + w + pad) * scale) + 1); y1 = min(size[1], int((y + h + pad) * scale) + 1)
        region = diff_mask[y0:y1, x0:x1]
        target_changed = bool(region.size and region.mean() >= MIN_CHANGED_FRACTION)

    return {
        "changed": bool(changed),
        "changed_fraction": round(changed_fraction, 4),
        "ssim": round(ssim, 4),
        "changed_bbox": changed_bbox,
        "target_changed": target_changed,
        "ms": round((time.perf_counter() - start) * 1000, 1),
    }


# Alias with the wording used in the plan
compare_screenshots = verify_action


def verify_with_vlm(after: ImageLike, expected: str) -> dict:
    """Optional second opinion from the local VLM: 'Does the page now show <expected>?'"""
    from models.vlm_client import ask_vlm
    answer = ask_vlm(after, f"Look at this web page. Does it show: {expected}? Answer only YES or NO.",
                     max_tokens=5, temperature=0.0)
    return {"vlm_says_yes": answer.strip().upper().startswith("YES"), "raw": answer}
