from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import os
import uuid
import logging
import traceback
from playwright.async_api import async_playwright
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the project root directory
ROOT_DIR = Path(__file__).parent.parent
UTILS_DIR = ROOT_DIR / "utils"

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/convert")
async def convert_pdf(file: UploadFile = File(...)):
    try:
        # Generate unique filenames
        input_pdf = ROOT_DIR / f"input_{uuid.uuid4()}.pdf"
        output_html = ROOT_DIR / "output.html"
        output_pdf = ROOT_DIR / f"output_{uuid.uuid4()}.pdf"
        
        logger.info(f"Starting conversion process for file: {file.filename}")
        
        # Save uploaded file
        try:
            with open(input_pdf, "wb") as f:
                content = await file.read()
                f.write(content)
        except Exception as e:
            error_msg = f"Error saving uploaded file: {str(e)}"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Process the PDF with OpenAI
        try:
            result = subprocess.run(
                ["python3", str(UTILS_DIR / "process_with_openai.py"), str(input_pdf)],
                check=True,
                capture_output=True,
                text=True
            )
            logger.info("OpenAI processing output: " + result.stdout)
        except subprocess.CalledProcessError as e:
            error_msg = f"Error in OpenAI processing: {e.stderr}"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Convert HTML to PDF using Playwright
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                abs_html_path = f"file://{output_html.absolute()}"
                await page.goto(abs_html_path)
                await page.pdf(path=str(output_pdf))
                await browser.close()
        except Exception as e:
            error_msg = f"Error in HTML to PDF conversion: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Clean up temporary files
        try:
            os.remove(input_pdf)
            os.remove(output_html)
        except Exception as e:
            logger.warning(f"Error cleaning up temporary files: {str(e)}")
        
        # Return the generated PDF
        return FileResponse(output_pdf, media_type="application/pdf", filename=output_pdf.name)
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg) 