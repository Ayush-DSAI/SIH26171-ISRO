# perception/grounding.py
import re

# Once Shaurya's server client is ready in the repo, uncomment the import below:
# from models.vlm_client import ask_vlm

def ground_element(image_path: str, description: str) -> dict:
    """
    Takes a screenshot image path and an element description.
    Returns the bounding box coordinates [x, y, w, h] and confidence score.
    """
    prompt = f"Locate the {description} on this page. Return bounding box as [x, y, w, h]."
    
    try:
        # 1. Call the local VLM server (uncomment when Shaurya's client is live)
        # raw_response = ask_vlm(image_path, prompt)
        
        # MOCK FALLBACK: Use this while testing locally so you aren't blocked
        raw_response = "The element is located at [342, 280, 120, 40]."
        
        # 2. Parse out [x, y, w, h] using regular expressions
        match = re.search(r'\[\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\]', raw_response)
        if match:
            bbox = [int(g) for g in match.groups()]
            return {
                "element": description,
                "bbox": bbox,
                "confidence": 0.90,
                "raw_response": raw_response
            }
    except Exception as e:
        pass

    # Fallback if no bounding box is detected
    return {
        "element": description,
        "bbox": None,
        "confidence": 0.0,
        "raw_response": raw_response if 'raw_response' in locals() else ""
    }