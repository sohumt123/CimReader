from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CIMSummary(BaseModel):
    id: Optional[str] = None
    user_id: str
    original_filename: str
    summary_pdf_url: str
    title: str
    extracted_text: Optional[str] = None  # Store the original PDF text content
    created_at: Optional[datetime] = None

class User(BaseModel):
    id: str
    email: str
    created_at: Optional[datetime] = None

class ChatRequest(BaseModel):
    question: str
    document_id: str 