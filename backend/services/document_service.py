import os
import re
from pathlib import Path
from typing import List


def extract_text_from_upload(uploaded_file) -> str:
    """Extract text from a simple uploaded text file."""
    filename = (uploaded_file.filename or '').lower()
    if filename.endswith('.txt') or filename.endswith('.md'):
        return uploaded_file.read().decode('utf-8', errors='ignore')

    # For non-text uploads, return a placeholder message.
    return ""


def build_document_chunks(text_content: str, chunk_size: int = 300) -> List[str]:
    """Split extracted text into smaller chunks for retrieval."""
    cleaned_text = re.sub(r'\s+', ' ', text_content or '').strip()
    if not cleaned_text:
        return []

    words = cleaned_text.split()
    chunks = []
    for index in range(0, len(words), chunk_size):
        chunk = ' '.join(words[index:index + chunk_size]).strip()
        if chunk:
            chunks.append(chunk)
    return chunks
