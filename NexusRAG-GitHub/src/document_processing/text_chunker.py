"""Text Chunker module for NexusRAG.
Implements semantic, boundary-aware document chunking with configurable overlap and page metadata.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from .pdf_extractor import ExtractedDocument, ExtractedPage
from ..utils.logger import get_logger

logger = get_logger("nexusrag.text_chunker")

@dataclass
class TextChunk:
    chunk_id: str
    doc_id: str
    doc_name: str
    page_number: int
    chunk_index: int
    text: str
    character_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "doc_name": self.doc_name,
            "page_number": self.page_number,
            "chunk_index": self.chunk_index,
            "text": self.text,
            "character_count": self.character_count,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TextChunk":
        return cls(
            chunk_id=data["chunk_id"],
            doc_id=data["doc_id"],
            doc_name=data["doc_name"],
            page_number=data["page_number"],
            chunk_index=data["chunk_index"],
            text=data["text"],
            character_count=data.get("character_count", len(data["text"])),
            metadata=data.get("metadata", {})
        )

class TextChunker:
    """Splits extracted document pages into overlapping, boundary-aware chunks."""

    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 120):
        if chunk_overlap >= chunk_size:
            raise ValueError(f"chunk_overlap ({chunk_overlap}) must be strictly less than chunk_size ({chunk_size})")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, document: ExtractedDocument) -> List[TextChunk]:
        """Chunks an entire extracted document page by page while maintaining metadata."""
        all_chunks: List[TextChunk] = []
        global_chunk_idx = 0

        for page in document.pages:
            page_chunks = self._chunk_page(
                page=page,
                doc_id=document.doc_id,
                doc_name=document.doc_name,
                start_chunk_idx=global_chunk_idx
            )
            all_chunks.extend(page_chunks)
            global_chunk_idx += len(page_chunks)

        logger.info(
            f"Created {len(all_chunks)} chunks for document '{document.doc_name}' "
            f"(chunk_size={self.chunk_size}, overlap={self.chunk_overlap})."
        )
        return all_chunks

    def _chunk_page(self, page: ExtractedPage, doc_id: str, doc_name: str, start_chunk_idx: int) -> List[TextChunk]:
        """Splits single page text into overlapping windows using boundary heuristics."""
        text = page.text
        if len(text) <= self.chunk_size:
            chunk_id = f"{doc_id}_p{page.page_number}_c{start_chunk_idx}"
            return [TextChunk(
                chunk_id=chunk_id,
                doc_id=doc_id,
                doc_name=doc_name,
                page_number=page.page_number,
                chunk_index=start_chunk_idx,
                text=text,
                character_count=len(text)
            )]

        chunks: List[TextChunk] = []
        start = 0
        text_len = len(text)
        current_idx = start_chunk_idx

        while start < text_len:
            end = start + self.chunk_size
            if end >= text_len:
                chunk_text = text[start:].strip()
                if chunk_text:
                    chunk_id = f"{doc_id}_p{page.page_number}_c{current_idx}"
                    chunks.append(TextChunk(
                        chunk_id=chunk_id,
                        doc_id=doc_id,
                        doc_name=doc_name,
                        page_number=page.page_number,
                        chunk_index=current_idx,
                        text=chunk_text,
                        character_count=len(chunk_text)
                    ))
                break

            # Find natural break point near 'end' (prefer sentence end '. ', then newline '\n', then space ' ')
            split_at = self._find_split_point(text, start, end)
            chunk_text = text[start:split_at].strip()

            if chunk_text:
                chunk_id = f"{doc_id}_p{page.page_number}_c{current_idx}"
                chunks.append(TextChunk(
                    chunk_id=chunk_id,
                    doc_id=doc_id,
                    doc_name=doc_name,
                    page_number=page.page_number,
                    chunk_index=current_idx,
                    text=chunk_text,
                    character_count=len(chunk_text)
                ))
                current_idx += 1

            # Advance with overlap
            start = max(start + 1, split_at - self.chunk_overlap)

        return chunks

    def _find_split_point(self, text: str, start: int, target_end: int) -> int:
        """Finds the best boundary to split without breaking words."""
        # Search backward from target_end within a window of 100 characters
        search_window_start = max(start, target_end - 100)
        window = text[search_window_start:target_end]

        # 1. Paragraph break
        para_idx = window.rfind("\n\n")
        if para_idx != -1:
            return search_window_start + para_idx + 2

        # 2. Sentence break
        for punct in [". ", "? ", "! "]:
            p_idx = window.rfind(punct)
            if p_idx != -1:
                return search_window_start + p_idx + 2

        # 3. Line break
        line_idx = window.rfind("\n")
        if line_idx != -1:
            return search_window_start + line_idx + 1

        # 4. Word boundary (space)
        space_idx = window.rfind(" ")
        if space_idx != -1:
            return search_window_start + space_idx + 1

        # Fallback to hard split
        return target_end
