from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
import subprocess
import sys
import os
from pathlib import Path

# Get the directory where this script is located
UTILS_DIR = Path(__file__).parent
ROOT_DIR = UTILS_DIR.parent

client = OpenAI()

def read_text_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Could not find file {filename}")
        print(f"Please make sure the file exists in {ROOT_DIR}")
        sys.exit(1)

def extract_text_from_pdf(pdf_path):
    try:
        subprocess.run(
            ["python3", str(UTILS_DIR / "extract_text.py"), pdf_path],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running extract_text.py: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python process_with_openai.py <path_to_pdf>")
        sys.exit(1)
    pdf_path = sys.argv[1]

    # Check if required files exist
    prompt_file = ROOT_DIR / "prompt.txt"
    if not prompt_file.exists():
        print(f"Error: prompt.txt not found in {ROOT_DIR}")
        print("Please make sure prompt.txt exists in the backend directory")
        sys.exit(1)

    extract_text_from_pdf(pdf_path)
    
    # Check if text.text was created
    text_file = ROOT_DIR / "text.text"
    if not text_file.exists():
        print(f"Error: text.text not found in {ROOT_DIR}")
        print("The text extraction process may have failed")
        sys.exit(1)

    text = read_text_file(text_file)
    prompt = read_text_file(prompt_file)

    # Combine prompt and text for the user message
    user_message = prompt + "\n\n" + text

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        output_file = ROOT_DIR / "output.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(response.choices[0].message.content)
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        sys.exit(1)
    