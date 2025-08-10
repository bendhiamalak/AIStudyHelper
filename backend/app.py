from fastapi import FastAPI, UploadFile, File
from pdf_utils import extract_text_from_pdf
from pipeline import chunk_text, store_embeddings, generate_quiz
import json

app = FastAPI()

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    text = extract_text_from_pdf(file.file)
    chunks = chunk_text(text)
    vectordb = store_embeddings(chunks)
    return {"message": "PDF processed!"}

@app.post("/generate_quiz")
async def make_quiz(topic: str = "general", num_questions: int = 8):
    vectordb = Chroma(persist_directory="./chroma_db", embedding_function=OllamaEmbeddings())
    quiz = generate_quiz(vectordb, topic, num_questions)
    return json.loads(quiz)

@app.post("/submit_quiz")
async def check_answers(answers: dict):
    # Compare user answers with correct answers
    return {"score": "80%", "feedback": "Great job!"}