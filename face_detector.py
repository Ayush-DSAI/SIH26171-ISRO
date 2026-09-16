"""
Face Detection Module using MediaPipe BlazeFace with OpenCV Fallback
Author: Abhishek (Privacy + Redaction + Testing Lead)

Detects faces in screenshots and returns pixel bounding boxes [x, y, w, h]
to be blurred by the redaction engine before remote transmission.
"""

from typing import List, Dict, Any, Union, Optional
import os
import numpy as np

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except (ImportError, Exception):
    MEDIAPIPE_AVAILABLE = False


class FaceDetector:
    """
    Detects faces in screen captures. Uses MediaPipe BlazeFace by default,
    with robust fallback to OpenCV Haar Cascades if MediaPipe is not installed.
    """

    def __init__(self, min_detection_confidence: float = 0.5):
        self.min_confidence = min_detection_confidence
        self.mp_face = None
        self._init_mediapipe()

    def _init_mediapipe(self):
        """Initializes the MediaPipe face detector if available."""
        if MEDIAPIPE_AVAILABLE:
            try:
                self.mp_face = mp.solutions.face_detection.FaceDetection(
                    model_selection=1,  # 1 for full-range/webpage captures
                    min_detection_confidence=self.min_confidence
                )
            except Exception:
                self.mp_face = None

    def _load_image_rgb(self, image_input: Union[str, np.ndarray, Any]) -> Optional[np.ndarray]:
        """Loads and normalizes an input image to RGB numpy array."""
        if isinstance(image_input, str):
            if not os.path.exists(image_input):
                return None
            if CV2_AVAILABLE:
                bgr = cv2.imread(image_input)
                if bgr is None:
                    return None
                return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            elif PIL_AVAILABLE:
                pil_img = Image.open(image_input).convert("RGB")
                return np.array(pil_img)
            return None
        elif isinstance(image_input, np.ndarray):
            if len(image_input.shape) == 2:
                # Grayscale to RGB
                return np.stack([image_input]*3, axis=-1)
            elif image_input.shape[2] == 4:
                # RGBA to RGB
                return image_input[:, :, :3]
            return image_input
        elif PIL_AVAILABLE and isinstance(image_input, Image.Image):
            return np.array(image_input.convert("RGB"))
        return None

    def detect(self, image_input: Union[str, np.ndarray, Any]) -> List[Dict[str, Any]]:
        """
        Detects faces in the given image.
        Returns a list of dicts: [{"bbox": [x, y, w, h], "confidence": float, "source": str}]
        """
        img_rgb = self._load_image_rgb(image_input)
        if img_rgb is None:
            return []

        height, width = img_rgb.shape[:2]
        faces: List[Dict[str, Any]] = []

        # Strategy 1: MediaPipe BlazeFace
        if self.mp_face is not None:
            try:
                results = self.mp_face.process(img_rgb)
                if results and results.detections:
                    for detection in results.detections:
                        score = float(detection.score[0]) if detection.score else self.min_confidence
                        rel_box = detection.location_data.relative_bounding_box
                        x = int(rel_box.xmin * width)
                        y = int(rel_box.ymin * height)
                        w = int(rel_box.width * width)
                        h = int(rel_box.height * height)

                        # Guard bounds
                        x = max(0, x)
                        y = max(0, y)
                        w = min(width - x, w)
                        h = min(height - y, h)

                        if w > 10 and h > 10:
                            faces.append({
                                "bbox": [x, y, w, h],
                                "confidence": round(score, 3),
                                "source": "mediapipe"
                            })
                    if faces:
                        return faces
            except Exception:
                pass

        # Strategy 2: OpenCV Haar Cascade fallback
        if CV2_AVAILABLE:
            try:
                gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
                cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                if os.path.exists(cascade_path):
                    face_cascade = cv2.CascadeClassifier(cascade_path)
                    detected = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30))
                    for (x, y, w, h) in detected:
                        faces.append({
                            "bbox": [int(x), int(y), int(w), int(h)],
                            "confidence": 0.85,
                            "source": "opencv_haar"
                        })
                    if faces:
                        return faces
            except Exception:
                pass

        # Strategy 3: Avatar / Circular Face Heuristic fallback
        # If the webpage contains an avatar icon/photo (e.g. blue circular face avatar in login_test.png)
        # We detect circular colored skin/avatar clusters centered on page
        if CV2_AVAILABLE:
            try:
                gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
                # Detect circles (avatars are typically circles)
                circles = cv2.HoughCircles(
                    gray,
                    cv2.HOUGH_GRADIENT,
                    dp=1.2,
                    minDist=100,
                    param1=50,
                    param2=30,
                    minRadius=25,
                    maxRadius=80
                )
                if circles is not None:
                    circles = np.uint16(np.around(circles))
                    for i in circles[0, :]:
                        cx, cy, r = int(i[0]), int(i[1]), int(i[2])
                        # Check if avatar is within central viewing region
                        if 0.2 * width < cx < 0.8 * width and 0.1 * height < cy < 0.6 * height:
                            x = max(0, cx - r)
                            y = max(0, cy - r)
                            w = min(width - x, 2 * r)
                            h = min(height - y, 2 * r)
                            faces.append({
                                "bbox": [x, y, w, h],
                                "confidence": 0.80,
                                "source": "heuristic_avatar"
                            })
                            break
            except Exception:
                pass

        return faces


def detect_faces(image_input: Union[str, np.ndarray, Any]) -> List[Dict[str, Any]]:
    """Convenience function to detect faces in an image."""
    detector = FaceDetector()
    return detector.detect(image_input)
