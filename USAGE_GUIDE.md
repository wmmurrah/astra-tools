# ASTRA Tools - Quick Start Guide

## What You've Created

You now have a reusable Python package that can convert ASTRA research reports across all your projects!

## Installation Status

✅ **Already installed** in your current environment as an editable package.

The `astra-convert` command is now available globally in this Python environment.

## Using in This Project

Since you're already in the project directory, you can use the tool immediately:

```bash
# Example: Convert an ASTRA export
astra-convert json-to-qmd path/to/your/report.json
```

## Using in Other Projects

Because you installed it in editable mode (`pip install -e`), the tool is available in ANY directory:

```bash
cd ~/Projects/AnotherResearchProject/
astra-convert json-to-qmd astra-export.json  # Works!
```

## Quick Reference

### Basic Conversion Workflow

1. **Download from ASTRA**: Get both JSON and BibTeX files
2. **Standardize citations** (optional):
   ```bash
   astra-convert regenerate-bib report.bib --inplace
   ```
3. **Convert to Quarto**:
   ```bash
   astra-convert json-to-qmd report.json
   ```
4. **Render**:
   ```bash
   quarto render report.qmd --to pdf
   ```

### All Available Commands

```bash
# Convert to Quarto (with bibliography)
astra-convert json-to-qmd report.json

# Convert to plain Markdown
astra-convert json-to-md report.json

# Regenerate citation keys (creates .new.bib)
astra-convert regenerate-bib report.bib

# Regenerate citation keys in-place (creates .backup)
astra-convert regenerate-bib report.bib --inplace

# Get help
astra-convert --help
astra-convert json-to-qmd --help
```

## Updating the Package

Since it's installed in editable mode, any changes you make to the source code in:
```
astra-tools/src/astra_tools/
```

Will be immediately available when you run `astra-convert` - no need to reinstall!

## Checking Installation

Verify it's working:

```bash
astra-convert --version
# Should show: astra-convert 0.1.0

which astra-convert
# Shows where the command is installed
```

## Future: Making it Public

When you're ready to share this with colleagues or make it public:

### Option 1: Share via Git

1. Copy `astra-tools/` directory to new location
2. Initialize git repository:
   ```bash
   cd /path/to/new/location/astra-tools
   git init
   git add .
   git commit -m "Initial commit"
   ```
3. Create GitHub repository
4. Push code
5. Others can install:
   ```bash
   pip install git+https://github.com/yourusername/astra-tools.git
   ```

### Option 2: Publish to PyPI

1. Create account on [PyPI](https://pypi.org)
2. Build the package:
   ```bash
   python -m build
   ```
3. Upload:
   ```bash
   python -m twine upload dist/*
   ```
4. Anyone can install:
   ```bash
   pip install astra-tools
   ```

## Troubleshooting

### Command not found

If `astra-convert` isn't found after installation:

```bash
# Reinstall
cd /path/to/GenerativeCausalInference/astra-tools
pip install -e .

# Check Python scripts directory is in PATH
python -m site --user-base
# Add the bin/ or Scripts/ subdirectory to your PATH
```

### Testing in a New Project

```bash
# Navigate to any other project
cd ~/Projects/SomeOtherProject/

# Verify command is available
astra-convert --version

# Use it!
astra-convert json-to-qmd my-astra-export.json
```

## What's Next

You can now:
- ✅ Use ASTRA tools in any project without copying scripts
- ✅ Install once, use everywhere
- ✅ Modify the source and changes take effect immediately
- ✅ Share with colleagues via git or PyPI
- ✅ Version control your conversion tools separately from research

Enjoy your new research workflow tool! 🎉
