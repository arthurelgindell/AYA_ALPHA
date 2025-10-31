#!/usr/bin/env python3
"""
Intelligence Scout Processor - Content Processing Pipeline
Handles markdown cleaning, chunking, metadata extraction, and deduplication
"""

import re
import json
from typing import List, Dict, Optional
from datetime import datetime

class ScoutProcessor:
    """
    Processes crawled content for knowledge base ingestion
    """
    
    def __init__(self, max_chunk_tokens: int = 512):
        """
        Initialize processor
        
        Args:
            max_chunk_tokens: Maximum tokens per chunk for embeddings
        """
        self.max_chunk_tokens = max_chunk_tokens
        # Approximate tokens: 1 token ≈ 4 characters
        self.max_chunk_chars = max_chunk_tokens * 4
    
    def clean_markdown(self, markdown: str) -> str:
        """
        Clean markdown content for better processing
        
        Args:
            markdown: Raw markdown content
            
        Returns:
            Cleaned markdown text
        """
        if not markdown:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', markdown)
        
        # Remove HTML comments
        text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
        
        # Clean up code blocks (preserve content, normalize formatting)
        text = re.sub(r'```(\w+)?\n', '```\n', text)
        
        # Remove navigation elements and common web cruft
        text = re.sub(r'\[Skip to content\]', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[Skip to navigation\]', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def extract_metadata(self, url: str, content: str, title: str = "") -> Dict:
        """
        Extract metadata from content
        
        Args:
            url: Source URL
            content: Content text
            title: Page title
            
        Returns:
            Metadata dictionary
        """
        metadata = {
            'url': url,
            'title': title,
            'crawled_at': datetime.now().isoformat(),
            'word_count': len(content.split()) if content else 0,
            'section_type': self._determine_section_type(url, content)
        }
        
        # Extract version if present in URL or content
        version_match = re.search(r'v?(\d+\.\d+(?:\.\d+)?)', url + ' ' + content)
        if version_match:
            metadata['version'] = version_match.group(1)
        
        # Extract category from URL path
        if '/api/' in url:
            metadata['category'] = 'api'
        elif '/docs/' in url or '/documentation' in url:
            metadata['category'] = 'documentation'
        elif '/tutorial' in url or '/guide' in url:
            metadata['category'] = 'tutorial'
        elif '/reference' in url or '/ref' in url:
            metadata['category'] = 'reference'
        else:
            metadata['category'] = 'general'
        
        return metadata
    
    def _determine_section_type(self, url: str, content: str) -> str:
        """Determine section type from URL and content"""
        if '/docs/' in url or '/documentation' in url:
            return 'documentation'
        elif '/api/' in url:
            return 'api'
        elif '/blog' in url:
            return 'blog'
        elif '/tutorial' in url:
            return 'tutorial'
        elif '/guide' in url:
            return 'guide'
        elif '/reference' in url or '/ref' in url:
            return 'reference'
        else:
            return 'general'
    
    def chunk_content(self, content: str, url: str = "", preserve_structure: bool = True) -> List[Dict]:
        """
        Chunk content into embedding-sized pieces
        
        Args:
            content: Content to chunk
            url: Source URL for context
            preserve_structure: Try to preserve paragraph/section boundaries
            
        Returns:
            List of chunk dictionaries with content and metadata
        """
        if not content:
            return []
        
        cleaned = self.clean_markdown(content)
        
        if len(cleaned) <= self.max_chunk_chars:
            # Single chunk
            return [{
                'content': cleaned,
                'url': url,
                'chunk_index': 0,
                'total_chunks': 1
            }]
        
        chunks = []
        
        if preserve_structure:
            # Try to chunk by paragraphs/sections
            # Split by double newlines (paragraphs)
            paragraphs = cleaned.split('\n\n')
            current_chunk = ""
            chunk_index = 0
            
            for para in paragraphs:
                # If adding this paragraph would exceed limit, save current chunk
                if current_chunk and len(current_chunk) + len(para) + 2 > self.max_chunk_chars:
                    chunks.append({
                        'content': current_chunk.strip(),
                        'url': url,
                        'chunk_index': chunk_index,
                        'total_chunks': 0  # Will update later
                    })
                    chunk_index += 1
                    current_chunk = para
                else:
                    if current_chunk:
                        current_chunk += "\n\n" + para
                    else:
                        current_chunk = para
                
                # If single paragraph exceeds limit, split by sentences
                if len(current_chunk) > self.max_chunk_chars:
                    sentences = re.split(r'(?<=[.!?])\s+', current_chunk)
                    temp_chunk = ""
                    
                    for sentence in sentences:
                        if temp_chunk and len(temp_chunk) + len(sentence) + 1 > self.max_chunk_chars:
                            chunks.append({
                                'content': temp_chunk.strip(),
                                'url': url,
                                'chunk_index': chunk_index,
                                'total_chunks': 0
                            })
                            chunk_index += 1
                            temp_chunk = sentence
                        else:
                            temp_chunk += " " + sentence if temp_chunk else sentence
                    
                    current_chunk = temp_chunk
            
            # Add final chunk
            if current_chunk.strip():
                chunks.append({
                    'content': current_chunk.strip(),
                    'url': url,
                    'chunk_index': chunk_index,
                    'total_chunks': 0
                })
        else:
            # Simple character-based chunking
            for i in range(0, len(cleaned), self.max_chunk_chars):
                chunk = cleaned[i:i + self.max_chunk_chars]
                chunks.append({
                    'content': chunk.strip(),
                    'url': url,
                    'chunk_index': i // self.max_chunk_chars,
                    'total_chunks': 0
                })
        
        # Update total_chunks
        total = len(chunks)
        for chunk in chunks:
            chunk['total_chunks'] = total
        
        return chunks
    
    def check_duplicate(self, content: str, existing_hashes: set) -> Optional[str]:
        """
        Check if content is duplicate
        
        Args:
            content: Content to check
            existing_hashes: Set of existing content hashes
            
        Returns:
            Content hash if duplicate, None otherwise
        """
        import hashlib
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        if content_hash in existing_hashes:
            return content_hash
        
        return None
    
    def calculate_importance(self, url: str, content: str, title: str = "") -> int:
        """
        Calculate importance score (1-10) for prioritization
        
        Args:
            url: Source URL
            content: Content text
            title: Page title
            
        Returns:
            Importance score (1-10)
        """
        score = 5  # Base score
        
        # Boost for API documentation
        if '/api/' in url:
            score += 2
        
        # Boost for getting started / quickstart
        if any(term in url.lower() for term in ['getting-started', 'quickstart', 'install', 'setup']):
            score += 2
        
        # Boost for reference docs
        if '/reference' in url or '/ref' in url:
            score += 1
        
        # Boost for tutorial/guide
        if '/tutorial' in url or '/guide' in url:
            score += 1
        
        # Penalize for blog/news
        if '/blog' in url or '/news' in url:
            score -= 2
        
        # Boost for substantial content
        word_count = len(content.split())
        if word_count > 1000:
            score += 1
        elif word_count < 100:
            score -= 1
        
        return max(1, min(10, score))

