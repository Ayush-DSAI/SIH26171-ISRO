# perception/benchmark.py
import os
import sys

# Ensure Python can find modules in the root folder and perception folder
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from grounding import ground_element
except ModuleNotFoundError:
    from perception.grounding import ground_element


def run_benchmark():
    # Test scenarios across test pages
    test_cases = [
        {"page": "test_login.html", "element": "Login button"},
        {"page": "test_login.html", "element": "Password field"},
        {"page": "search_page.html", "element": "Search button"},
        {"page": "search_page.html", "element": "Footer link"},
    ]

    results = []

    print("--- Running Grounding Benchmark ---")
    for test in test_cases:
        res = ground_element(test["page"], test["element"])
        passed = "PASS" if res["bbox"] is not None else "FAIL"
        results.append(
            {
                "page": test["page"],
                "element": test["element"],
                "bbox": str(res["bbox"]),
                "status": passed,
            }
        )
        print(
            f"[{passed}] {test['page']} -> '{test['element']}': BBox={res['bbox']}"
        )

    # Write Markdown table for Day 8 output
    os.makedirs("results", exist_ok=True)
    with open("results/grounding_accuracy.md", "w") as f:
        f.write("# Grounding Accuracy Benchmark\n\n")
        f.write(
            "| Test Page | Target Element | Predicted BBox [x,y,w,h] | Status"
            " |\n"
        )
        f.write("| :--- | :--- | :--- | :--- |\n")
        for r in results:
            f.write(
                f"| {r['page']} | {r['element']} | {r['bbox']} | {r['status']}"
                " |\n"
            )

    print("\nBenchmark saved to results/grounding_accuracy.md!")


if __name__ == "__main__":
    run_benchmark()