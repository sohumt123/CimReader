from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Header
from fastapi.responses import FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import os
import uuid
import logging
import traceback
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
from pathlib import Path
from typing import List, Optional
from .models import CIMSummary, ChatRequest
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import tempfile
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Debug logging for environment variables
logger.info("Current working directory: %s", os.getcwd())
logger.info("SUPABASE_URL: %s", os.getenv("SUPABASE_URL"))
logger.info("SUPABASE_SERVICE_KEY: %s", os.getenv("SUPABASE_SERVICE_KEY"))

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL", "")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY", "")

if not supabase_url or not supabase_key:
    logger.error("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment variables")
    raise ValueError("Missing Supabase configuration")

supabase: Client = create_client(supabase_url, supabase_key)

# Get the project root directory
ROOT_DIR = Path(__file__).parent.parent
UTILS_DIR = ROOT_DIR / "utils"

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # React dev server (Vite default)
        "http://localhost:5173",   # Alternative Vite port
        "https://cim-reader.vercel.app",  # Your specific Vercel deployment
        "https://cim-reader.vercel.app/", # With trailing slash
        "https://vercel.app",       # Vercel base domain
        "https://cimreader.onrender.com",  # Allow backend to call itself
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "CIMez API is running"}

@app.options("/{rest_of_path:path}")
async def preflight_handler(request, rest_of_path: str):
    response = Response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response

@app.get("/health")
async def health_check():
    try:
        # Test Supabase connection
        test_response = supabase.table("summaries").select("count", count="exact").execute()
        return {
            "status": "healthy", 
            "message": "API is working",
            "supabase_connection": "working",
            "summaries_count": test_response.count if hasattr(test_response, 'count') else "unknown"
        }
    except Exception as e:
        return {
            "status": "healthy", 
            "message": "API is working",
            "supabase_connection": "error",
            "supabase_error": str(e)
        }

def sync_html_to_pdf(output_pdf_path: str, html_file_path: str = "output.html") -> dict:
    """Synchronous HTML to PDF conversion using Playwright"""
    try:
        # Check if HTML file exists
        if not os.path.exists(html_file_path):
            return {
                "success": False,
                "error": f"HTML file not found: {html_file_path}",
                "message": f"HTML file not found: {html_file_path}"
            }
        
        logger.info(f"Converting HTML to PDF: {html_file_path} -> {output_pdf_path}")
        
        # Use Playwright to convert HTML to PDF
        try:
            with sync_playwright() as p:
                # Debug: Show what executable Playwright is trying to use
                try:
                    executable_path = p.chromium.executable_path
                    logger.info(f"Playwright Chromium executable: {executable_path}")
                    logger.info(f"Executable exists: {os.path.exists(executable_path)}")
                except Exception as e:
                    logger.warning(f"Could not get Chromium executable path: {e}")
                
                # Debug: Show environment variables
                logger.info(f"PLAYWRIGHT_BROWSERS_PATH: {os.getenv('PLAYWRIGHT_BROWSERS_PATH', 'Not set')}")
                
                # Debug: Try to find any Chromium installations
                import glob
                search_patterns = [
                    "/opt/render/.cache/ms-playwright/chromium-*/chrome-linux/chrome",
                    "/opt/render/.cache/ms-playwright/*/chrome-linux/chrome",
                    "/usr/bin/chromium*",
                    "/usr/bin/google-chrome*"
                ]
                
                for pattern in search_patterns:
                    matches = glob.glob(pattern)
                    if matches:
                        logger.info(f"Found browsers at pattern {pattern}: {matches}")
                
                # Simple launch with minimal options for Render.com
                logger.info("Attempting to launch Chromium browser...")
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--single-process'
                    ]
                )
                logger.info("Browser launched successfully")
                
                page = browser.new_page()
                logger.info("New page created")
                
                # Use absolute path for file URL
                abs_html_path = "file://" + os.path.abspath(html_file_path)
                logger.info(f"Loading HTML from: {abs_html_path}")
                
                page.goto(abs_html_path, wait_until='networkidle', timeout=30000)
                logger.info("HTML page loaded successfully")
                
                # Generate PDF
                logger.info("Generating PDF...")
                page.pdf(
                    path=output_pdf_path, 
                    format='A4', 
                    print_background=True,
                    margin={
                        'top': '20px',
                        'bottom': '20px', 
                        'left': '20px',
                        'right': '20px'
                    }
                )
                logger.info("PDF generated successfully")
                
                browser.close()
                logger.info("Browser closed")
                
        except Exception as conversion_error:
            logger.error(f"Playwright conversion error: {str(conversion_error)}")
            return {
                "success": False,
                "error": str(conversion_error),
                "error_type": str(type(conversion_error)),
                "message": f"Playwright conversion error: {str(conversion_error)}"
            }
        
        # Verify PDF was created
        if not os.path.exists(output_pdf_path):
            return {
                "success": False,
                "error": f"PDF file was not created: {output_pdf_path}",
                "message": f"PDF file was not created: {output_pdf_path}"
            }
        
        pdf_size = os.path.getsize(output_pdf_path)
        logger.info(f"PDF created successfully with size: {pdf_size} bytes")
        
        return {
            "success": True,
            "message": "PDF conversion successful",
            "pdf_size": pdf_size
        }
        
    except Exception as e:
        logger.error(f"Unexpected error in PDF conversion: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "error_type": str(type(e)),
            "message": f"PDF conversion failed: {str(e)}"
        }

