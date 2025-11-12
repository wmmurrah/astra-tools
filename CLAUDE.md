# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**astra-tools** is a Python package for converting ASTRA research reports (JSON exports from astra.allen.ai) into well-formatted Quarto (.qmd) and Markdown (.md) documents with proper bibliography support.

The package is designed for researchers who use ASTRA for literature reviews and want to integrate those reviews into their academic writing workflows using Quarto.

## Key Architecture

### Package Structure
```
astra-tools/
├── src/astra_tools/           # Main package code
│   ├── cli.py                 # Command-line interface
│   ├── data/                  # Bundled resources
│   │   └── apa.csl            # APA citation style file
│   ├── converters/            # Format conversion modules
│   │   ├── json_to_qmd.py     # ASTRA JSON → Quarto converter
│   │   └── json_to_md.py      # ASTRA JSON → Markdown converter
│   └── bib/                   # Bibliography tools
│       └── regenerate_keys.py # BibTeX key standardization
├── pyproject.toml             # Package configuration
├── README.md                  # User documentation
├── USAGE_GUIDE.md            # Quick start guide
└── tests/                     # Test suite (to be developed)
```

### Core Functionality

1. **JSON to Quarto Conversion** (`json_to_qmd.py`)
   - Converts ASTRA JSON exports to Quarto markdown
   - Maps inline `<Paper>` citations to Quarto format (`[@key]`)
   - Handles bibliography file detection and linking
   - **Automatically copies bundled CSL file** to project directory
   - Creates YAML front matter with bibliography configuration

2. **Bibliography Management** (`regenerate_keys.py`)
   - Standardizes BibTeX citation keys
   - Convention: `FirstAuthorLastNameYearFirstThreeSubstantialTitleWords`
   - Handles duplicate keys with numeric suffixes

3. **CLI** (`cli.py`)
   - Main entry point: `astra-convert`
   - Subcommands: `json-to-qmd`, `json-to-md`, `regenerate-bib`
   - Uses argparse for command-line argument parsing

## Common Development Commands

### Development Setup
```bash
# Clone repository
git clone https://github.com/wmmurrah/astra-tools.git
cd astra-tools

# Install in editable mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

### Testing the CLI
```bash
# Test basic conversion
astra-convert json-to-qmd test-report.json

# Test with custom CSL
astra-convert json-to-qmd test-report.json --csl-file custom.csl

# Test bibliography regeneration
astra-convert regenerate-bib test-report.bib --show-mapping
```

### Code Quality
```bash
# Format code
black src/

# Type checking
mypy src/

# Run tests (when implemented)
pytest
```

## Design Principles

1. **Zero External Dependencies**: Uses only Python standard library (importlib, json, os, re, glob, shutil, pathlib, argparse)
   - This makes the package lightweight and easy to install
   - Reduces maintenance burden and compatibility issues

2. **Bundled Resources**: Includes APA CSL file for citation formatting
   - Configured in `pyproject.toml` under `[tool.setuptools.package-data]`
   - Automatically copied to project directories when needed

3. **Smart Defaults**: Auto-detects files and provides sensible fallbacks
   - Bibliography files: tries multiple naming patterns
   - CSL files: uses bundled APA by default
   - Citation mapping: fuzzy matching for robustness

4. **User-Friendly Output**: Clear status messages with emoji indicators
   - ✅ for success
   - ⚠️  for warnings
   - ❌ for errors

## File Naming Conventions

- Python modules: snake_case (e.g., `json_to_qmd.py`)
- Command-line tool: kebab-case (e.g., `astra-convert`)
- Package name: hyphenated (e.g., `astra-tools`)
- Import name: underscore (e.g., `import astra_tools`)

## Important Implementation Details

### CSL File Handling
The package bundles an APA CSL file and automatically copies it to the output directory. Key functions:

- `get_bundled_csl_file()`: Locates the bundled CSL using importlib.resources
- `copy_csl_file()`: Copies CSL to target directory with smart duplicate detection
- Only copies if file is missing or different (compares file contents)

See [CSL_SOLUTION.md](CSL_SOLUTION.md) for full technical details.

### Citation Mapping
The `extract_citation_mapping_from_bib()` function creates multiple variations of each citation for fuzzy matching:
- `Author2024`
- `Authoretal2024`
- `(Author et al., 2024)`
- `(Author, 2024)`

This handles ASTRA's varied citation formats.

## Development Guidelines

### Adding New Features
1. Consider whether it needs external dependencies (avoid if possible)
2. Update CLI in `cli.py` with new subcommands/options
3. Add comprehensive docstrings
4. Update README.md with usage examples
5. Test with real ASTRA exports

### Testing Philosophy (Future)
- Unit tests for conversion functions
- Integration tests with sample ASTRA JSON files
- CLI tests using subprocess
- Test coverage for edge cases (missing files, malformed JSON, etc.)

### Documentation Standards
- All public functions must have docstrings
- CLI help messages should be clear and concise
- README examples should be copy-paste ready
- Error messages should suggest solutions

## Common Tasks for Claude Code

### Modifying Converters
When editing conversion logic:
- Read the full converter module first
- Understand the JSON structure from ASTRA
- Test with sample files before committing
- Update return values and calling code consistently

### Adding CLI Options
When adding new command-line options:
1. Add argument in `cli.py` subparser
2. Update the corresponding `cmd_*` function
3. Pass parameter through to underlying function
4. Update README.md command reference
5. Update help text examples

### Handling Bibliography Files
When working with .bib file parsing:
- Use regex patterns that handle varied BibTeX formatting
- Test with both clean and messy bibliography files
- Handle missing or malformed entries gracefully
- Preserve original formatting when possible

## Integration with User Workflows

Users typically:
1. Export JSON and BibTeX files from ASTRA
2. Optionally run `regenerate-bib` to standardize keys
3. Run `json-to-qmd` to create Quarto document
4. Render with `quarto render file.qmd --to pdf`

The package should make steps 2-3 as seamless as possible.

## Version Management

- Use semantic versioning (MAJOR.MINOR.PATCH)
- Update version in `pyproject.toml`
- Current version: 0.1.0 (Alpha)
- Tag releases in git: `git tag v0.1.0`

## Related Resources

- [ASTRA](https://astra.allen.ai) - AI research assistant
- [Quarto](https://quarto.org) - Scientific publishing system
- [BibTeX](http://www.bibtex.org) - Reference management
- [CSL (Citation Style Language)](https://citationstyles.org/)
- [Zotero Style Repository](https://www.zotero.org/styles) - CSL file collection
