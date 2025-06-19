from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Header
from fastapi.responses import FileResponse
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
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "CIMez API is running"}

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
    """Synchronous HTML to PDF conversion to avoid async context issues"""
    try:
        # Check if HTML file exists
        if not os.path.exists(html_file_path):
            return {
                "success": False,
                "error": f"HTML file not found: {html_file_path}",
                "message": f"HTML file not found: {html_file_path}"
            }
        
        # Verify Playwright can launch browser
        try:
            with sync_playwright() as p:
                # Find the correct Chromium executable path
                import glob
                chromium_paths = glob.glob("/Users/sohumtrivedi/Library/Caches/ms-playwright/chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium")
                chromium_path = chromium_paths[0] if chromium_paths else None
                
                logger.info(f"Available Chromium paths: {chromium_paths}")
                logger.info(f"Using Chromium path: {chromium_path}")
                
                # Try to launch browser with explicit executable path
                launch_options = {
                    "headless": True,
                    "args": [
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor'
                    ]
                }
                
                if chromium_path and os.path.exists(chromium_path):
                    launch_options["executable_path"] = chromium_path
                
                browser = p.chromium.launch(**launch_options)
                page = browser.new_page()
                
                # Use absolute path for file URL
                abs_html_path = "file://" + os.path.abspath(html_file_path)
                logger.info(f"Loading HTML from: {abs_html_path}")
                
                page.goto(abs_html_path, wait_until='networkidle', timeout=30000)
                
                # Wait a moment for content to load
                page.wait_for_timeout(2000)
                
                # Generate PDF
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
                browser.close()
                
        except Exception as browser_error:
            return {
                "success": False,
                "error": str(browser_error),
                "error_type": str(type(browser_error)),
                "message": f"Browser error: {str(browser_error)}"
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
    """Debug endpoint to test summaries fetch"""
    try:
        logger.info(f"Debug summaries - User: {current_user}")
        logger.info(f"Debug summaries - User ID: {current_user.id}")
        logger.info(f"Debug summaries - User ID type: {type(current_user.id)}")
        
        # Test the sync database fetch
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(sync_database_fetch, current_user.id)
            db_result = future.result(timeout=30)
        
        return {
            "user_id": current_user.id,
            "fetch_result": db_result
        }
    except Exception as e:
        logger.error(f"Debug summaries error: {str(e)}")
        return {
            "error": str(e),
            "error_type": str(type(e))
        }

@app.post("/convert-pdf")
async def convert_pdf(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    logger.info(f"Current user: {current_user}")
    logger.info(f"Current user ID: {current_user.id if hasattr(current_user, 'id') else 'No ID attribute'}")
    try:
        # Create a temporary file to store the uploaded PDF
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        try:
            # Write the uploaded file to the temporary file
            content = await file.read()
            temp_file.write(content)
            temp_file.close()

            # Process the PDF with OpenAI
            try:
                logger.info("Starting OpenAI processing...")
                result = subprocess.run(
                    ["python3", str(UTILS_DIR / "process_with_openai.py"), temp_file.name],
                    check=True,
                    capture_output=True,
                    text=True,
                    cwd=str(ROOT_DIR),
                    env=os.environ.copy()
                )
                logger.info(f"OpenAI processing stdout: {result.stdout}")
                if result.stderr:
                    logger.warning(f"OpenAI processing stderr: {result.stderr}")
                
                # Read the extracted text content for storage
                extracted_text = ""
                text_file_path = ROOT_DIR / "text.text"
                if os.path.exists(text_file_path):
                    with open(text_file_path, "r", encoding="utf-8") as f:
                        extracted_text = f.read()
                    logger.info(f"Read {len(extracted_text)} characters of extracted text")
                else:
                    logger.warning("text.text file not found after processing")
                    
            except subprocess.CalledProcessError as e:
                logger.error(f"Error in OpenAI processing: {e.stderr}")
                logger.error(f"Command output: {e.stdout}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error in OpenAI processing: {e.stderr}"
                )

            # Convert HTML to PDF using thread executor
            try:
                logger.info("Converting HTML to PDF...")
                output_pdf_path = f"output_{uuid.uuid4()}.pdf"
                html_file_path = "output.html"
                
                # Check if HTML file exists before attempting conversion
                if not os.path.exists(html_file_path):
                    raise FileNotFoundError(f"HTML file not found: {html_file_path}")
                
                logger.info(f"HTML file found: {html_file_path}")
                
                # Use thread executor to run Playwright synchronously
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(sync_html_to_pdf, output_pdf_path, html_file_path)
                    pdf_result = future.result(timeout=60)  # 60 second timeout for PDF generation
                
                if not pdf_result["success"]:
                    logger.error(f"PDF conversion failed: {pdf_result['message']}")
                    if 'error' in pdf_result:
                        logger.error(f"PDF conversion error: {pdf_result['error']}")
                    raise Exception(pdf_result["message"])
                
                logger.info(f"Successfully converted HTML to PDF: {output_pdf_path} (size: {pdf_result.get('pdf_size', 'unknown')} bytes)")
                
                # Read the generated PDF
                if not os.path.exists(output_pdf_path):
                    raise FileNotFoundError(f"PDF not found after conversion: {output_pdf_path}")
                
                with open(output_pdf_path, "rb") as f:
                    pdf_content = f.read()
                
                logger.info(f"Successfully read {len(pdf_content)} bytes from PDF")
                
            except Exception as e:
                logger.error(f"Error converting HTML to PDF: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error converting HTML to PDF: {str(e)}"
                )

            # Store the PDF in Supabase Storage
            try:
                # Create a unique filename
                filename = f"{uuid.uuid4()}.pdf"
                logger.info(f"Storing PDF with filename: {filename}")
                
                # Upload to Supabase Storage
                try:
                    storage_client = supabase.storage.from_("summaries")
                    storage_response = storage_client.upload(
                        f"{current_user.id}/{filename}",
                        pdf_content,
                        {"content-type": "application/pdf"}
                    )
                except AttributeError as e:
                    logger.error(f"Storage API error: {e}")
                    # Try alternative storage access
                    storage_response = supabase.storage().from_("summaries").upload(
                        f"{current_user.id}/{filename}",
                        pdf_content,
                        {"content-type": "application/pdf"}
                    )
                
                if not storage_response:
                    raise Exception("Failed to upload to storage")
                
                logger.info("Successfully uploaded to Supabase storage")

                # Get the public URL
                try:
                    public_url_response = supabase.storage.from_("summaries").get_public_url(f"{current_user.id}/{filename}")
                    # Handle both cases: when it returns a string directly or an object with .data
                    if isinstance(public_url_response, str):
                        public_url = public_url_response
                    else:
                        public_url = public_url_response.data
                except AttributeError:
                    public_url_response = supabase.storage().from_("summaries").get_public_url(f"{current_user.id}/{filename}")
                    if isinstance(public_url_response, str):
                        public_url = public_url_response
                    else:
                        public_url = public_url_response.data
                logger.info(f"Generated public URL: {public_url}")

                # Store metadata in the summaries table
                # Note: Only include extracted_text if the column exists in the database
                summary_data = {
                    "user_id": current_user.id,
                    "original_filename": file.filename,
                    "summary_pdf_url": public_url,
                    "title": f"Summary of {file.filename}",
                    "created_at": datetime.utcnow().isoformat()
                }
                
                # Add extracted_text separately so we can handle column not existing
                if extracted_text:
                    summary_data["extracted_text"] = extracted_text
                
                logger.info("Storing summary metadata...")
                logger.info(f"Summary data to insert: {summary_data}")
                
                # Use thread executor to run database insert synchronously
                logger.info("Running database insert in thread executor to avoid async context issues...")
                logger.info(f"Summary data: {summary_data}")
                logger.info(f"User ID type: {type(current_user.id)}")
                logger.info(f"User ID value: {current_user.id}")
                
                # Run the synchronous database insert in a thread pool
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(sync_database_insert, summary_data)
                    db_result = future.result(timeout=30)  # 30 second timeout
                
                logger.info(f"Database insert result: {db_result}")
                
                if not db_result["success"]:
                    logger.error(f"Database insert failed: {db_result['message']}")
                    logger.error(f"Error type: {db_result.get('error_type', 'unknown')}")
                    
                    # Check if it's a UUID error
                    if "invalid input syntax for type uuid" in str(db_result.get("error", "")):
                        logger.error(f"UUID format error - user_id: {current_user.id}")
                        raise Exception(f"Invalid user ID format: {current_user.id}")
                    
                    # Check if it's an extracted_text column error - try without it
                    if "extracted_text" in str(db_result.get("error", "")) and "column" in str(db_result.get("error", "")):
                        logger.warning("extracted_text column not found, trying insert without it...")
                        summary_data_without_text = {k: v for k, v in summary_data.items() if k != 'extracted_text'}
                        
                        with ThreadPoolExecutor(max_workers=1) as executor:
                            future = executor.submit(sync_database_insert, summary_data_without_text)
                            retry_result = future.result(timeout=30)
                        
                        if not retry_result["success"]:
                            raise Exception(retry_result["message"])
                        
                        logger.info("Successfully stored summary without extracted_text")
                        db_result = retry_result  # Use the successful result
                    else:
                        raise Exception(db_result["message"])
                
                logger.info("Successfully stored summary metadata")
                db_response_data = db_result["data"]

                return {
                    "message": "PDF processed successfully",
                    "summary_id": db_response_data["id"],
                    "public_url": public_url
                }

            except Exception as e:
                logger.error(f"Error storing summary: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error storing summary: {str(e)}"
                )

        finally:
            # Clean up the temporary file
            os.unlink(temp_file.name)
            # Clean up the output files
            for file_to_remove in ["text.text", "output.html"]:
                if os.path.exists(file_to_remove):
                    os.remove(file_to_remove)
            # Clean up the generated PDF
            if 'output_pdf_path' in locals() and os.path.exists(output_pdf_path):
                os.remove(output_pdf_path)

    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(e)}"
        )

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