# ASTRA Tools

Tools for converting ASTRA research reports (JSON) to Quarto and Markdown formats with proper bibliography support.

## Overview

This package provides command-line tools to convert research artifacts exported from [ASTRA](https://astra.allen.ai) into well-formatted academic documents:

- **JSON to Quarto (.qmd)**: Convert ASTRA JSON reports to Quarto markdown with full bibliography support, proper citations, and APA formatting
- **JSON to Markdown (.md)**: Convert ASTRA JSON reports to plain markdown with inline references
- **Bibliography Key Regeneration**: Standardize BibTeX citation keys using a consistent naming convention

## Installation

### For Development (Recommended for Personal Use)

Install the package in editable mode from this subdirectory:

```bash
# From the GenerativeCausalInference directory
pip install -e ./astra-tools
```

This makes the `astra-convert` command available across all your projects while allowing you to modify the source code.

### For Use in Other Projects

You can also install directly from the path:

```bash
pip install -e /path/to/GenerativeCausalInference/astra-tools
```

### Verifying Installation

Check that the tool is installed correctly:

```bash
astra-convert --version
astra-convert --help
```

## Usage

### Converting JSON to Quarto Markdown

Convert an ASTRA JSON export to a Quarto-formatted document with bibliography support:

```bash
astra-convert json-to-qmd report.json
```

**Requirements:**
- A `.bib` file with the same base name as your JSON file (e.g., `report.bib` for `report.json`)
- Download the `.bib` file from ASTRA when you export your research report

**What it does:**
- Converts ASTRA's JSON structure to Quarto markdown format
- Maps inline `<Paper>` citations to proper Quarto citations (`[@AuthorYear]`)
- Creates YAML front matter with bibliography configuration
- **Automatically copies bundled APA CSL file** to your project directory
- Adds document metadata and table of contents
- Generates a references summary table
- Creates a formatted references section

**Citation Style:** The tool includes a bundled `apa.csl` file that is automatically copied to your project directory. You can use a custom CSL file with:

```bash
astra-convert json-to-qmd report.json --csl-file custom-style.csl
```

**Output:** Creates `report.qmd` and `apa.csl` (if not already present) that can be rendered with Quarto:

```bash
quarto render report.qmd --to pdf
```

### Converting JSON to Plain Markdown

For simpler markdown output without bibliography integration:

```bash
astra-convert json-to-md report.json
```

**Output:** Creates `report.md` with embedded reference information

### Regenerating Bibliography Keys

Standardize citation keys in your `.bib` file using the convention:
`FirstAuthorLastNameYearFirstThreeSubstantialTitleWords`

```bash
# Create a new file with regenerated keys (safe, creates .new.bib)
astra-convert regenerate-bib report.bib

# Modify in-place with automatic backup
astra-convert regenerate-bib report.bib --inplace

# Show the key mappings
astra-convert regenerate-bib report.bib --show-mapping

# Save key mappings to a file
astra-convert regenerate-bib report.bib --save-mapping
```

**Example key transformation:**
- Old: `DBLP:conf/nips/YancosekBBB24`
- New: `Yancosek2024BeaconBayesianEvolutionary`

## Command Reference

### `json-to-qmd`

```bash
astra-convert json-to-qmd [OPTIONS] JSON_FILE

Arguments:
  JSON_FILE              Path to ASTRA JSON file

Options:
  --no-bib               Skip bibliography file check and proceed without prompting
  --csl-file CSL_FILE    Path to custom CSL file (default: uses bundled apa.csl)
  -v, --verbose          Show detailed output and error traces
```

### `json-to-md`

```bash
astra-convert json-to-md [OPTIONS] JSON_FILE

Arguments:
  JSON_FILE       Path to ASTRA JSON file

Options:
  -v, --verbose  Show detailed output and error traces
```

### `regenerate-bib`

```bash
astra-convert regenerate-bib [OPTIONS] BIB_FILE

Arguments:
  BIB_FILE           Path to .bib file

Options:
  --inplace          Modify file in place (creates .backup)
  --show-mapping     Display key mappings after regeneration
  --save-mapping     Save key mappings to a text file
  -v, --verbose      Show detailed output and error traces
```

## Typical Workflow

1. **Export from ASTRA**: Download both the JSON and BibTeX files from your ASTRA research report

2. **Regenerate citation keys** (optional but recommended):
   ```bash
   astra-convert regenerate-bib report.bib --inplace
   ```

3. **Convert to Quarto**:
   ```bash
   astra-convert json-to-qmd report.json
   ```

4. **Render with Quarto**:
   ```bash
   quarto render report.qmd --to pdf
   ```

## File Organization

When working with ASTRA exports, organize files like this:

```
research-project/
├── 2025-01-15-literature-review.json
├── 2025-01-15-literature-review.bib
├── apa.csl                            (automatically copied)
├── 2025-01-15-literature-review.qmd  (generated)
└── 2025-01-15-literature-review.pdf  (rendered by Quarto)
```

## Features

### Smart Citation Mapping

The tool automatically maps ASTRA's citation format to your bibliography:
- Handles various citation formats: `(Author, 2024)`, `Author2024`, `Authoretal2024`
- Fuzzy matching for robust citation resolution
- Fallback mechanisms for unmatched citations

### Clean Formatting

- Removes ASTRA's internal `<Model>` tags
- Preserves document structure and section hierarchy
- Adds TL;DR callouts for section summaries
- Creates professional document metadata

### Bibliography Support

- Auto-detects `.bib` files using multiple naming patterns
- **Bundles APA CSL file** - automatically copied to your project
- Configures Quarto for APA citation style
- Supports custom CSL files for other citation styles
- Generates reference summary tables
- Maintains citation integrity
- Smart CSL file management (only copies if missing or different)

## Requirements

- Python 3.8 or higher
- [Quarto](https://quarto.org) (for rendering `.qmd` files)
- No external Python dependencies (uses only standard library)

## Development

### Running from Source

```bash
# Install in editable mode
pip install -e .

# Run tests (when available)
pytest

# Format code
black src/

# Type checking
mypy src/
```

### Package Structure

```
astra-tools/
├── pyproject.toml          # Package configuration
├── README.md               # This file
├── src/
│   └── astra_tools/
│       ├── __init__.py     # Package exports
│       ├── cli.py          # Command-line interface
│       ├── data/           # Bundled resources
│       │   └── apa.csl     # APA citation style
│       ├── converters/     # Format converters
│       │   ├── json_to_qmd.py
│       │   └── json_to_md.py
│       └── bib/            # Bibliography tools
│           └── regenerate_keys.py
└── tests/                  # Test suite (TBD)
```

## Troubleshooting

### "Bibliography file not found"

Make sure you've downloaded the `.bib` file from ASTRA and saved it with the same base name as your JSON file:
- JSON: `report.json`
- BibTeX: `report.bib`

Both files should be in the same directory.

### Citations not rendering

1. Ensure you have a valid `.bib` file
2. Run `regenerate-bib` to standardize citation keys
3. The `apa.csl` file should be automatically copied - if not, try reinstalling: `pip install -e ./astra-tools --force-reinstall`
4. Verify Quarto is installed: `quarto --version`

### Using a different citation style

To use a different citation style (e.g., Chicago, MLA):

1. Download your desired CSL file from the [Zotero Style Repository](https://www.zotero.org/styles)
2. Use the `--csl-file` option:
   ```bash
   astra-convert json-to-qmd report.json --csl-file chicago-author-date.csl
   ```

### Command not found: `astra-convert`

Reinstall the package:
```bash
pip install -e ./astra-tools
```

Or check your PATH includes Python's script directory.

## Future Development

When this package matures, it can be:
- Extracted to a standalone repository
- Published to PyPI for easy installation: `pip install astra-tools`
- Distributed to the research community
- Extended with additional export formats

## License

This project is part of the GenerativeCausalInference research project.

## Related Resources

- [ASTRA](https://astra.allen.ai) - AI-powered research assistant
- [Quarto](https://quarto.org) - Scientific and technical publishing system
- [BibTeX](http://www.bibtex.org) - Reference management for LaTeX
