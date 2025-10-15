"""
Chunking Service for SuperKB

Orchestrates document chunking and storage in Snowflake.

STRATEGY: Single recursive character splitting strategy for hackathon demo.
Uses simple, effective chunking without over-engineering.
"""

from typing import Dict, List, Optional
from uuid import UUID
import re

from sqlmodel import Session, select

from graph_rag.db import get_db
from graph_rag.models.chunk import Chunk
from graph_rag.models.file_record import FileRecord


class ChunkingService:
    """Service for chunking documents and storing chunks."""
    
    def __init__(self, db: Session):
        """
        Initialize chunking service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def chunk_document(
        self,
        file_id: UUID,
        chunk_size: int = 512,
        chunk_overlap: int = 50
    ) -> List[Dict]:
        """
        Chunk a document using recursive character splitting.
        
        Single strategy for demo - simple and effective.
        
        Args:
            file_id: File ID to chunk
            chunk_size: Maximum chunk size in characters (default: 512)
            chunk_overlap: Overlap between chunks (default: 50)
            
        Returns:
            List of created chunk dictionaries
            
        Raises:
            ValueError: If file not found
        """
        # Get file record
        file_record = self.db.get(FileRecord, file_id)
        if not file_record:
            raise ValueError(f"File not found: {file_id}")
        
        # Extract text from file
        text = self._extract_text_from_file(file_record)
        
        # Split into chunks using simple recursive splitting
        text_chunks = self._split_text(text, chunk_size, chunk_overlap)
        
        # Create chunk records
        # Insert one at a time to avoid Snowflake executemany issues with VARIANT columns
        result = []
        for chunk_index, chunk_text in enumerate(text_chunks):
            chunk_metadata = {
                "strategy": "recursive_split",
                "char_count": len(chunk_text),
                "word_count": len(chunk_text.split()),
                "chunk_size": chunk_size,
                "overlap": chunk_overlap
            }
            
            chunk = Chunk(
                file_id=file_id,
                chunk_index=chunk_index,
                content=chunk_text,
                start_page=None,  # Can be enhanced with page tracking
                end_page=None,
                chunk_metadata=chunk_metadata,
                embedding=None  # Generated later by embedding service
            )
            
            self.db.add(chunk)
            self.db.commit()  # Commit each chunk individually
            self.db.refresh(chunk)
            result.append(chunk.to_dict())
        
        return result
    
    def get_chunks(self, file_id: UUID) -> List[Dict]:
        """
        Get all chunks for a file.
        
        Args:
            file_id: File ID
            
        Returns:
            List of chunk dictionaries
        """
        statement = select(Chunk).where(Chunk.file_id == file_id).order_by(Chunk.chunk_index)
        chunks = self.db.exec(statement).all()
        return [chunk.to_dict() for chunk in chunks]
    
    def get_chunk(self, chunk_id: UUID) -> Optional[Dict]:
        """
        Get a single chunk by ID.
        
        Args:
            chunk_id: Chunk ID
            
        Returns:
            Chunk dictionary or None if not found
        """
        chunk = self.db.get(Chunk, chunk_id)
        return chunk.to_dict() if chunk else None
    
    def count_chunks(self, file_id: UUID) -> int:
        """
        Count chunks for a file.
        
        Args:
            file_id: File ID
            
        Returns:
            Number of chunks
        """
        statement = select(Chunk).where(Chunk.file_id == file_id)
        chunks = self.db.exec(statement).all()
        return len(chunks)
    
    def delete_chunks(self, file_id: UUID) -> int:
        """
        Delete all chunks for a file.
        
        Args:
            file_id: File ID
            
        Returns:
            Number of chunks deleted
        """
        statement = select(Chunk).where(Chunk.file_id == file_id)
        chunks = self.db.exec(statement).all()
        
        count = 0
        for chunk in chunks:
            self.db.delete(chunk)
            count += 1
        
        self.db.commit()
        return count
    
    def _extract_text_from_file(self, file_record: FileRecord) -> str:
        """
        Extract text from file record.
        
        For now, returns mock text. In production, would:
        1. Locate actual file on disk/storage
        2. Use appropriate parser (PDF, DOCX, etc.)
        3. Extract and return full text
        
        Args:
            file_record: File record
            
        Returns:
            Extracted text
        """
        # Mock text for demonstration
        # In production, you would:
        # - Get file path from file_record or storage
        # - Use PDFParser or other parser
        # - Return actual extracted text
        
        mock_text = f"""
        {file_record.filename} - Research Paper on Knowledge Graphs
        
        Abstract:
        This paper presents a novel approach to knowledge graph construction using
        multimodal database architectures. We demonstrate how relational, graph, and
        vector databases can be unified through a single schema definition.
        
        Introduction:
        Knowledge graphs have become essential for modern information retrieval systems.
        However, traditional approaches struggle with multimodal data representation.
        
        Methods:
        We propose a three-tier architecture:
        1. Relational layer for structured data
        2. Graph layer for relationship traversal  
        3. Vector layer for semantic search
        
        The system uses schema-guided extraction to identify entities and relationships
        automatically from source documents.
        
        Results:
        Our experiments show significant improvements in retrieval accuracy and speed
        compared to traditional single-database approaches.
        
        Conclusion:
        Multimodal knowledge graphs represent the future of information retrieval,
        combining the strengths of multiple database paradigms.
        
        Authors:
        Dr. Jane Smith (MIT), Prof. John Doe (Stanford), Dr. Alice Johnson (Berkeley)
        
        Organizations:
        Massachusetts Institute of Technology, Stanford University, UC Berkeley
        
        The authors are affiliated with leading research institutions and have 
        collaborated on this work as part of a multi-year research project.
        """
        
        return mock_text.strip()
    
    def _split_text(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """
        Split text into chunks using recursive character splitting.
        
        Simple and effective strategy:
        1. Try to split on paragraph boundaries (\n\n)
        2. If chunks too large, split on sentence boundaries (.!?)
        3. If still too large, split on words
        4. Add overlap between chunks
        
        Args:
            text: Text to split
            chunk_size: Maximum chunk size
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        if not text or chunk_size <= 0:
            return []
        
        # Separators in order of preference
        separators = ["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " "]
        
        chunks = []
        current_chunk = ""
        
        # Split by preferred separators
        parts = re.split(r'(\n\n|\n|\. |! |\? |; |, | )', text)
        
        for part in parts:
            # Skip empty parts
            if not part or part.isspace():
                continue
            
            # If adding this part would exceed chunk_size
            if len(current_chunk) + len(part) > chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    # Start new chunk with overlap
                    if chunk_overlap > 0 and len(current_chunk) > chunk_overlap:
                        current_chunk = current_chunk[-chunk_overlap:] + part
                    else:
                        current_chunk = part
                else:
                    # Part itself is larger than chunk_size
                    # Split it forcefully
                    if len(part) > chunk_size:
                        for i in range(0, len(part), chunk_size - chunk_overlap):
                            chunks.append(part[i:i + chunk_size].strip())
                        current_chunk = ""
                    else:
                        current_chunk = part
            else:
                current_chunk += part
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # Filter out empty chunks
        return [c for c in chunks if c]
