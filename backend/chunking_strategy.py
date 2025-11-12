# -----------------------------------------------------------------------------
# File: chunking_strategy.py
# Description: Intelligent chunking strategy for large documents - handles 
#              documents of any size by splitting into processable chunks.
# Author: Pradyumna Chacham
# Date: November 2025
# Copyright (c) 2025 Pradyumna Chacham. All rights reserved.
# License: MIT License - see LICENSE file in the root directory.
# -----------------------------------------------------------------------------

"""
Intelligent Chunking Strategy for Large Documents
Handles documents of any size by splitting into processable chunks
"""

import re
from typing import Dict, List, Tuple


class DocumentChunker:
    """Intelligent document chunking for LLM processing"""

    def __init__(self, max_tokens: int = 3000):
        """
        Initialize chunker

        Args:
            max_tokens: Maximum tokens per chunk (conservative estimate)
        """
        self.max_tokens = max_tokens
        # Rough estimate: 1 token ≈ 4 characters
        self.max_chars_per_chunk = max_tokens * 4

    def chunk_document(self, text: str, strategy: str = "auto") -> List[Dict]:
        """
        Split document into processable chunks

        Args:
            text: Full document text
            strategy: Chunking strategy - "auto", "sentence", "paragraph", "section"

        Returns:
            List of chunks with metadata
        """
        char_count = len(text)

        print(f"\n{'='*80}")
        print(f"📄 DOCUMENT CHUNKING")
        print(f"{'='*80}")
        print(f"Total characters: {char_count:,}")
        print(f"Estimated tokens: {int(char_count / 4):,}")
        print(f"Max tokens per chunk: {self.max_tokens:,}")

        # If text is small enough and strategy is auto, return as single chunk
        if char_count <= self.max_chars_per_chunk and strategy == "auto":
            print(f"✅ Document fits in single chunk - no splitting needed\n")
            return [
                {
                    "chunk_id": 0,
                    "text": text,
                    "char_count": char_count,
                    "estimated_tokens": int(char_count / 4),
                    "strategy": "single",
                }
            ]

        # Force chunking for non-auto strategies or large texts
        if char_count > self.max_chars_per_chunk:
            print(f"⚠️ Document exceeds chunk size - splitting required")

        # Auto-detect best strategy
        if strategy == "auto":
            strategy = self._detect_best_strategy(text)

        print(f"Strategy: {strategy}")

        # Apply chunking strategy
        if strategy == "section":
            chunks = self._chunk_by_sections(text)
        elif strategy == "paragraph":
            chunks = self._chunk_by_paragraphs(text)
        else:
            chunks = self._chunk_by_sentences(text)

        print(f"✅ Created {len(chunks)} chunks")
        for i, chunk in enumerate(chunks):
            print(
                f"   Chunk {i+1}: {chunk['char_count']:,} chars (~{chunk['estimated_tokens']:,} tokens)"
            )
        print(f"{'='*80}\n")

        return chunks

    def _detect_best_strategy(self, text: str) -> str:
        """Detect the best chunking strategy based on document structure"""

        # Check for section headers (markdown or numbered)
        section_patterns = [
            r"^#{1,3}\s+.+$",  # Markdown headers
            r"^\d+\.\s+[A-Z].+$",  # Numbered sections
            r"^[A-Z][A-Z\s]+:",  # ALL CAPS headers
        ]

        section_count = 0
        for pattern in section_patterns:
            section_count += len(re.findall(pattern, text, re.MULTILINE))

        if section_count >= 3:
            return "section"

        # Check paragraph density
        paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
        if len(paragraphs) >= 5:
            return "paragraph"

        return "sentence"

    def _chunk_by_sections(self, text: str) -> List[Dict]:
        """Chunk by detecting sections/headers"""

        # Split by common section patterns
        section_pattern = r"(^#{1,3}\s+.+$|^\d+\.\s+[A-Z].+$|^[A-Z][A-Z\s]+:)"

        parts = re.split(section_pattern, text, flags=re.MULTILINE)

        chunks = []
        current_chunk = ""
        chunk_id = 0

        for i, part in enumerate(parts):
            if not part.strip():
                continue

            potential_chunk = current_chunk + "\n\n" + part if current_chunk else part

            # If adding this part exceeds limit, save current and start new
            if len(potential_chunk) > self.max_chars_per_chunk and current_chunk:
                chunks.append(self._create_chunk_dict(chunk_id, current_chunk))
                chunk_id += 1
                current_chunk = part
            else:
                current_chunk = potential_chunk

        # Add final chunk
        if current_chunk.strip():
            chunks.append(self._create_chunk_dict(chunk_id, current_chunk))

        return chunks if chunks else [self._create_chunk_dict(0, text)]

    def _chunk_by_paragraphs(self, text: str) -> List[Dict]:
        """Chunk by paragraphs"""

        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        chunks = []
        current_chunk = ""
        chunk_id = 0

        for para in paragraphs:
            potential_chunk = current_chunk + "\n\n" + para if current_chunk else para

            if len(potential_chunk) > self.max_chars_per_chunk and current_chunk:
                chunks.append(self._create_chunk_dict(chunk_id, current_chunk))
                chunk_id += 1
                current_chunk = para
            else:
                current_chunk = potential_chunk

        if current_chunk.strip():
            chunks.append(self._create_chunk_dict(chunk_id, current_chunk))

        return chunks if chunks else [self._create_chunk_dict(0, text)]

    def _chunk_by_sentences(self, text: str) -> List[Dict]:
        """Chunk by sentences with overlap"""

        # Simple sentence splitting
        sentences = re.split(r"(?<=[.!?])\s+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        chunks = []
        chunk_id = 0
        current_sentences = []

        for sentence in sentences:
            current_sentences.append(sentence)
            current_text = " ".join(current_sentences)

            # If current chunk would exceed the limit
            if (
                len(current_text) * 4 > self.max_tokens * 4
                and len(current_sentences) > 1
            ):
                # Keep all but the last sentence for the current chunk
                chunk_text = " ".join(current_sentences[:-1])
                chunks.append(self._create_chunk_dict(chunk_id, chunk_text))
                chunk_id += 1

                # Start new chunk with the last sentence from previous chunk for overlap
                current_sentences = (
                    current_sentences[-2:]
                    if len(current_sentences) > 2
                    else current_sentences[-1:]
                )

        # Add final chunk if there's remaining text
        if current_sentences:
            chunks.append(
                self._create_chunk_dict(chunk_id, " ".join(current_sentences))
            )

        return chunks if chunks else [self._create_chunk_dict(0, text)]

    def _create_chunk_dict(self, chunk_id: int, text: str) -> Dict:
        """Create chunk dictionary with metadata"""
        char_count = len(text)
        return {
            "chunk_id": chunk_id,
            "text": text.strip(),
            "char_count": char_count,
            "estimated_tokens": int(char_count / 4),
            "strategy": "chunked",
        }

    def merge_extracted_use_cases(self, chunk_results: List[List[dict]]) -> List[dict]:
        """
        Merge use cases extracted from multiple chunks, removing duplicates

        Args:
            chunk_results: List of use case lists from each chunk

        Returns:
            Deduplicated list of use cases
        """
        all_use_cases = []
        seen_titles = set()

        for chunk_uc_list in chunk_results:
            for uc in chunk_uc_list:
                title_normalized = uc.get("title", "").lower().strip()

                # Skip if we've seen this title
                if title_normalized in seen_titles:
                    print(
                        f"🔄 Skipping duplicate across chunks: {uc.get('title', 'Unknown')}"
                    )
                    continue

                seen_titles.add(title_normalized)
                all_use_cases.append(uc)

        print(
            f"\n✅ Merged {len(all_use_cases)} unique use cases from {len(chunk_results)} chunks"
        )

        return all_use_cases
