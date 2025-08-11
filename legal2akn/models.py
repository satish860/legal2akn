"""Data models for legal document processing."""

from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Metadata for a legal document."""
    
    title: str = Field(..., description="Document title")
    document_type: str = Field(default="act", description="Type of document (act, bill, judgment, etc.)")
    country: str = Field(default="US", description="Country code")
    language: str = Field(default="eng", description="Language code")
    date_enacted: Optional[date] = Field(None, description="Date of enactment")
    date_effective: Optional[date] = Field(None, description="Effective date")
    publisher: Optional[str] = Field(None, description="Publishing authority")
    uri: Optional[str] = Field(None, description="Document URI")


class Section(BaseModel):
    """Represents a section in a legal document."""
    
    id: str = Field(..., description="Section identifier")
    number: str = Field(..., description="Section number")
    heading: Optional[str] = Field(None, description="Section heading")
    content: str = Field(..., description="Section content text")
    subsections: List["Section"] = Field(default_factory=list, description="Nested subsections")


class Article(BaseModel):
    """Represents an article in a legal document."""
    
    id: str = Field(..., description="Article identifier")
    number: str = Field(..., description="Article number")
    heading: Optional[str] = Field(None, description="Article heading")
    sections: List[Section] = Field(default_factory=list, description="Sections within the article")


class Chapter(BaseModel):
    """Represents a chapter in a legal document."""
    
    id: str = Field(..., description="Chapter identifier")
    number: str = Field(..., description="Chapter number")
    heading: Optional[str] = Field(None, description="Chapter heading")
    articles: List[Article] = Field(default_factory=list, description="Articles within the chapter")


class Part(BaseModel):
    """Represents a part in the Indian Constitution."""
    
    id: str = Field(..., description="Part identifier")
    number: str = Field(..., description="Part number (e.g., I, II, XIX-A)")
    heading: Optional[str] = Field(None, description="Part heading")
    articles: List[Article] = Field(default_factory=list, description="Articles within the part")
    chapters: List[Chapter] = Field(default_factory=list, description="Chapters within the part (if any)")


class LegalDocument(BaseModel):
    """Represents a complete legal document."""
    
    metadata: DocumentMetadata = Field(..., description="Document metadata")
    preamble: Optional[str] = Field(None, description="Document preamble")
    parts: List[Part] = Field(default_factory=list, description="Document parts (for Constitution)")
    chapters: List[Chapter] = Field(default_factory=list, description="Document chapters")
    articles: List[Article] = Field(default_factory=list, description="Top-level articles (if no chapters/parts)")
    sections: List[Section] = Field(default_factory=list, description="Top-level sections (if no articles)")
    conclusions: Optional[str] = Field(None, description="Document conclusions")


# Enable forward references
Section.model_rebuild()