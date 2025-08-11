# Test Directory Structure

This directory contains test files and scripts for testing the Legal2AKN converter.

## Directory Structure

```
tests/
├── input/          # Place your test documents here
│   ├── *.pdf       # PDF files (e.g., constitution_1950.pdf)
│   ├── *.txt       # Plain text files
│   └── *.json      # Structured JSON documents
├── output/         # Generated Akoma Ntoso XML files will be saved here
├── expected/       # Reference/expected XML outputs for validation
└── temp/           # Temporary files during processing
```

## Usage

### 1. Place Test Documents

Add your test documents to the `input/` folder:
- **PDF files**: Place the 1950 Constitution PDF or other legal documents here
- **Text files**: Plain text versions of legal documents
- **JSON files**: Pre-structured legal documents in JSON format

### 2. Run Conversion

```powershell
# Using uv to run the CLI
# Convert a single PDF
uv run python -m legal2akn.cli tests/input/constitution_1950.pdf -o tests/output/constitution_1950.xml --parse

# Preview without saving
uv run python -m legal2akn.cli tests/input/constitution_1950.pdf --preview
```

### 3. Validate Output

Compare generated files in `output/` with expected results in `expected/`.

## Test Files Naming Convention

- `constitution_*.pdf/txt` - Constitution documents
- `act_*.pdf/txt` - Acts
- `rules_*.pdf/txt` - Rules and Regulations
- `bill_*.pdf/txt` - Bills
- `ordinance_*.pdf/txt` - Ordinances

## Sample Test Commands (PowerShell)

```powershell
# Test Constitution parsing
uv run python -m legal2akn.cli tests/input/constitution_1950.pdf -o tests/output/constitution_1950.xml --parse --type constitution --country IN

# Test Act parsing
uv run python -m legal2akn.cli tests/input/act_sample.txt -o tests/output/act_sample.xml --parse --type act --country IN

# Test JSON input
uv run python -m legal2akn.cli tests/input/structured_doc.json -o tests/output/structured_doc.xml --json --country IN

# Verbose mode for debugging
uv run python -m legal2akn.cli tests/input/constitution_1950.pdf -o tests/output/constitution_1950.xml --parse --verbose
```

## Notes

- The `output/` folder is gitignored to avoid committing generated files
- Place reference outputs in `expected/` for comparison
- Use `temp/` for any intermediate processing files
- All commands use `uv` for dependency management