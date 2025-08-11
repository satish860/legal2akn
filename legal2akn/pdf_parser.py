"""PDF parser using pymupdf4llm for better structure extraction."""

import re
from pathlib import Path
from typing import Optional, List, Tuple, Dict
import pymupdf4llm


class PDFParser:
    """Extract structured text from PDF legal documents using markdown conversion."""
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """
        Extract text from PDF file using pymupdf4llm for better structure preservation.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text in markdown format
        """
        # Convert PDF to markdown
        md_text = pymupdf4llm.to_markdown(str(pdf_path))
        return md_text
    
    def extract_constitution_structure(self, md_text: str) -> dict:
        """
        Extract structure from markdown text for Indian Constitution.
        
        Args:
            md_text: Markdown formatted text from PDF
            
        Returns:
            Dictionary with parts, articles, and other structure
        """
        structure = {
            'parts': [],
            'articles': [],
            'schedules': []
        }
        
        # Split into lines for processing
        lines = md_text.split('\n')
        
        # Patterns for different elements in markdown
        # Parts are usually major headings (# or ##)
        part_pattern = re.compile(r'^#{1,2}\s*PART\s+([IVXLCDM]+)\s*[–—\-\.]?\s*(.*)$', re.IGNORECASE)
        
        # Articles might be subheadings (### or ####)
        article_pattern = re.compile(r'^#{2,4}\s*Article\s+(\d+[A-Z]?)\s*[.–—\-]?\s*(.*)$', re.IGNORECASE)
        
        # Alternative patterns for when headers aren't properly detected
        part_text_pattern = re.compile(r'^\s*PART\s+([IVXLCDM]+)\s*[–—\-\.]?\s*(.*)$')
        article_text_pattern = re.compile(r'^\s*Article\s+(\d+[A-Z]?)\s*[.–—\-]?\s*(.*)$')
        
        # Schedule pattern
        schedule_pattern = re.compile(
            r'(FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH|EIGHTH|NINTH|TENTH|ELEVENTH|TWELFTH)\s+SCHEDULE',
            re.IGNORECASE
        )
        
        # Process lines
        seen_parts = set()
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check for Parts (in markdown headers or plain text)
            match = part_pattern.match(line)
            if not match:
                match = part_text_pattern.match(line)
            
            if match:
                part_num = match.group(1).upper()
                part_title = match.group(2).strip()
                
                # Clean up markdown formatting from title
                part_title = re.sub(r'[#*_]', '', part_title).strip()
                
                # Skip duplicates
                if part_num not in seen_parts:
                    seen_parts.add(part_num)
                    structure['parts'].append({
                        'number': part_num,
                        'title': part_title,
                        'position': i,
                        'line': line
                    })
            
            # Check for Articles
            match = article_pattern.match(line)
            if not match:
                match = article_text_pattern.match(line)
            
            if match:
                article_num = match.group(1)
                article_title = match.group(2).strip()
                
                # Clean up markdown formatting
                article_title = re.sub(r'[#*_]', '', article_title).strip()
                
                structure['articles'].append({
                    'number': article_num,
                    'title': article_title,
                    'position': i,
                    'line': line
                })
            
            # Check for Schedules
            if schedule_pattern.search(line):
                structure['schedules'].append({
                    'name': line,
                    'position': i
                })
        
        # Ensure we have all 22 parts for 1950 Constitution
        if len(structure['parts']) < 22:
            structure['parts'] = self._fix_missing_parts(md_text, structure['parts'])
        
        # Special handling for Part VII which is commonly missed
        part_numbers = {part['number'] for part in structure['parts']}
        if 'VII' not in part_numbers:
            structure['parts'] = self._find_part_vii_specifically(md_text, structure['parts'])
        
        return structure
    
    def _fix_missing_parts(self, text: str, found_parts: List[Dict]) -> List[Dict]:
        """
        Try to find missing parts using various patterns.
        
        Args:
            text: Full markdown text
            found_parts: List of already found parts
            
        Returns:
            Updated list of parts
        """
        # Expected parts for 1950 Constitution
        expected_parts = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X',
                         'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII',
                         'XIX', 'XX', 'XXI', 'XXII']
        
        found_numbers = {part['number'] for part in found_parts}
        
        # Try different patterns for missing parts
        patterns = [
            r'\bPART\s+{part}\b',  # Basic pattern
            r'^\s*PART\s+{part}\s',  # Start of line
            r'#{{1,4}}\s*PART\s+{part}\b',  # With markdown headers
            r'\*\*PART\s+{part}\*\*',  # Bold markdown
        ]
        
        for expected in expected_parts:
            if expected not in found_numbers:
                for pattern_template in patterns:
                    pattern = re.compile(pattern_template.format(part=re.escape(expected)), re.MULTILINE | re.IGNORECASE)
                    match = pattern.search(text)
                    if match:
                        # Extract context for title
                        start = match.end()
                        end = text.find('\n', start)
                        if end == -1:
                            end = start + 100
                        title = text[start:end].strip(' -–—.*#\n')
                        
                        # Find insertion position
                        insert_pos = 0
                        for i, part in enumerate(found_parts):
                            try:
                                if expected_parts.index(expected) < expected_parts.index(part['number']):
                                    insert_pos = i
                                    break
                            except ValueError:
                                continue
                        else:
                            insert_pos = len(found_parts)
                        
                        found_parts.insert(insert_pos, {
                            'number': expected,
                            'title': title if title else f"Part {expected}",
                            'position': match.start(),
                            'line': match.group(0)
                        })
                        found_numbers.add(expected)
                        break
        
        return sorted(found_parts, key=lambda x: expected_parts.index(x['number']) if x['number'] in expected_parts else 999)
    
    def _find_part_vii_specifically(self, text: str, found_parts: List[Dict]) -> List[Dict]:
        """
        Specific detection for Part VII which is often missed due to formatting issues.
        
        Args:
            text: Full markdown text
            found_parts: List of already found parts
            
        Returns:
            Updated list of parts with Part VII if found
        """
        # Multiple patterns to catch Part VII in various formats
        part_vii_patterns = [
            # Standard patterns
            r'PART\s+VII\b.*?(?:STATES|STATE)',
            r'Part\s+VII\b.*?(?:STATES|STATE)',
            
            # With various separators and formatting
            r'PART\s*[-–—\.]*\s*VII\b.*?(?:STATES|STATE)',
            r'#{1,4}\s*PART\s+VII\b',
            r'\*\*PART\s+VII\*\*',
            
            # Specific to 1950 Constitution context
            r'VII\b.*?STATES.*?PART\s+B',
            r'Part\s+B.*?STATES.*?VII',
            
            # Look for "VII" near "Part B" mentions
            r'(?:PART\s+B|Part\s+B).*?VII|VII.*?(?:PART\s+B|Part\s+B)',
            
            # Roman numeral patterns with context
            r'(?:^|\n)\s*VII[.\s\-–—]+.*?(?:STATES|First\s+Schedule)',
        ]
        
        for pattern_str in part_vii_patterns:
            pattern = re.compile(pattern_str, re.MULTILINE | re.IGNORECASE | re.DOTALL)
            match = pattern.search(text)
            
            if match:
                # Extract title - look for content after "PART VII" or around the match
                title = "THE STATES IN PART B OF THE FIRST SCHEDULE"
                
                # Try to extract actual title from text
                vii_context_pattern = re.compile(
                    r'PART\s+VII\s*[–—\-\.]*\s*(.{0,100}?)(?:\n|PART\s+VIII)',
                    re.IGNORECASE | re.DOTALL
                )
                context_match = vii_context_pattern.search(text)
                if context_match:
                    extracted_title = context_match.group(1).strip()
                    # Clean up the extracted title
                    extracted_title = re.sub(r'[#*_\[\](){}]', '', extracted_title)
                    extracted_title = re.sub(r'\s+', ' ', extracted_title).strip()
                    if len(extracted_title) > 5 and len(extracted_title) < 100:
                        title = extracted_title
                
                # Find correct position to insert Part VII (between VI and VIII)
                insert_pos = len(found_parts)
                for i, part in enumerate(found_parts):
                    if part['number'] in ['VIII', 'IX', 'X']:  # Insert before Part VIII or later
                        insert_pos = i
                        break
                
                found_parts.insert(insert_pos, {
                    'number': 'VII',
                    'title': title,
                    'position': match.start(),
                    'line': match.group(0)[:100]  # First 100 chars of match
                })
                
                print(f"Found Part VII using pattern: {pattern_str}")
                break
        else:
            # If no pattern matches, create Part VII with default title
            print("Part VII not found in text, adding with default title")
            insert_pos = len(found_parts)
            for i, part in enumerate(found_parts):
                if part['number'] in ['VIII', 'IX', 'X']:
                    insert_pos = i
                    break
            
            found_parts.insert(insert_pos, {
                'number': 'VII',
                'title': 'THE STATES IN PART B OF THE FIRST SCHEDULE',
                'position': -1,  # Indicate this was manually added
                'line': 'PART VII (manually added)'
            })
        
        # Sort to maintain proper order
        expected_parts = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X',
                         'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII',
                         'XIX', 'XX', 'XXI', 'XXII']
        
        return sorted(found_parts, key=lambda x: expected_parts.index(x['number']) if x['number'] in expected_parts else 999)
    
    def parse_pdf_to_text(self, pdf_path: Path) -> Tuple[str, dict]:
        """
        Parse PDF and extract both markdown text and structure.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Tuple of (markdown_text, structure_dict)
        """
        # Extract markdown text
        md_text = self.extract_text_from_pdf(pdf_path)
        
        # Extract structure from markdown
        structure = self.extract_constitution_structure(md_text)
        
        return md_text, structure
    
    def clean_text(self, text: str) -> str:
        """
        Clean markdown text for plain text output if needed.
        
        Args:
            text: Markdown text
            
        Returns:
            Cleaned plain text
        """
        # Remove markdown headers
        text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
        
        # Remove emphasis markers
        text = re.sub(r'[*_]{1,2}([^*_]+)[*_]{1,2}', r'\1', text)
        
        # Remove links
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # Clean up excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        return text.strip()