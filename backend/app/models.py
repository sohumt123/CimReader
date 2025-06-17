from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CIMSummary(BaseModel):
    id: Optional[str] = None
    user_id: str
    original_filename: str
    summary_pdf_url: str
    created_at: Optional[datetime] = None
    title: str

class User(BaseModel):
    id: str
    email: str
    created_at: Optional[datetime] = None 