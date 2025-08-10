from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama

def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    return splitter.split_text(text)



def store_embeddings(chunks):
    embeddings = OllamaEmbeddings(model="all-minilm")
    vectordb = Chroma.from_texts(chunks, embeddings, persist_directory="./chroma_db")
    vectordb.persist()
    return vectordb



def generate_quiz(vectordb, topic="general", num_questions=8):
    # Retrieve relevant chunks
    retriever = vectordb.as_retriever(search_kwargs={"k": 4})
    context = "\n".join([doc.page_content for doc in retriever.get_relevant_documents(topic)])
    
    # Quiz prompt
    prompt = f"""
    Generate {num_questions} quiz questions about: {topic}.
    Rules:
    - Mix question types (MCQ, True/False, Short Answer).
    - Return as JSON.
    Example:
    {{
        "questions": [
            {{
                "type": "mcq",
                "question": "What is photosynthesis?",
                "options": ["A", "B", "C", "D"],
                "answer": 0,
                "explanation": "Because plants use sunlight."
            }},
            {{
                "type": "true_false",
                "question": "The Earth is flat.",
                "answer": false
            }}
        ]
    }}
    Context: {context}
    """
    
    llm = Ollama(model="mistral")
    quiz_json = llm(prompt)
    return quiz_json

