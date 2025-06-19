from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
import subprocess
import sys
import os
import traceback
from pathlib import Path

# Get the directory where this script is located
UTILS_DIR = Path(__file__).parent
ROOT_DIR = UTILS_DIR.parent

# Set up logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if OpenAI API key is set
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.error("OPENAI_API_KEY environment variable is not set")
    sys.exit(1)
else:
    logger.info("OpenAI API key is set")

client = OpenAI()

def read_text_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"Could not find file {filename}")
        logger.error(f"Please make sure the file exists in {ROOT_DIR}")
        sys.exit(1)

def extract_text_from_pdf(pdf_path):
    try:
        logger.info(f"Extracting text from PDF: {pdf_path}")
        result = subprocess.run(
            ["python3", str(UTILS_DIR / "extract_text.py"), pdf_path],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info("Text extraction completed successfully")
        logger.debug(f"Extraction output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running extract_text.py: {e}")
        logger.error(f"Error output: {e.stderr}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Usage: python process_with_openai.py <path_to_pdf>")
        sys.exit(1)
    pdf_path = sys.argv[1]
    logger.info(f"Processing PDF: {pdf_path}")

    # Check if required files exist
    prompt_file = ROOT_DIR / "prompt.txt"
    if not prompt_file.exists():
        logger.error(f"prompt.txt not found in {ROOT_DIR}")
        logger.error("Please make sure prompt.txt exists in the backend directory")
        sys.exit(1)
    logger.info("Found prompt.txt")

    extract_text_from_pdf(pdf_path)
    
    # Check if text.text was created
    text_file = ROOT_DIR / "text.text"
    if not text_file.exists():
        logger.error(f"text.text not found in {ROOT_DIR}")
        logger.error("The text extraction process may have failed")
        sys.exit(1)
    logger.info("Found text.text")

    text = read_text_file(text_file)
    prompt = read_text_file(prompt_file)
    logger.info(f"Read {len(text)} characters from text.text")
    logger.info(f"Read {len(prompt)} characters from prompt.txt")

    # Combine prompt and text for the user message
    user_message = prompt + "\n\n" + text
    logger.info(f"Combined message length: {len(user_message)} characters")

    try:
        logger.info("Calling OpenAI API...")
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        logger.info("Received response from OpenAI API")

        if not response.choices or not response.choices[0].message.content:
            logger.error("No response content from OpenAI API")
            sys.exit(1)

        output_file = ROOT_DIR / "output.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(response.choices[0].message.content)
        logger.info(f"Wrote response to {output_file}")
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)
    