def sync_database_insert(summary_data: dict) -> dict:
    """Synchronous database insert using direct HTTP to avoid Supabase client issues"""
    try:
        import requests
        
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        url = f"{supabase_url}/rest/v1/summaries"
        response = requests.post(url, headers=headers, json=summary_data, timeout=30)
        
        if response.status_code == 201:
            response_data = response.json()
            if response_data:
                return {
                    "success": True,
                    "data": response_data[0],
                    "message": "Database insert successful"
                }
            else:
                raise Exception("No data returned from successful insert")
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": str(type(e)),
            "message": f"Database insert failed: {str(e)}"
        }

def sync_database_fetch(user_id: str) -> dict:
    """Synchronous database fetch using direct HTTP to avoid Supabase client issues"""
    try:
        import requests
        
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{supabase_url}/rest/v1/summaries"
        params = {"user_id": f"eq.{user_id}", "select": "*"}
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            response_data = response.json()
            return {
                "success": True,
                "data": response_data,
                "message": "Database fetch successful"
            }
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": str(type(e)),
            "message": f"Database fetch failed: {str(e)}"
        }

def sync_database_fetch_single(summary_id: str, user_id: str) -> dict:
    """Synchronous database fetch for a single summary using direct HTTP"""
    try:
        import requests
        
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{supabase_url}/rest/v1/summaries"
        params = {
            "id": f"eq.{summary_id}", 
            "user_id": f"eq.{user_id}",
            "select": "*"
        }
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            response_data = response.json()
            return {
                "success": True,
                "data": response_data,
                "message": "Database fetch successful"
            }
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": str(type(e)),
            "message": f"Database fetch failed: {str(e)}"
        }

def sync_database_delete(summary_id: str, user_id: str) -> dict:
    """Synchronous database delete using direct HTTP to avoid Supabase client issues"""
    try:
        import requests
        
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{supabase_url}/rest/v1/summaries"
        params = {
            "id": f"eq.{summary_id}", 
            "user_id": f"eq.{user_id}"
        }
        response = requests.delete(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 204:  # No content - successful delete
            return {
                "success": True,
                "message": "Database delete successful"
            }
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": str(type(e)),
            "message": f"Database delete failed: {str(e)}"
        }

def sync_storage_delete(storage_path: str) -> dict:
    """Synchronous storage delete using direct HTTP to avoid Supabase client issues"""
    try:
        import requests
        
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        
        # Try multiple API endpoints for storage deletion
        storage_urls = [
            f"{supabase_url}/storage/v1/object/summaries/{storage_path}",
            f"{supabase_url}/storage/v1/object/public/summaries/{storage_path}"
        ]
        
        last_error = None
        for url in storage_urls:
            logger.info(f"Attempting storage delete at URL: {url}")
            try:
                response = requests.delete(url, headers=headers, timeout=30)
                logger.info(f"Storage delete response: {response.status_code} - {response.text}")
                
                if response.status_code in [200, 204]:  # Success
                    return {
                        "success": True,
                        "message": f"Storage delete successful at {url}",
                        "status_code": response.status_code
                    }
                else:
                    last_error = f"HTTP {response.status_code}: {response.text}"
                    logger.warning(f"Storage delete failed at {url}: {last_error}")
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Storage delete exception at {url}: {last_error}")
        
        # If we get here, all attempts failed
        raise Exception(f"All storage delete attempts failed. Last error: {last_error}")
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": str(type(e)),
            "message": f"Storage delete failed: {str(e)}"
        }

