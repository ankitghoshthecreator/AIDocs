import pypdf

def extract_text_by_page(file_path: str) -> list[dict]:
    """
    Extract text and associate with page numbers from a PDF file.
    Returns: list of dicts [{"page": int, "text": str}]
    """
    pages_data = []
    try:
        reader = pypdf.PdfReader(file_path)
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            pages_data.append({
                "page": i + 1,
                "text": text.strip()
            })
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
    return pages_data
