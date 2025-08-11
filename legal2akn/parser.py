"""Parser for extracting structure from plain text legal documents."""

import re
from typing import List, Optional, Tuple
from .models import LegalDocument, Chapter, Article, Section, DocumentMetadata


class DocumentParser:
    """Parse plain text legal documents into structured format."""
    
    def __init__(self):
        """Initialize the parser with regex patterns."""
        # Common patterns for legal document structure
        self.chapter_pattern = re.compile(r'^CHAPTER\s+(\d+|[IVXLCDM]+)\.?\s*[-:]?\s*(.*)$', re.IGNORECASE | re.MULTILINE)
        self.article_pattern = re.compile(r'^(?:Article|Art\.?)\s+(\d+|[IVXLCDM]+)\.?\s*[-:]?\s*(.*)$', re.IGNORECASE | re.MULTILINE)
        self.section_pattern = re.compile(r'^(?:Section|Sec\.?|§)\s+(\d+(?:\.\d+)*)\s*[-:]?\s*(.*)$', re.IGNORECASE | re.MULTILINE)
        self.subsection_pattern = re.compile(r'^\s*\(([a-z]|\d+)\)\s+(.*)$', re.MULTILINE)
    
    def parse(self, text: str, metadata: Optional[DocumentMetadata] = None) -> LegalDocument:
        """
        Parse plain text into a structured legal document.
        
        Args:
            text: The plain text content
            metadata: Optional metadata for the document
            
        Returns:
            Structured LegalDocument object
        """
        if metadata is None:
            metadata = DocumentMetadata(title="Untitled Document")
        
        document = LegalDocument(metadata=metadata)
        
        # Try to extract preamble (text before first structural element)
        preamble_end = self._find_first_structure(text)
        if preamble_end > 0:
            document.preamble = text[:preamble_end].strip()
            text = text[preamble_end:]
        
        # Check for chapters
        chapters = self._extract_chapters(text)
        if chapters:
            document.chapters = chapters
        else:
            # Check for articles
            articles = self._extract_articles(text)
            if articles:
                document.articles = articles
            else:
                # Extract sections directly
                document.sections = self._extract_sections(text)
        
        return document
    
    def _find_first_structure(self, text: str) -> int:
        """Find the position of the first structural element."""
        positions = []
        
        for pattern in [self.chapter_pattern, self.article_pattern, self.section_pattern]:
            match = pattern.search(text)
            if match:
                positions.append(match.start())
        
        return min(positions) if positions else -1
    
    def _extract_chapters(self, text: str) -> List[Chapter]:
        """Extract chapters from text."""
        chapters = []
        matches = list(self.chapter_pattern.finditer(text))
        
        for i, match in enumerate(matches):
            chapter_num = match.group(1)
            chapter_heading = match.group(2).strip()
            
            # Get content until next chapter or end
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            content = text[start:end]
            
            # Extract articles within this chapter
            articles = self._extract_articles(content)
            
            chapter = Chapter(
                id=f"chp_{chapter_num}",
                number=chapter_num,
                heading=chapter_heading if chapter_heading else None,
                articles=articles
            )
            chapters.append(chapter)
        
        return chapters
    
    def _extract_articles(self, text: str) -> List[Article]:
        """Extract articles from text."""
        articles = []
        matches = list(self.article_pattern.finditer(text))
        
        for i, match in enumerate(matches):
            article_num = match.group(1)
            article_heading = match.group(2).strip()
            
            # Get content until next article or end
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            content = text[start:end]
            
            # Extract sections within this article
            sections = self._extract_sections(content)
            
            article = Article(
                id=f"art_{article_num}",
                number=article_num,
                heading=article_heading if article_heading else None,
                sections=sections
            )
            articles.append(article)
        
        return articles
    
    def _extract_sections(self, text: str) -> List[Section]:
        """Extract sections from text."""
        sections = []
        matches = list(self.section_pattern.finditer(text))
        
        for i, match in enumerate(matches):
            section_num = match.group(1)
            section_heading = match.group(2).strip()
            
            # Get content until next section or end
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            content = text[start:end].strip()
            
            # Extract subsections if any
            subsections = self._extract_subsections(content)
            
            # If subsections found, remove them from main content
            if subsections:
                first_subsection = self.subsection_pattern.search(content)
                if first_subsection:
                    content = content[:first_subsection.start()].strip()
            
            section = Section(
                id=f"sec_{section_num.replace('.', '_')}",
                number=section_num,
                heading=section_heading if section_heading else None,
                content=content,
                subsections=subsections
            )
            sections.append(section)
        
        return sections
    
    def _extract_subsections(self, text: str) -> List[Section]:
        """Extract subsections from text."""
        subsections = []
        matches = list(self.subsection_pattern.finditer(text))
        
        for i, match in enumerate(matches):
            subsection_num = match.group(1)
            
            # Get content until next subsection or end
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            content = text[start:end]
            
            # Clean up the content
            content = re.sub(r'^\s*\([a-z]|\d+\)\s*', '', content).strip()
            
            subsection = Section(
                id=f"subsec_{subsection_num}",
                number=subsection_num,
                heading=None,
                content=content
            )
            subsections.append(subsection)
        
        return subsections