async def get_current_user(authorization: Optional[str] = Header(None)):
    logger.info(f"get_current_user called with authorization: {authorization is not None}")
    
    if not authorization or not authorization.startswith("Bearer "):
        logger.error("Invalid authorization header format")
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    logger.info(f"Extracted token length: {len(token) if token else 0}")
    
    try:
        user_response = supabase.auth.get_user(token)
        logger.info(f"Auth response type: {type(user_response)}")
        logger.info(f"User object type: {type(user_response.user)}")
        logger.info(f"User ID: {user_response.user.id}")
        return user_response.user
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        logger.error(f"Authentication error type: {type(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/debug-auth")
async def debug_auth(current_user: dict = Depends(get_current_user)):
    """Debug endpoint to test authentication"""
    return {
        "user_object": str(current_user),
        "user_type": str(type(current_user)),
        "user_id": getattr(current_user, 'id', 'NO_ID_ATTRIBUTE'),
        "user_id_type": str(type(getattr(current_user, 'id', None))),
        "user_attributes": [attr for attr in dir(current_user) if not attr.startswith('_')]
    }

@app.get("/debug-summaries")
async def debug_summaries(current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user['id']
        # Fetch summaries for the user
        response = supabase.table("summaries").select("*").eq("user_id", user_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/convert-pdf")
async def convert_pdf(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    This endpoint does the following:
    1.  Receives a PDF file.
    2.  Runs an external Python script (`process_with_openai.py`) to:
        a. Extract text from the PDF.
        b. Send the text to OpenAI for processing (summarization, etc.).
        c. Save the result as an HTML file (`output.html`).
    3.  Converts the resulting `output.html` to a new PDF.
    4.  Stores this new PDF in Supabase Storage.
    5.  Stores metadata about the summary in the Supabase `summaries` table.
    6.  Returns the public URL of the stored PDF and its summary ID.
    """
    user_id = current_user.get('id')
    if not user_id:
        raise HTTPException(status_code=401, detail="Could not verify user.")

    # Use a temporary directory for all file operations
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        original_pdf_path = temp_dir_path / file.filename
        
        # Save the uploaded PDF to the temp directory
        with open(original_pdf_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Define paths for output files
        output_html_path = Path("output.html") # Script writes to project root
        output_pdf_path = temp_dir_path / f"output_{uuid.uuid4()}.pdf"
        
        # --- Run the OpenAI processing script ---
        script_path = UTILS_DIR / "process_with_openai.py"
        process = None
        try:
            # We run this in a separate process to handle its dependencies and environment
            logger.info(f"Running OpenAI processing script for: {original_pdf_path}")
            process = await asyncio.create_subprocess_exec(
                "python", str(script_path), str(original_pdf_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error("OpenAI processing script failed.")
                logger.error(f"Stderr: {stderr.decode()}")
                raise HTTPException(status_code=500, detail=f"Failed to process PDF with OpenAI: {stderr.decode()}")
            
            logger.info(f"OpenAI processing script stdout: {stdout.decode()}")
            if stderr:
                logger.warning(f"OpenAI processing stderr: {stderr.decode()}")
        
        except Exception as e:
            logger.error(f"Error executing subprocess: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        
        # --- Convert the resulting HTML to PDF ---
        logger.info("Converting HTML to PDF...")
        conversion_result = sync_html_to_pdf(
            output_pdf_path=str(output_pdf_path),
            html_file_path=str(output_html_path)
        )
        
        if not conversion_result.get("success"):
            logger.error(f"HTML to PDF conversion failed: {conversion_result.get('error')}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to convert summary to PDF: {conversion_result.get('error')}"
            )
        
        logger.info(f"Successfully converted HTML to PDF: {output_pdf_path} (size: {conversion_result.get('pdf_size')})")
        
        # --- Store PDF in Supabase Storage and metadata in DB ---
        storage_filename = f"{uuid.uuid4()}.pdf"
        storage_file_path = f"{user_id}/{storage_filename}"
        public_url = None
        
        try:
            # Read the generated PDF content
            with open(output_pdf_path, 'rb') as f:
                pdf_content = f.read()
            logger.info(f"Read {len(pdf_content)} bytes from generated PDF.")
            
            # 1. Upload to Storage
            logger.info(f"Uploading to Supabase Storage at path: {storage_file_path}")
            supabase.storage.from_("summaries").upload(
                path=storage_file_path,
                file=pdf_content,
                file_options={"content-type": "application/pdf"}
            )
            logger.info("Successfully uploaded to Supabase storage.")

            # 2. Get Public URL
            public_url = supabase.storage.from_("summaries").get_public_url(storage_file_path)
            logger.info(f"Generated public URL: {public_url}")

            # 3. Store Metadata in Database
            summary_data = {
                "user_id": user_id,
                "original_filename": file.filename,
                "summary_pdf_url": public_url,
                "storage_path": storage_file_path,
                "title": f"Summary for {file.filename}",
                "created_at": datetime.utcnow().isoformat()
            }
            
            logger.info("Inserting summary metadata into database...")
            db_response = sync_database_insert(summary_data)
            
            if not db_response.get("success"):
                raise Exception(f"Database insert failed: {db_response.get('error')}")

            db_response_data = db_response.get("data", {})
            logger.info("Successfully stored summary metadata.")
            
            return {
                "message": "PDF processed successfully",
                "summary_id": db_response_data.get("id"),
                "public_url": public_url
            }

        except Exception as e:
            logger.error(f"An error occurred during Supabase operation: {str(e)}")
            # Attempt to clean up the uploaded file if the DB insert fails
            if public_url:
                logger.info(f"Attempting to clean up failed upload at: {storage_file_path}")
                sync_storage_delete(storage_file_path)
            raise HTTPException(status_code=500, detail=f"Storage or database error: {str(e)}")
        finally:
            # Clean up the local output.html file
            if os.path.exists(output_html_path):
                os.remove(output_html_path)

@app.get("/summaries", response_model=List[CIMSummary])
async def get_summaries(user = Depends(get_current_user)):
    try:
        logger.info(f"Fetching summaries for user: {user.id}")
        
        # Use thread executor to run database fetch synchronously
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(sync_database_fetch, user.id)
            db_result = future.result(timeout=30)  # 30 second timeout
        
        if not db_result["success"]:
            logger.error(f"Database fetch failed: {db_result['message']}")
            if 'error' in db_result:
                logger.error(f"Database fetch error: {db_result['error']}")
            raise Exception(db_result["message"])
        
        logger.info(f"Successfully fetched {len(db_result['data'])} summaries")
        return db_result["data"]
        
    except Exception as e:
        logger.error(f"Error fetching summaries: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/summaries/{summary_id}")
async def delete_summary(summary_id: str, user = Depends(get_current_user)):
    try:
        logger.info(f"Deleting summary {summary_id} for user {user.id}")
        
        # Get the summary to find the PDF path using thread executor
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(sync_database_fetch_single, summary_id, user.id)
            fetch_result = future.result(timeout=30)
        
        if not fetch_result["success"]:
            logger.error(f"Failed to fetch summary for deletion: {fetch_result['message']}")
            raise Exception(fetch_result["message"])
        
        if not fetch_result["data"]:
            logger.warning(f"Summary {summary_id} not found for user {user.id}")
            raise HTTPException(status_code=404, detail="Summary not found")
        
        summary = fetch_result["data"][0]
        logger.info(f"Found summary to delete: {summary['title']}")
        
        # Delete the PDF from storage
        # Extract the storage path from the summary_pdf_url
        # The URL format is typically: https://...supabase.co/storage/v1/object/public/summaries/{user_id}/{filename}
        pdf_url = summary["summary_pdf_url"]
        logger.info(f"Attempting to extract storage path from URL: {pdf_url}")
        
        url_parts = pdf_url.split("/")
        logger.info(f"URL parts: {url_parts}")
        
        # Find the 'summaries' part in the URL and get everything after it
        storage_path = None
        try:
            summaries_index = url_parts.index("summaries")
            if summaries_index < len(url_parts) - 1:
                # Get everything after 'summaries' - should be user_id/filename
                storage_path = "/".join(url_parts[summaries_index + 1:])
                logger.info(f"Extracted storage path: {storage_path}")
        except ValueError:
            logger.error(f"Could not find 'summaries' in URL parts: {url_parts}")
        
        if storage_path:
            logger.info(f"Deleting storage file: {storage_path}")
            
            # Delete from storage using thread executor
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(sync_storage_delete, storage_path)
                storage_result = future.result(timeout=30)
            
            logger.info(f"Storage deletion result: {storage_result}")
            
            if not storage_result["success"]:
                logger.warning(f"Failed to delete storage file: {storage_result['message']}")
                # Continue with database deletion even if storage fails
            else:
                logger.info(f"Successfully deleted storage file: {storage_path}")
        else:
            logger.warning(f"Could not extract storage path from URL: {pdf_url}")
        
        # Delete the summary record using thread executor
        logger.info("Deleting summary from database")
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(sync_database_delete, summary_id, user.id)
            delete_result = future.result(timeout=30)
        
        if not delete_result["success"]:
            logger.error(f"Failed to delete summary from database: {delete_result['message']}")
            raise Exception(delete_result["message"])
        
        logger.info(f"Successfully deleted summary {summary_id}")
        return {"message": "Summary deleted successfully"}
        
    except HTTPException:
        raise  # Re-raise HTTPExceptions as-is
    except Exception as e:
        logger.error(f"Error deleting summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat-pdf")
async def chat_with_pdf(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Chat with a processed PDF document using the original PDF text content
    """
    try:
        logger.info(f"Chat request for document {request.document_id} by user {current_user.id}")
        
        # First, verify the user owns this document
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(sync_database_fetch_single, request.document_id, current_user.id)
            fetch_result = future.result(timeout=30)
        
        if not fetch_result["success"] or not fetch_result["data"]:
            logger.warning(f"Document {request.document_id} not found for user {current_user.id}")
            raise HTTPException(status_code=404, detail="Document not found")
        
        document = fetch_result["data"][0]
        logger.info(f"User verified for document: {document['title']}")
        
        # Get the extracted text content from the document
        extracted_text = document.get('extracted_text', '')
        if not extracted_text:
            logger.warning(f"No extracted text found for document {request.document_id} - falling back to basic mode")
            # Fall back to basic chat without document content
            system_prompt = f"""You are an AI assistant helping users understand a document titled "{document['title']}". 
            
            I apologize, but the full document content is not available for this document. This may be because it was processed before the text extraction feature was added.
            
            I can provide general assistance about the document based on its title and filename, but I cannot reference specific content.
            
            Document title: {document['title']}
            Original filename: {document['original_filename']}
            
            Please let me know how I can help you with this document."""
            
            truncated_text = ""  # No content available
        else:
            logger.info(f"Using {len(extracted_text)} characters of original document text for context")
            
            # Create a comprehensive prompt that includes the full document text
            # Truncate text if it's too long for the API (keep last part which is usually most relevant)
            max_context_length = 24000  # Leave room for question and system prompt
            if len(extracted_text) > max_context_length:
                # Keep the first part and last part of the document
                first_part = extracted_text[:max_context_length//2]
                last_part = extracted_text[-(max_context_length//2):]
                truncated_text = f"{first_part}\n\n[... middle content truncated ...]\n\n{last_part}"
                logger.info(f"Truncated document text from {len(extracted_text)} to {len(truncated_text)} characters")
            else:
                truncated_text = extracted_text
            
            system_prompt = f"""You are an AI assistant helping users understand a document titled "{document['title']}". 
            
            You have access to the FULL ORIGINAL TEXT CONTENT of this document below. Use this content to answer questions accurately and in detail.
            
            Be helpful, accurate, and specific. You can reference specific sections, quote relevant passages, and provide detailed explanations based on the document content.
            
            If the user asks about something not covered in the document, clearly state that the information is not available in this document.
            
            Document title: {document['title']}
            Original filename: {document['original_filename']}
            
                         DOCUMENT CONTENT:
             {truncated_text}
             """
        
        # Use OpenAI to answer the question about the document
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-4.1-nano",  # Use 16k model for longer context
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": request.question}]
              # Lower temperature for more accurate responses
            )
            
            answer = response.choices[0].message.content
            
        except Exception as openai_error:
            logger.error(f"OpenAI API error: {str(openai_error)}")
            # Fallback response if OpenAI fails
            answer = f"I'm sorry, but I'm having trouble accessing the AI service right now. However, I have access to the full content of '{document['title']}' (originally '{document['original_filename']}'). Please try again later or rephrase your question."
        
        logger.info(f"Generated response for question: {request.question[:50]}...")
        
        return {
            "answer": answer,
            "document_title": document['title'],
            "question": request.question
        }
        
    except HTTPException:
        raise  # Re-raise HTTPExceptions as-is
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 