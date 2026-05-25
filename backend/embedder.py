import os
import json
import numpy as np
import faiss
from google import genai

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def get_genai_client():
    # Pick up API key from environment
    return genai.Client()

def create_embeddings_and_index(chunks: list[dict], doc_id: str):
    """
    Generate embeddings for each chunk and build a FAISS vector index.
    Saves index and metadata map to disk.
    """
    if not chunks:
        return
        
    client = get_genai_client()
    texts = [chunk["text"] for chunk in chunks]
    
    # Batch embeddings to optimize API calls
    batch_size = 50
    embeddings_list = []
    
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        response = client.models.embed_content(
            model='text-embedding-004',
            contents=batch_texts
        )
        for emb in response.embeddings:
            embeddings_list.append(emb.values)
            
    embeddings = np.array(embeddings_list, dtype=np.float32)
    
    # FAISS setup - 768 dimensions for text-embedding-004
    dimension = 768
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    # Create output directory
    doc_dir = os.path.join(DATA_DIR, doc_id)
    os.makedirs(doc_dir, exist_ok=True)
    
    # Save FAISS Index
    index_path = os.path.join(doc_dir, "index.faiss")
    faiss.write_index(index, index_path)
    
    # Save chunk mapping to retrieve matching text later
    metadata_path = os.path.join(doc_dir, "metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
