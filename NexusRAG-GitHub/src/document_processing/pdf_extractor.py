"""PDF Extractor module for NexusRAG.
Handles loading, text extraction, page tracking, and error handling for PDF documents.
"""
import io
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Union, Optional
import pypdf

from ..utils.logger import get_logger

logger = get_logger("nexusrag.pdf_extractor")

@dataclass
class ExtractedPage:
    page_number: int  # 1-indexed
    text: str
    char_count: int

@dataclass
class ExtractedDocument:
    doc_id: str
    doc_name: str
    total_pages: int
    pages: List[ExtractedPage] = field(default_factory=list)
    total_characters: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def full_text(self) -> str:
        return "\n\n".join(p.text for p in self.pages)

class PDFExtractor:
    """Extracts text and page metadata from PDF files."""

    def __init__(self, min_char_per_page: int = 10):
        self.min_char_per_page = min_char_per_page

    @staticmethod
    def clean_text(text: str) -> str:
        """Removes abnormal whitespace while keeping paragraph structure."""
        if not text:
            return ""
        # Normalize carriage returns and non-breaking spaces
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = text.replace("\xa0", " ").replace("\u200b", "")
        # Remove consecutive spaces but keep line breaks
        text = re.sub(r"[ \t]+", " ", text)
        # Collapse excessive newlines (>2 to 2)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def extract_from_bytes(self, file_bytes: bytes, file_name: str, doc_id: Optional[str] = None) -> ExtractedDocument:
        """Extracts text from in-memory PDF bytes (e.g., from Streamlit file uploader)."""
        if not file_bytes:
            raise ValueError(f"Uploaded file '{file_name}' is empty (0 bytes).")

        stream = io.BytesIO(file_bytes)
        return self._extract_stream(stream, file_name, doc_id)

    def extract_from_path(self, file_path: Union[str, Path], doc_id: Optional[str] = None) -> ExtractedDocument:
        """Extracts text from a file system path."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found at path: {path}")
        if path.suffix.lower() != ".pdf":
            raise ValueError(f"Unsupported file type '{path.suffix}'. Only .pdf is supported.")

        with open(path, "rb") as f:
            stream = io.BytesIO(f.read())
        return self._extract_stream(stream, path.name, doc_id)

    def _extract_stream(self, stream: io.BytesIO, file_name: str, doc_id: Optional[str] = None) -> ExtractedDocument:
        """Core parsing logic using pypdf with robust error recovery."""
        if not doc_id:
            # Deterministic sanitization of file name as doc_id
            clean_name = re.sub(r"[^\w\-.]", "_", file_name)
            doc_id = f"doc_{clean_name}"

        try:
            reader = pypdf.PdfReader(stream)
        except Exception as e:
            logger.error(f"Failed to read PDF stream for {file_name}: {e}")
            raise ValueError(f"Invalid or corrupted PDF file '{file_name}': {str(e)}")

        if reader.is_encrypted:
            try:
                # Attempt empty password decrypt
                reader.decrypt("")
            except Exception:
                raise ValueError(f"PDF '{file_name}' is password protected and cannot be processed.")

        total_pages = len(reader.pages)
        if total_pages == 0:
            raise ValueError(f"PDF '{file_name}' contains no readable pages.")

        extracted_pages: List[ExtractedPage] = []
        total_chars = 0

        for page_idx, page in enumerate(reader.pages, start=1):
            try:
                page_text = page.extract_text() or ""
                cleaned = self.clean_text(page_text)
                if len(cleaned) >= self.min_char_per_page:
                    extracted_pages.append(ExtractedPage(
                        page_number=page_idx,
                        text=cleaned,
                        char_count=len(cleaned)
                    ))
                    total_chars += len(cleaned)
                else:
                    logger.warning(f"Page {page_idx} of '{file_name}' had insufficient text ({len(cleaned)} chars). Skipped.")
            except Exception as page_err:
                logger.warning(f"Error extracting text from page {page_idx} of '{file_name}': {page_err}")

        if not extracted_pages or total_chars == 0:
            raise ValueError(
                f"No extractable text found in '{file_name}'. The PDF may be scanned or image-only."
            )

        logger.info(f"Successfully extracted {len(extracted_pages)} pages ({total_chars} chars) from '{file_name}'.")

        return ExtractedDocument(
            doc_id=doc_id,
            doc_name=file_name,
            total_pages=total_pages,
            pages=extracted_pages,
            total_characters=total_chars,
            metadata={"source": file_name, "pages_extracted": len(extracted_pages)}
        )
