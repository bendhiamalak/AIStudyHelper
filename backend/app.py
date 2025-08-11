from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from pdf_utils import extract_text
from pipeline import chunk_text, store_embeddings, generate_quiz
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
import json
import os
import warnings
import time
# Suppress LangChain deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
async def health_check():
    return {"status": "ready", "timestamp": time.time()}

@app.get("/debug")
async def debug_info():
    return {
        "host": "127.0.0.1",
        "port": 8001,
        "status": "running",
        "chroma_db": os.path.exists("./chroma_db")
    }

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        print(f"Starting upload for file: {file.filename}")  # Debug log
        
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        # Read file contents first
        contents = await file.read()
        print(f"File size: {len(contents)} bytes")  # Debug log
        
        # Process PDF - need to use BytesIO for PDF processing
        from io import BytesIO
        text = extract_text(BytesIO(contents))
        print(f"Extracted text length: {len(text)}")  # Debug log
        
        chunks = chunk_text(text)
        print(f"Created {len(chunks)} chunks")  # Debug log
        
        vectordb = store_embeddings(chunks)
        print("Embeddings stored successfully")  # Debug log
        
        return {
            "message": "PDF processed successfully!", 
            "num_chunks": len(chunks),
            "status": "chroma_db created"
        }
    
    except Exception as e:
        print(f"Error in upload endpoint: {str(e)}", exc_info=True)  # Detailed error logging
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/generate_quiz")
async def make_quiz(
    topic: str = Form("general"),  # Default value is "general"
    num_questions: int = Form(8)   # Default value is 8
):
    try:
        # Verify ChromaDB exists
        if not os.path.exists("./chroma_db"):
            raise HTTPException(
                status_code=404, 
                detail="No processed documents found. Upload a PDF first."
            )
            
        # Load vector store
        embeddings = OllamaEmbeddings(model="all-minilm")
        vectordb = Chroma(
            persist_directory="./chroma_db",
            embedding_function=embeddings
        )
        
        # Generate quiz
        quiz_json = generate_quiz(vectordb, topic, num_questions)
        
        # Parse JSON safely
        try:
            quiz_data = json.loads(quiz_json)
            return quiz_data
        except json.JSONDecodeError as e:
            return {
                "error": "Failed to parse quiz response",
                "raw_response": quiz_json,
                "exception": str(e)
            }
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error generating quiz: {str(e)}"
        )

@app.post("/submit_quiz")
async def check_answers(answers: dict):
    try:
        # Basic implementation - replace with your actual logic
        return {
            "score": "80%",
            "feedback": "Great job!",
            "submitted_answers": answers,
            "details": "Implement your scoring logic here"
        }
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Error checking answers: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)