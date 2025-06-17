import sys
import subprocess
import os
from playwright.sync_api import sync_playwright

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python html_to_pdf.py <path_to_pdf> <output.pdf>")
        exit(1)
    pdf_input = sys.argv[1]
    pdf_output = sys.argv[2]

    # Call process_with_openai.py to generate output.html
    subprocess.run(
        ["python3", "process_with_openai.py", pdf_input],
        check=True
    )

    # Use Playwright to convert output.html to PDF
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        abs_html_path = "file://" + os.path.abspath("output.html")
        page.goto(abs_html_path)
        page.pdf(path=pdf_output)
        browser.close()