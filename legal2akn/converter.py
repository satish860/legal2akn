"""Core converter for transforming legal documents to Akoma Ntoso XML."""

from typing import Optional, Union
from pathlib import Path
from lxml import etree
from datetime import datetime

from .models import LegalDocument, Part, Chapter, Article, Section, DocumentMetadata


class AkomaNtosoConverter:
    """Converts legal documents to Akoma Ntoso XML format."""
    
    AKN_NAMESPACE = "http://docs.oasis-open.org/legaldocml/ns/akn/3.0"
    NSMAP = {None: AKN_NAMESPACE}
    
    def __init__(self):
        """Initialize the converter."""
        self.root = None
        self.meta = None
        self.body = None
    
    def convert(self, document: LegalDocument) -> etree.Element:
        """
        Convert a LegalDocument to Akoma Ntoso XML.
        
        Args:
            document: The legal document to convert
            
        Returns:
            The root XML element
        """
        # Create root element based on document type
        doc_type = document.metadata.document_type.lower()
        self.root = etree.Element(f"{{{self.AKN_NAMESPACE}}}{doc_type}", nsmap=self.NSMAP)
        
        # Add metadata
        self._add_metadata(document.metadata)
        
        # Add main content
        self._add_body(document)
        
        return self.root
    
    def _add_metadata(self, metadata: DocumentMetadata) -> None:
        """Add metadata section to the document."""
        meta = etree.SubElement(self.root, "meta")
        
        # Identification section
        identification = etree.SubElement(meta, "identification")
        identification.set("source", "#source")
        
        # FRBRWork
        work = etree.SubElement(identification, "FRBRWork")
        etree.SubElement(work, "FRBRthis").set("value", metadata.uri or f"/akn/{metadata.country}/{metadata.document_type}/main")
        etree.SubElement(work, "FRBRuri").set("value", metadata.uri or f"/akn/{metadata.country}/{metadata.document_type}")
        
        if metadata.date_enacted:
            etree.SubElement(work, "FRBRdate").set("date", metadata.date_enacted.isoformat())
        
        etree.SubElement(work, "FRBRauthor").set("href", f"#{metadata.publisher or 'author'}")
        etree.SubElement(work, "FRBRcountry").set("value", metadata.country)
        
        # FRBRExpression
        expr = etree.SubElement(identification, "FRBRExpression")
        etree.SubElement(expr, "FRBRthis").set("value", f"/akn/{metadata.country}/{metadata.document_type}/{metadata.language}@/main")
        etree.SubElement(expr, "FRBRuri").set("value", f"/akn/{metadata.country}/{metadata.document_type}/{metadata.language}@")
        
        if metadata.date_enacted:
            etree.SubElement(expr, "FRBRdate").set("date", metadata.date_enacted.isoformat())
        
        etree.SubElement(expr, "FRBRauthor").set("href", f"#{metadata.publisher or 'author'}")
        etree.SubElement(expr, "FRBRlanguage").set("language", metadata.language)
        
        # FRBRManifestation
        manif = etree.SubElement(identification, "FRBRManifestation")
        etree.SubElement(manif, "FRBRthis").set("value", f"/akn/{metadata.country}/{metadata.document_type}/{metadata.language}@/main.xml")
        etree.SubElement(manif, "FRBRuri").set("value", f"/akn/{metadata.country}/{metadata.document_type}/{metadata.language}@.akn")
        etree.SubElement(manif, "FRBRdate").set("date", datetime.now().isoformat())
        etree.SubElement(manif, "FRBRauthor").set("href", "#legal2akn")
        
        # References section
        references = etree.SubElement(meta, "references")
        if metadata.publisher:
            org = etree.SubElement(references, "TLCOrganization")
            org.set("eId", metadata.publisher)
            org.set("href", f"/ontology/organization/{metadata.country}/{metadata.publisher}")
            org.set("showAs", metadata.publisher)
    
    def _add_body(self, document: LegalDocument) -> None:
        """Add the main body content of the document."""
        self.body = etree.SubElement(self.root, "body")
        
        # Add preamble if exists
        if document.preamble:
            preamble = etree.SubElement(self.body, "preamble")
            p = etree.SubElement(preamble, "p")
            p.text = document.preamble
        
        # Add hierarchical content
        if document.parts:
            for part in document.parts:
                self._add_part(part)
        elif document.chapters:
            for chapter in document.chapters:
                self._add_chapter(chapter)
        elif document.articles:
            for article in document.articles:
                self._add_article(article, self.body)
        elif document.sections:
            for section in document.sections:
                self._add_section(section, self.body)
        
        # Add conclusions if exists
        if document.conclusions:
            conclusions = etree.SubElement(self.body, "conclusions")
            p = etree.SubElement(conclusions, "p")
            p.text = document.conclusions
    
    def _add_part(self, part: Part) -> None:
        """Add a part element (for Constitution)."""
        part_elem = etree.SubElement(self.body, "part")
        part_elem.set("eId", part.id)
        
        num = etree.SubElement(part_elem, "num")
        num.text = f"PART {part.number}"
        
        if part.heading:
            heading = etree.SubElement(part_elem, "heading")
            heading.text = part.heading
        
        # Add articles within this part
        for article in part.articles:
            self._add_article(article, part_elem)
        
        # Add chapters if any
        for chapter in part.chapters:
            self._add_chapter_to_parent(chapter, part_elem)
    
    def _add_chapter(self, chapter: Chapter) -> None:
        """Add a chapter element."""
        self._add_chapter_to_parent(chapter, self.body)
    
    def _add_chapter_to_parent(self, chapter: Chapter, parent: etree.Element) -> None:
        """Add a chapter element to a parent element."""
        chapter_elem = etree.SubElement(parent, "chapter")
        chapter_elem.set("eId", chapter.id)
        
        num = etree.SubElement(chapter_elem, "num")
        num.text = chapter.number
        
        if chapter.heading:
            heading = etree.SubElement(chapter_elem, "heading")
            heading.text = chapter.heading
        
        for article in chapter.articles:
            self._add_article(article, chapter_elem)
    
    def _add_article(self, article: Article, parent: etree.Element) -> None:
        """Add an article element."""
        article_elem = etree.SubElement(parent, "article")
        article_elem.set("eId", article.id)
        
        num = etree.SubElement(article_elem, "num")
        num.text = article.number
        
        if article.heading:
            heading = etree.SubElement(article_elem, "heading")
            heading.text = article.heading
        
        for section in article.sections:
            self._add_section(section, article_elem)
    
    def _add_section(self, section: Section, parent: etree.Element) -> None:
        """Add a section element."""
        section_elem = etree.SubElement(parent, "section")
        section_elem.set("eId", section.id)
        
        num = etree.SubElement(section_elem, "num")
        num.text = section.number
        
        if section.heading:
            heading = etree.SubElement(section_elem, "heading")
            heading.text = section.heading
        
        # Add content
        content = etree.SubElement(section_elem, "content")
        p = etree.SubElement(content, "p")
        p.text = section.content
        
        # Add subsections
        for subsection in section.subsections:
            self._add_section(subsection, section_elem)
    
    def to_string(self, document: LegalDocument, pretty_print: bool = True) -> str:
        """
        Convert a document to Akoma Ntoso XML string.
        
        Args:
            document: The legal document to convert
            pretty_print: Whether to format the output
            
        Returns:
            XML string representation
        """
        root = self.convert(document)
        return etree.tostring(
            root,
            pretty_print=pretty_print,
            xml_declaration=True,
            encoding="UTF-8"
        ).decode("utf-8")
    
    def to_file(self, document: LegalDocument, filepath: Union[str, Path], pretty_print: bool = True) -> None:
        """
        Convert a document and save to file.
        
        Args:
            document: The legal document to convert
            filepath: Path to save the XML file
            pretty_print: Whether to format the output
        """
        xml_string = self.to_string(document, pretty_print)
        Path(filepath).write_text(xml_string, encoding="utf-8")