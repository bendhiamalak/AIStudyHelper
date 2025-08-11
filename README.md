# AI Study Helper 📚

A powerful tool that processes PDF documents, generates quizzes from the content, and helps you study through interactive question-answering.

## Features ✨

- **PDF Processing**: Upload and extract text from PDF documents
- **Smart Chunking**: Intelligent text splitting for optimal content processing
- **Vector Embeddings**: Store document embeddings for semantic search
- **Quiz Generation**: Automatically create quizzes from document content
- **Multiple Question Types**: MCQs, True/False, and Short Answer questions
- **Interactive Review**: Submit answers and get immediate feedback
- **API Backend**: FastAPI server for processing and quiz generation
- **Streamlit UI**: Beautiful, interactive web interface

## 🎥 Demo

Watch a complete demo of the system in action:

👉 ![AI Study Helper Demo](./demo.gif)


## Tech Stack 🛠️

- **Backend**:
  - FastAPI (Python web framework)
  - LangChain (LLM orchestration)
  - ChromaDB (vector database)
  - Ollama (local LLM)
  - pdfplumber (PDF text extraction)

- **Frontend**:
  - Streamlit (web interface)
  - Requests (API communication)

## Installation ⚙️
### Prerequisites
1. Python 3.9 or higher
2. Ollama installed and running (with `mistral` model downloaded)
3. Node.js (for ChromaDB)
   

### Setup
1. Clone the repository:
```bash
git clone https://github.com/bendhiamalak/AIStudyHelper
cd AIStudyHelper
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install ChromaDB:
```bash
npm install chromadb
```

## Usage 🚀
### Running the Backend API
```bash
uvicorn main:app --reload --port 8001
```

### Running the Frontend
```bash
streamlit run app.py
```

### Workflow
Upload PDF: Use the "Upload PDF" tab to submit your document
Generate Quiz: Specify quiz topic and number of questions
Take Quiz: Answer the generated questions
Review Results: Get immediate feedback on your answers
   

