# 4C Tool Backend

This directory contains the backend code for the 4C Tool application.

## Directory Structure

```
backend/
├── app/                    # Main application package
│   ├── __init__.py        # Package initialization
│   ├── main.py            # FastAPI application entry point
│   └── models.py          # Database models
├── utils/                  # Utility functions
│   ├── __init__.py        # Package initialization
│   ├── extract_text.py    # PDF text extraction utilities
│   ├── html_to_pdf.py     # HTML to PDF conversion utilities
│   └── process_with_openai.py  # OpenAI processing utilities
└── requirements.txt        # Python dependencies
```

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

The server will start at `http://localhost:8000`. 