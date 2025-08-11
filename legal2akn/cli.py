"""Command-line interface for legal2akn."""

import sys
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from .converter import AkomaNtosoConverter
from .parser import DocumentParser
from .pdf_parser import PDFParser
from .models import DocumentMetadata, LegalDocument


console = Console()


@click.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option('-o', '--output', type=click.Path(path_type=Path), help='Output XML file path')
@click.option('-t', '--title', help='Document title')
@click.option('--type', 'doc_type', default='act', help='Document type (act, bill, judgment, etc.)')
@click.option('--country', default='US', help='Country code (e.g., US, UK, CA)')
@click.option('--language', default='eng', help='Language code (e.g., eng, fra, esp)')
@click.option('--parse', is_flag=True, help='Parse plain text document structure')
@click.option('--json', 'as_json', is_flag=True, help='Input is JSON format')
@click.option('--preview', is_flag=True, help='Preview output without saving')
@click.option('--verbose', is_flag=True, help='Show detailed processing information')
def main(
    input_file: Path,
    output: Optional[Path],
    title: Optional[str],
    doc_type: str,
    country: str,
    language: str,
    parse: bool,
    as_json: bool,
    preview: bool,
    verbose: bool
):
    """
    Convert legal documents to Akoma Ntoso XML format.
    
    Example usage:
    
        legal2akn document.txt -o document.xml --parse
        
        legal2akn structured.json -o output.xml --json
    """
    try:
        # Check if input is PDF
        if input_file.suffix.lower() == '.pdf':
            if verbose:
                console.print(f"[blue]Processing PDF file:[/blue] {input_file}")
            
            pdf_parser = PDFParser()
            markdown_content, structure_info = pdf_parser.parse_pdf_to_text(input_file)
            
            # Clean markdown for text parsing
            content = pdf_parser.clean_text(markdown_content)
            
            if verbose:
                console.print(f"[green]Extracted text from PDF using pymupdf4llm[/green]")
                console.print(f"[dim]Found {len(structure_info.get('parts', []))} parts[/dim]")
                console.print(f"[dim]Found {len(structure_info.get('articles', []))} articles[/dim]")
                
                # Show parts found
                if structure_info.get('parts'):
                    console.print("\n[bold]Parts detected:[/bold]")
                    for part in structure_info['parts'][:5]:  # Show first 5
                        console.print(f"  - Part {part['number']}: {part['title'][:50]}...")
                    if len(structure_info['parts']) > 5:
                        console.print(f"  ... and {len(structure_info['parts']) - 5} more")
        else:
            # Read text file
            content = input_file.read_text(encoding='utf-8')
            structure_info = {}
            
            if verbose:
                console.print(f"[blue]Reading file:[/blue] {input_file}")
        
        # Create metadata
        metadata = DocumentMetadata(
            title=title or input_file.stem,
            document_type=doc_type,
            country=country,
            language=language
        )
        
        # Process document based on input format
        if as_json:
            data = json.loads(content)
            document = LegalDocument(**data)
            if verbose:
                console.print("[green]Loaded structured JSON document[/green]")
        elif parse:
            # Parse plain text document
            parser = DocumentParser()
            document = parser.parse(content, metadata)
            if verbose:
                console.print("[green]Parsed plain text document[/green]")
                _print_structure_summary(document)
        else:
            # Create simple document with content as single section
            from .models import Section
            document = LegalDocument(
                metadata=metadata,
                sections=[Section(
                    id="sec_1",
                    number="1",
                    content=content
                )]
            )
            if verbose:
                console.print("[yellow]Created simple document (use --parse for structure extraction)[/yellow]")
        
        # Convert to Akoma Ntoso XML
        converter = AkomaNtosoConverter()
        xml_string = converter.to_string(document, pretty_print=True)
        
        # Output handling
        if preview or not output:
            # Show preview
            console.print("\n[bold blue]Akoma Ntoso XML Output:[/bold blue]")
            syntax = Syntax(xml_string, "xml", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, expand=False))
            
            if not output and not preview:
                console.print("\n[yellow]Use -o/--output to save to file[/yellow]")
        
        if output:
            output.write_text(xml_string, encoding='utf-8')
            console.print(f"\n[green]Success:[/green] XML saved to: {output}")
        
    except FileNotFoundError:
        console.print(f"[red]Error:[/red] File not found: {input_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        console.print(f"[red]Error:[/red] Invalid JSON format: {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


def _print_structure_summary(document: LegalDocument):
    """Print a summary of the document structure."""
    summary = []
    
    if document.chapters:
        summary.append(f"Chapters: {len(document.chapters)}")
        total_articles = sum(len(ch.articles) for ch in document.chapters)
        summary.append(f"Articles: {total_articles}")
    elif document.articles:
        summary.append(f"Articles: {len(document.articles)}")
        total_sections = sum(len(art.sections) for art in document.articles)
        summary.append(f"Sections: {total_sections}")
    elif document.sections:
        summary.append(f"Sections: {len(document.sections)}")
    
    console.print(f"[dim]Structure: {', '.join(summary)}[/dim]")


if __name__ == "__main__":
    main()