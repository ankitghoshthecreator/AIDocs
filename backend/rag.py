import os
import json
import numpy as np
import faiss
from google import genai
from google.genai import types
from backend.prompts import (
    SummaryResponse, ClausesResponse, 
    SUMMARY_SYSTEM_INSTRUCTION, CLAUSE_SYSTEM_INSTRUCTION
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def get_genai_client():
    return genai.Client()

def analyze_document_full(text: str) -> dict:
    """
    Generate summary and extract clauses from the full document text using Gemini.
    """
    client = get_genai_client()
    
    # Run Summary extraction
    summary_response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=text,
        config=types.GenerateContentConfig(
            system_instruction=SUMMARY_SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=SummaryResponse,
        ),
    )
    
    # Run Clause extraction
    clause_response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=text,
        config=types.GenerateContentConfig(
            system_instruction=CLAUSE_SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=ClausesResponse,
        ),
    )
    
    # Parse results safely
    try:
        summary_data = json.loads(summary_response.text)
    except Exception:
        summary_data = {}
        
    try:
        clause_data = json.loads(clause_response.text).get("clauses", [])
    except Exception:
        clause_data = []
        
    return {
        "summary": summary_data,
        "clauses": clause_data
    }

def rag_query(doc_id: str, query: str) -> dict:
    """
    Perform a semantic search in FAISS and generate a context-aware answer.
    """
    doc_dir = os.path.join(DATA_DIR, doc_id)
    index_path = os.path.join(doc_dir, "index.faiss")
    metadata_path = os.path.join(doc_dir, "metadata.json")
    
    if not os.path.exists(index_path) or not os.path.exists(metadata_path):
        return {"answer": "Document index not found.", "citations": []}
        
    # 1. Load FAISS index and metadata
    index = faiss.read_index(index_path)
    with open(metadata_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)
        
    # 2. Embed the query
    client = get_genai_client()
    response = client.models.embed_content(
        model='text-embedding-004',
        contents=query
    )
    query_vector = np.array([response.embeddings[0].values], dtype=np.float32)
    
    # 3. Search index
    k = min(4, len(chunks))
    distances, indices = index.search(query_vector, k)
    
    # 4. Compile relevant context & citations
    retrieved_chunks = []
    context_parts = []
    
    for idx in indices[0]:
        if idx != -1 and idx < len(chunks):
            chunk = chunks[idx]
            retrieved_chunks.append({
                "page": chunk["page"],
                "text": chunk["text"]
            })
            context_parts.append(f"[Page {chunk['page']}]: {chunk['text']}")
            
    context_str = "\n\n".join(context_parts)
    
    # 5. Execute Gemini RAG generation
    rag_system_instruction = """
    You are an AI legal assistant helper. Your job is to answer questions about the provided document using only the provided context.
    Keep your answer concise, informative, and professional. 
    Whenever you reference details from the context, cite it by putting the source page in brackets, like [Page 3] or [Page 1].
    If the context does not contain enough information to answer the question, state that the document does not specify.
    """
    
    prompt = f"Context:\n{context_str}\n\nUser Question: {query}"
    
    gen_response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=rag_system_instruction
        )
    )
    
    return {
        "answer": gen_response.text,
        "citations": retrieved_chunks
    }
