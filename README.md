# 📄 CIMez - AI-Powered PDF Intelligence Tool

A modern web application that transforms PDF documents into interactive, AI-powered summaries with intelligent chat capabilities.

## ✨ Features

- **🚀 PDF Processing**: Upload and automatically process PDF documents
- **🤖 AI Summarization**: Generate professional 2-page briefs using GPT-4
- **💬 Intelligent Chat**: Ask questions about your documents using the full original content
- **🎨 Modern UI**: Beautiful React frontend with Material-UI components  
- **🔐 Authentication**: Secure user authentication with Supabase
- **☁️ Cloud Storage**: Automatic document storage and management
- **📱 Responsive Design**: Works seamlessly on desktop and mobile

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│────│  FastAPI Backend│────│  Supabase DB    │
│   (TypeScript)  │    │    (Python)     │    │   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐             │
         └──────────────│  OpenAI GPT-4   │─────────────┘
                        │   (AI Engine)   │
                        └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+
- Supabase account
- OpenAI API key

### 1. Clone Repository
```bash
git clone <repository-url>
cd 4c-tool
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` file in backend directory:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
OPENAI_API_KEY=your_openai_api_key
```

Start backend server:
```bash
uvicorn app.main:app --reload
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

Create `.env` file in frontend directory:
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

Start frontend development server:
```bash
npm run dev
```

### 4. Database Setup
Add the following column to your Supabase `summaries` table:
```sql
ALTER TABLE summaries ADD COLUMN extracted_text TEXT;
```

## 📚 API Documentation

### Core Endpoints

- **POST** `/convert-pdf` - Upload and process PDF documents
- **GET** `/summaries` - Retrieve user's processed documents  
- **POST** `/chat-pdf` - Chat with document using AI
- **DELETE** `/summaries/{id}` - Delete processed document
- **GET** `/health` - Health check endpoint

### API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🛠️ Technology Stack

### Frontend
- **React 18** with TypeScript
- **Material-UI (MUI)** for components
- **Vite** for fast development
- **Supabase** for authentication

### Backend  
- **FastAPI** (Python) for REST API
- **PyMuPDF** for PDF text extraction
- **Playwright** for HTML to PDF conversion
- **OpenAI GPT-4** for AI processing
- **Supabase** for database and storage

### Infrastructure
- **Supabase** - Database, Authentication, File Storage
- **OpenAI** - AI language model integration

## 📖 How It Works

1. **Upload PDF**: Users upload PDF documents via the web interface
2. **Text Extraction**: System extracts text content using PyMuPDF
3. **AI Processing**: OpenAI GPT-4 generates professional summaries  
4. **PDF Generation**: Summaries are converted to formatted PDF files
5. **Storage**: Original text and summaries stored in Supabase
6. **Chat Interface**: Users can ask questions about document content
7. **AI Responses**: System provides detailed answers using full document context

## 🔧 Development

### Project Structure
```
4c-tool/
├── frontend/          # React TypeScript application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── contexts/      # React contexts  
│   │   └── lib/          # Utility functions
│   └── package.json
├── backend/           # FastAPI Python application  
│   ├── app/
│   │   ├── main.py       # FastAPI app entry point
│   │   └── models.py     # Pydantic models
│   ├── utils/            # Utility functions
│   └── requirements.txt
└── README.md
```

### Key Components
- **PDFConverter**: Handles PDF upload and processing
- **PDFChat**: Interactive chat interface for documents
- **SummaryHistory**: Displays processed document history
- **Authentication**: Supabase-powered user management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support  

If you encounter any issues or have questions, please open an issue on GitHub.

---

**Built with ❤️ using React, FastAPI, and OpenAI** 