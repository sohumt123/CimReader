# PDF Processor Backend

This is the backend service for the PDF processing application. It provides APIs for processing PDF files and extracting text and images.

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

## Running the Server

To start the development server:

```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

## API Endpoints

- `POST /api/process-pdf`: Upload and process a PDF file
  - Accepts multipart/form-data with a PDF file
  - Returns processed text and images for each page

- `GET /api/health`: Health check endpoint
  - Returns server status

## API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc` 