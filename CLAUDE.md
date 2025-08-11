# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Legal2AKN is a Python library and CLI tool for converting Indian legal documents to Akoma Ntoso XML format. Akoma Ntoso is an international XML standard for representing legal documents in a machine-readable format. 

**Current Status**: The code is currently optimized for the Indian Constitution's structure. While it partially works for other Acts, modifications are needed to handle the diverse structures found in regular Indian legislation.

## Core Architecture

The project follows a modular architecture with clear separation of concerns:

1. **Models** (`legal2akn/models.py`): Pydantic data models representing the hierarchical structure of Indian legal documents. Two main structures are supported:
   - **Acts**: Chapter → Section → Subsection → Clause
   - **Constitution**: Part → Article → Clause
   - Key models: `DocumentMetadata`, `LegalDocument`, `Chapter`, `Article`, `Section`

2. **Parser** (`legal2akn/parser.py`): Extracts structure from plain text using regex patterns to identify the hierarchical elements specific to Indian legal documents. The parser recognizes patterns common in Indian Acts and Constitutional text.

3. **Converter** (`legal2akn/converter.py`): Transforms the structured document model into Akoma Ntoso XML using lxml. Handles the complex XML namespace and element structure required by the Akoma Ntoso standard while preserving Indian legal document conventions.

4. **CLI** (`legal2akn/cli.py`): Click-based command-line interface with rich terminal output. Supports multiple input formats (plain text, JSON) and processing modes.

## Indian Legal Document Structures

### Currently Supported (Optimized for Constitution)
- **Parts**: Major divisions (e.g., "PART I - THE UNION AND ITS TERRITORY")
- **Articles**: Primary constitutional provisions (e.g., "Article 1. Name and territory of the Union")
- **Clauses**: Numbered subdivisions within articles (e.g., "(1)", "(2)")

### Planned Support for Various Document Types

| Document Type | Structure Elements | Status |
|--------------|-------------------|--------|
| **Constitution** | Parts → Articles → Clauses | ✅ Fully Supported |
| **Acts** | Chapters → Sections → Sub-sections → Clauses | ⚠️ Partial Support |
| **Rules/Regulations** | Rules → Sub-rules → Clauses | 🔄 Planned |
| **Ordinances** | Similar to Acts | 🔄 Planned |
| **Bills** | Clauses → Sub-clauses | 🔄 Planned |
| **Amendments** | Amendment sections | 🔄 Planned |

### Special Elements to Handle
- **Provisos**: "Provided that..." clauses
- **Explanations**: Clarifying text after sections
- **Exceptions**: Special case handling
- **Illustrations**: Examples within legal text
- **Schedules**: Tabular data and lists
- **Definitions**: Special parsing for definition sections

## Development Commands

### Install dependencies
```bash
pip install -e .
```

### Run the CLI
```bash
# Convert Indian Act with structure parsing
python -m legal2akn.cli act.txt -o act.xml --parse --country IN

# Convert Constitution text
python -m legal2akn.cli constitution.txt -o constitution.xml --parse --type constitution --country IN

# Convert from JSON input
python -m legal2akn.cli structured.json -o output.xml --json --country IN

# Preview output without saving
python -m legal2akn.cli document.txt --preview
```

### Testing
```bash
# Run tests (when test files are added)
pytest

# Run tests with coverage
pytest --cov=legal2akn
```

## Key Technical Details

- **Python 3.11+** required
- **Dependencies**: lxml (XML processing), click (CLI), pydantic (data validation), rich (terminal output)
- **XML Namespace**: Uses Akoma Ntoso 3.0 namespace (`http://docs.oasis-open.org/legaldocml/ns/akn/3.0`)
- **Document Types**: Supports Indian legal document types (act, constitution, bill, ordinance, regulation)
- **Country Code**: Default set to 'IN' for India
- **Parsing Strategy**: Uses regex patterns tailored for Indian legal document formatting conventions
- **Output Format**: Generates valid Akoma Ntoso XML with proper FRBR metadata structure

## Input/Output Flow

1. **Input**: Plain text or JSON structured Indian legal document
2. **Parsing** (if plain text): Extract hierarchical structure using patterns specific to Indian legal formatting
3. **Modeling**: Build Pydantic models representing document structure
4. **Conversion**: Transform models to Akoma Ntoso XML elements
5. **Output**: Valid Akoma Ntoso XML file or preview

## Common Tasks

When modifying the parser, ensure it handles Indian legal document conventions including:
- Section numbering with periods (e.g., "1.", "2A.", "3-B")
- Subsection markers in parentheses (e.g., "(1)", "(2)")
- Clause markers with lowercase letters (e.g., "(a)", "(b)")
- Roman numerals for Parts in Constitution
- Special provisions like "Provided that", "Provided further that"
- Explanation sections following main provisions

When extending the converter, ensure compliance with the Akoma Ntoso schema while maintaining Indian legal document structure. The converter should properly map Indian document elements to their Akoma Ntoso equivalents.

## Future Enhancements Roadmap

### High Priority
1. **Document Type Detection**: Auto-detect whether input is Act, Rules, Regulation, or Constitution
2. **Enhanced Parser**: Handle varied structures across different types of legislation
3. **Metadata Extraction**: Extract Act numbers, years, enactment dates, ministry information

### Medium Priority
1. **Schedule Support**: Parse and convert schedule tables and lists
2. **Amendment Tracking**: Handle amendment acts and track changes
3. **PDF Support**: Direct PDF to Akoma Ntoso conversion
4. **Validation**: Validate output against Akoma Ntoso schema

### Nice to Have
1. **OCR Support**: Handle scanned PDFs
2. **Multilingual Support**: Handle documents in Hindi and regional languages
3. **Diff Viewer**: Compare different versions of acts
4. **Database Export**: Export to database format for legal information systems