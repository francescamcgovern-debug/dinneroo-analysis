"""
Transcript Parser
=================
Parses customer interview transcripts from DOCX files.

Features:
- Extracts text from 88 DOCX interview files
- Chunks long transcripts into segments suitable for LLM processing
- Extracts metadata (participant name, cycle) from filenames
- Filters to food-related sections for efficiency

Usage:
    from scripts.phase2_analysis.parse_transcripts import TranscriptParser
    
    parser = TranscriptParser()
    transcripts = parser.load_all()
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import python-docx
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logger.warning("python-docx not installed. Run: pip install python-docx")


@dataclass
class TranscriptChunk:
    """A chunk of transcript text with metadata."""
    text: str
    participant: str
    cycle: int
    chunk_index: int
    total_chunks: int
    file_path: str
    word_count: int = 0
    
    def __post_init__(self):
        self.word_count = len(self.text.split())


@dataclass  
class Transcript:
    """A full transcript with all chunks."""
    participant: str
    cycle: int
    file_path: str
    full_text: str
    chunks: List[TranscriptChunk] = field(default_factory=list)
    word_count: int = 0
    
    def __post_init__(self):
        self.word_count = len(self.full_text.split())


# Food-related keywords to identify relevant sections
FOOD_KEYWORDS = [
    # Dishes
    'pizza', 'pasta', 'curry', 'noodle', 'rice', 'chicken', 'burger', 'fish',
    'salad', 'soup', 'sandwich', 'wrap', 'taco', 'burrito', 'sushi', 'ramen',
    'katsu', 'pie', 'roast', 'lasagne', 'biryani', 'kebab', 'shawarma',
    # Cuisines
    'chinese', 'indian', 'italian', 'mexican', 'thai', 'japanese', 'british',
    'mediterranean', 'korean', 'vietnamese',
    # Food concepts
    'meal', 'dinner', 'food', 'eat', 'order', 'cook', 'dish', 'menu',
    'cuisine', 'restaurant', 'takeaway', 'delivery', 'dinneroo',
    # Family/kids food
    'kids', 'children', 'fussy', 'picky', 'vegetarian', 'vegan', 'healthy',
    'portion', 'share', 'family',
    # Sentiment
    'love', 'hate', 'want', 'wish', 'like', 'prefer', 'favourite', 'favorite',
    'missing', 'need', 'looking for',
]


class TranscriptParser:
    """Parser for customer interview transcripts."""
    
    def __init__(
        self,
        transcripts_dir: Optional[str] = None,
        chunk_size: int = 2000,  # words per chunk
        chunk_overlap: int = 200,  # overlap between chunks
        filter_to_food: bool = True
    ):
        """
        Initialize the transcript parser.
        
        Args:
            transcripts_dir: Path to transcripts directory. 
                            Defaults to DATA/1_SOURCE/qual_research/transcripts/customer_interviews/
            chunk_size: Target words per chunk for LLM processing
            chunk_overlap: Words of overlap between chunks
            filter_to_food: Whether to filter to food-related paragraphs only
        """
        if not DOCX_AVAILABLE:
            raise ImportError(
                "python-docx package not installed. "
                "Run: pip install python-docx"
            )
        
        if transcripts_dir:
            self.transcripts_dir = Path(transcripts_dir)
        else:
            # Default path
            base_path = Path(__file__).parent.parent.parent
            self.transcripts_dir = base_path / "DATA" / "1_SOURCE" / "qual_research" / "transcripts" / "customer_interviews"
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.filter_to_food = filter_to_food
        
        logger.info(f"TranscriptParser initialized: {self.transcripts_dir}")
    
    def _parse_filename(self, filename: str) -> Tuple[str, int]:
        """
        Extract participant name and cycle from filename.
        
        Examples:
            "Cycle 10 - Amber.mp4.docx" -> ("Amber", 10)
            "Cycle 2 - Alexander.docx" -> ("Alexander", 2)
            "Cycle 2- Sarah.docx" -> ("Sarah", 2)
        """
        # Remove file extensions
        name = filename.replace('.mp4.docx', '').replace('.docx', '')
        
        # Try to parse "Cycle X - Name" pattern
        match = re.match(r'Cycle\s*(\d+)\s*-\s*(.+)', name, re.IGNORECASE)
        if match:
            cycle = int(match.group(1))
            participant = match.group(2).strip()
            # Clean up participant name
            participant = re.sub(r'^P\d+\s*-\s*', '', participant)  # Remove "P6 - " prefix
            return participant, cycle
        
        # Fallback: try "Name - Cycle X" pattern
        match = re.match(r'(.+)\s*-\s*Cycle\s*(\d+)', name, re.IGNORECASE)
        if match:
            participant = match.group(1).strip()
            cycle = int(match.group(2))
            return participant, cycle
        
        # Last resort
        return name, 0
    
    def _extract_text(self, file_path: Path) -> str:
        """Extract all text from a DOCX file."""
        try:
            doc = Document(file_path)
            paragraphs = []
            
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    paragraphs.append(text)
            
            return "\n\n".join(paragraphs)
            
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return ""
    
    def _is_food_related(self, text: str) -> bool:
        """Check if a paragraph is related to food/dining."""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in FOOD_KEYWORDS)
    
    def _filter_food_paragraphs(self, text: str) -> str:
        """Filter to only food-related paragraphs."""
        paragraphs = text.split("\n\n")
        food_paragraphs = []
        
        for i, para in enumerate(paragraphs):
            if self._is_food_related(para):
                # Include surrounding context (1 paragraph before and after)
                start = max(0, i - 1)
                end = min(len(paragraphs), i + 2)
                for j in range(start, end):
                    if paragraphs[j] not in food_paragraphs:
                        food_paragraphs.append(paragraphs[j])
        
        return "\n\n".join(food_paragraphs)
    
    def _chunk_text(
        self,
        text: str,
        participant: str,
        cycle: int,
        file_path: str
    ) -> List[TranscriptChunk]:
        """Split text into chunks suitable for LLM processing."""
        words = text.split()
        
        if len(words) <= self.chunk_size:
            # Text fits in one chunk
            return [TranscriptChunk(
                text=text,
                participant=participant,
                cycle=cycle,
                chunk_index=0,
                total_chunks=1,
                file_path=file_path
            )]
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)
            
            chunks.append(TranscriptChunk(
                text=chunk_text,
                participant=participant,
                cycle=cycle,
                chunk_index=chunk_index,
                total_chunks=-1,  # Will update after
                file_path=file_path
            ))
            
            chunk_index += 1
            start = end - self.chunk_overlap
            
            # Prevent infinite loop
            if start >= end:
                break
        
        # Update total_chunks
        for chunk in chunks:
            chunk.total_chunks = len(chunks)
        
        return chunks
    
    def parse_file(self, file_path: Path) -> Optional[Transcript]:
        """Parse a single transcript file."""
        participant, cycle = self._parse_filename(file_path.name)
        
        full_text = self._extract_text(file_path)
        if not full_text:
            logger.warning(f"No text extracted from {file_path}")
            return None
        
        # Optionally filter to food-related content
        if self.filter_to_food:
            filtered_text = self._filter_food_paragraphs(full_text)
            if filtered_text:
                processing_text = filtered_text
            else:
                # No food content found, use full text
                processing_text = full_text
        else:
            processing_text = full_text
        
        # Chunk the text
        chunks = self._chunk_text(
            processing_text,
            participant,
            cycle,
            str(file_path)
        )
        
        return Transcript(
            participant=participant,
            cycle=cycle,
            file_path=str(file_path),
            full_text=full_text,
            chunks=chunks
        )
    
    def load_all(self) -> List[Transcript]:
        """Load all transcript files from the directory."""
        if not self.transcripts_dir.exists():
            logger.error(f"Transcripts directory not found: {self.transcripts_dir}")
            return []
        
        transcripts = []
        docx_files = list(self.transcripts_dir.glob("*.docx"))
        
        logger.info(f"Found {len(docx_files)} transcript files")
        
        for file_path in sorted(docx_files):
            transcript = self.parse_file(file_path)
            if transcript:
                transcripts.append(transcript)
                logger.debug(f"Parsed: {transcript.participant} (Cycle {transcript.cycle}) - {transcript.word_count} words, {len(transcript.chunks)} chunks")
        
        logger.info(f"Successfully parsed {len(transcripts)} transcripts")
        
        return transcripts
    
    def get_all_chunks(self) -> List[TranscriptChunk]:
        """Load all transcripts and return all chunks as a flat list."""
        transcripts = self.load_all()
        all_chunks = []
        
        for transcript in transcripts:
            all_chunks.extend(transcript.chunks)
        
        return all_chunks
    
    def get_summary(self) -> Dict:
        """Get a summary of the transcripts."""
        transcripts = self.load_all()
        
        total_words = sum(t.word_count for t in transcripts)
        total_chunks = sum(len(t.chunks) for t in transcripts)
        cycles = sorted(set(t.cycle for t in transcripts))
        
        return {
            "total_transcripts": len(transcripts),
            "total_words": total_words,
            "total_chunks": total_chunks,
            "cycles": cycles,
            "avg_words_per_transcript": total_words // len(transcripts) if transcripts else 0,
            "participants": [t.participant for t in transcripts]
        }


def main():
    """Test the transcript parser."""
    try:
        parser = TranscriptParser()
        
        # Get summary
        summary = parser.get_summary()
        
        print("\n" + "=" * 60)
        print("TRANSCRIPT PARSER SUMMARY")
        print("=" * 60)
        print(f"Total transcripts: {summary['total_transcripts']}")
        print(f"Total words: {summary['total_words']:,}")
        print(f"Total chunks: {summary['total_chunks']}")
        print(f"Avg words/transcript: {summary['avg_words_per_transcript']:,}")
        print(f"Cycles: {summary['cycles']}")
        
        # Show first few participants
        print(f"\nParticipants: {', '.join(summary['participants'][:10])}...")
        
        # Show sample chunk
        chunks = parser.get_all_chunks()
        if chunks:
            sample = chunks[0]
            print(f"\nSample chunk ({sample.participant}, Cycle {sample.cycle}):")
            print(f"  Words: {sample.word_count}")
            print(f"  Text preview: {sample.text[:200]}...")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
