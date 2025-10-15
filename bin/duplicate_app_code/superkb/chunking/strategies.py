"""
Chunking Strategies for SuperKB

Implements different strategies for splitting documents into chunks:
- ParagraphChunker: Split by paragraph boundaries
- SentenceChunker: Split by sentence boundaries  
- FixedSizeChunker: Fixed character/word count with overlap
"""

import re
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple


class ChunkingStrategy(ABC):
    """Base class for chunking strategies."""
    
    @abstractmethod
    def chunk(self, text: str, **kwargs) -> List[Tuple[str, Dict]]:
        """
        Chunk text into smaller pieces.
        
        Args:
            text: Input text to chunk
            **kwargs: Strategy-specific parameters
            
        Returns:
            List of (chunk_text, metadata) tuples
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get the name of this strategy."""
        pass


class ParagraphChunker(ChunkingStrategy):
    """Split text by paragraph boundaries (double newlines)."""
    
    def chunk(self, text: str, min_length: int = 50, **kwargs) -> List[Tuple[str, Dict]]:
        """
        Split text into paragraphs.
        
        Args:
            text: Input text
            min_length: Minimum paragraph length (skip shorter ones)
            
        Returns:
            List of (paragraph_text, metadata) tuples
        """
        # Split by double newlines or more
        paragraphs = re.split(r'\n\s*\n', text)
        
        chunks = []
        for para in paragraphs:
            para = para.strip()
            if len(para) >= min_length:
                metadata = {
                    "strategy": self.get_strategy_name(),
                    "char_count": len(para),
                    "word_count": len(para.split()),
                    "min_length": min_length
                }
                chunks.append((para, metadata))
        
        return chunks
    
    def get_strategy_name(self) -> str:
        return "paragraph"


class SentenceChunker(ChunkingStrategy):
    """Split text by sentence boundaries."""
    
    def chunk(self, text: str, sentences_per_chunk: int = 3, **kwargs) -> List[Tuple[str, Dict]]:
        """
        Split text into sentence-based chunks.
        
        Args:
            text: Input text
            sentences_per_chunk: Number of sentences per chunk
            
        Returns:
            List of (chunk_text, metadata) tuples
        """
        # Simple sentence splitting (can be improved with NLTK)
        # Split on . ! ? followed by whitespace and capital letter
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        
        chunks = []
        for i in range(0, len(sentences), sentences_per_chunk):
            chunk_sentences = sentences[i:i + sentences_per_chunk]
            chunk_text = ' '.join(chunk_sentences).strip()
            
            if chunk_text:
                metadata = {
                    "strategy": self.get_strategy_name(),
                    "char_count": len(chunk_text),
                    "word_count": len(chunk_text.split()),
                    "sentence_count": len(chunk_sentences),
                    "sentences_per_chunk": sentences_per_chunk
                }
                chunks.append((chunk_text, metadata))
        
        return chunks
    
    def get_strategy_name(self) -> str:
        return "sentence"


class FixedSizeChunker(ChunkingStrategy):
    """Split text into fixed-size chunks with optional overlap."""
    
    def chunk(
        self, 
        text: str, 
        chunk_size: int = 500, 
        overlap: int = 50,
        unit: str = "chars",
        **kwargs
    ) -> List[Tuple[str, Dict]]:
        """
        Split text into fixed-size chunks.
        
        Args:
            text: Input text
            chunk_size: Size of each chunk
            overlap: Number of units to overlap between chunks
            unit: "chars" or "words"
            
        Returns:
            List of (chunk_text, metadata) tuples
        """
        if unit == "words":
            items = text.split()
        else:  # chars
            items = list(text)
        
        chunks = []
        i = 0
        chunk_index = 0
        
        while i < len(items):
            # Get chunk
            chunk_items = items[i:i + chunk_size]
            
            if unit == "words":
                chunk_text = ' '.join(chunk_items)
            else:  # chars
                chunk_text = ''.join(chunk_items)
            
            chunk_text = chunk_text.strip()
            
            if chunk_text:
                metadata = {
                    "strategy": self.get_strategy_name(),
                    "char_count": len(chunk_text),
                    "word_count": len(chunk_text.split()),
                    "chunk_size": chunk_size,
                    "overlap": overlap,
                    "unit": unit,
                    "chunk_index": chunk_index
                }
                chunks.append((chunk_text, metadata))
                chunk_index += 1
            
            # Move to next chunk with overlap
            i += chunk_size - overlap
            
            # Prevent infinite loop
            if overlap >= chunk_size:
                i += 1
        
        return chunks
    
    def get_strategy_name(self) -> str:
        return "fixed_size"


# Strategy registry
STRATEGIES = {
    "paragraph": ParagraphChunker(),
    "sentence": SentenceChunker(),
    "fixed_size": FixedSizeChunker(),
}


def get_chunking_strategy(strategy_name: str) -> ChunkingStrategy:
    """
    Get a chunking strategy by name.
    
    Args:
        strategy_name: Name of the strategy ("paragraph", "sentence", "fixed_size")
        
    Returns:
        ChunkingStrategy instance
        
    Raises:
        ValueError: If strategy name is not recognized
    """
    if strategy_name not in STRATEGIES:
        raise ValueError(
            f"Unknown chunking strategy: {strategy_name}. "
            f"Available strategies: {list(STRATEGIES.keys())}"
        )
    return STRATEGIES[strategy_name]
