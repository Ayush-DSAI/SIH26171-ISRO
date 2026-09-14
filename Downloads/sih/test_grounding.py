# perception/test_grounding.py
from grounding import ground_element

def run_test():
    # Test ground_element with a dummy screenshot path
    result = ground_element("test_pages/login_form.html", "Login button")
    
    print("--- Grounding Module Test Output ---")
    print(result)
    
    assert result["bbox"] is not None, "Error: Bounding box parsing failed!"
    print("SUCCESS: Grounding function works as expected!")

if __name__ == "__main__":
    run_test()