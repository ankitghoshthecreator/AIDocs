def split_pages_into_chunks(pages: list[dict], chunk_size: int = 1000, chunk_overlap: int = 200) -> list[dict]:
    """
    Split pages into overlapping chunks while maintaining page number metadata.
    Returns: list of dicts [{"chunk_id": int, "page": int, "text": str}]
    """
    chunks = []
    chunk_id = 0
    
    for page_data in pages:
        page_num = page_data["page"]
        text = page_data["text"]
        
        if not text:
            continue
            
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = min(start + chunk_size, text_len)
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunks.append({
                    "chunk_id": chunk_id,
                    "page": page_num,
                    "text": chunk_text
                })
                chunk_id += 1
                
            if end >= text_len:
                break
                
            start += (chunk_size - chunk_overlap)
            
    return chunks
