import os
import uuid
import json
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load env variables (GEMINI_API_KEY)
load_dotenv()

from backend.parser import extract_text_by_page
from backend.chunker import split_pages_into_chunks
from backend.embedder import create_embeddings_and_index
from backend.rag import analyze_document_full, rag_query

app = FastAPI(title="AIDocs API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

class ChatRequest(BaseModel):
    doc_id: str
    query: str

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload, parse, chunk, embed, index, and analyze a document"""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    doc_id = uuid.uuid4().hex
    doc_dir = os.path.join(DATA_DIR, doc_id)
    os.makedirs(doc_dir, exist_ok=True)
    
    # Save the file to disk
    pdf_path = os.path.join(doc_dir, "doc.pdf")
    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # 1. Parse text from PDF page-by-page
        pages = extract_text_by_page(pdf_path)
        if not pages or all(not p["text"] for p in pages):
            raise HTTPException(status_code=400, detail="No readable text found in PDF.")
            
        full_text = "\n\n".join([f"--- Page {p['page']} ---\n{p['text']}" for p in pages])
        
        # 2. Extract structured summary & clauses via Gemini
        analysis = analyze_document_full(full_text)
        
        # 3. Create chunks with page references
        chunks = split_pages_into_chunks(pages)
        
        # 4. Generate embeddings and save FAISS index
        create_embeddings_and_index(chunks, doc_id)
        
        # Save analysis details to disk
        analysis_path = os.path.join(doc_dir, "analysis.json")
        with open(analysis_path, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
            
        return {
            "status": "success",
            "doc_id": doc_id,
            "filename": file.filename,
            "summary": analysis.get("summary", {}),
            "clauses": analysis.get("clauses", [])
        }
    except Exception as e:
        # Clean up on failure
        if os.path.exists(doc_dir):
            shutil.rmtree(doc_dir)
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Query the document via RAG"""
    try:
        result = rag_query(request.doc_id, request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents/{doc_id}")
async def get_document(doc_id: str):
    """Retrieve document summary and clauses"""
    analysis_path = os.path.join(DATA_DIR, doc_id, "analysis.json")
    if not os.path.exists(analysis_path):
        raise HTTPException(status_code=404, detail="Document not found.")
        
    try:
        with open(analysis_path, "r", encoding="utf-8") as f:
            analysis = json.load(f)
        return {
            "doc_id": doc_id,
            "summary": analysis.get("summary", {}),
            "clauses": analysis.get("clauses", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
