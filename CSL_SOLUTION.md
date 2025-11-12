# CSL File Handling Solution

## Problem
The `astra-tools` package generated `.qmd` files that required an `apa.csl` file to be present in the same directory for Quarto to render citations correctly. Users would get rendering errors if the CSL file was missing.

## Solution Implemented

### 1. Bundle CSL File with Package
- Added `docs/apa.csl` to the package at `src/astra_tools/data/apa.csl`
- Updated `pyproject.toml` to include package data files:
  ```toml
  [tool.setuptools.package-data]
  astra_tools = ["data/*.csl"]
  ```

### 2. Automatic CSL Copying
The `json_to_qmd.py` converter now:
- Automatically detects the bundled APA CSL file
- Copies it to the same directory as the output `.qmd` file
- Only copies if the file doesn't exist or is different (avoids unnecessary writes)
- Reports the CSL file status to the user

### 3. Custom CSL Support
Users can specify custom CSL files:
```bash
astra-convert json-to-qmd report.json --csl-file chicago-author-date.csl
```

This allows using different citation styles (Chicago, MLA, IEEE, etc.) downloaded from the [Zotero Style Repository](https://www.zotero.org/styles).

## Technical Implementation

### Key Functions

**`get_bundled_csl_file()`**
- Locates the bundled `apa.csl` file using Python 3.9+ `importlib.resources.files()`
- Falls back to path-based lookup for older Python versions
- Returns the full path to the bundled CSL file

**`copy_csl_file(target_dir, csl_file_path=None)`**
- Copies CSL file to the target directory
- Uses bundled CSL if no custom file specified
- Compares file contents to avoid redundant copies
- Returns the CSL filename for use in YAML front matter

**`convert_json_to_qmd(json_file_path, bib_file_path=None, csl_file_path=None)`**
- Enhanced to accept optional `csl_file_path` parameter
- Calls `copy_csl_file()` during conversion
- Includes CSL filename in YAML front matter
- Returns tuple: `(markdown_content, output_qmd_path, csl_filename)`

### CLI Changes

Added `--csl-file` option to `json-to-qmd` command:
```bash
astra-convert json-to-qmd --help

options:
  --csl-file CSL_FILE  Path to custom CSL file (default: uses bundled apa.csl)
```

## User Experience

### Before
1. User converts JSON to QMD
2. User tries to render with Quarto
3. **Error**: CSL file not found
4. User must manually copy `apa.csl` from somewhere
5. User renders successfully

### After
1. User converts JSON to QMD
2. **CSL file automatically copied** ✅
3. User renders successfully immediately

## Benefits

1. **Zero Configuration** - Works out of the box
2. **Cross-Platform** - CSL file travels with the package
3. **Flexible** - Supports custom citation styles
4. **Efficient** - Only copies when necessary
5. **User-Friendly** - Clear feedback about what's happening

## Testing

Verified with end-to-end test:
```bash
# Create test JSON file
astra-convert json-to-qmd test-report.json --no-bib

# Verify outputs:
# ✅ test-report.qmd created
# ✅ apa.csl copied (84KB, matches bundled version)
# ✅ YAML front matter includes: csl: apa.csl

# Run again:
# ✅ CSL file not copied again (detected as identical)
```

## Migration Notes

For users updating from older versions:
- No action required - the bundled CSL file works automatically
- Existing projects with `apa.csl` will not be overwritten (unless different)
- Custom CSL files can be specified with `--csl-file` flag

## Files Modified

1. `astra-tools/src/astra_tools/data/apa.csl` - New bundled CSL file
2. `astra-tools/pyproject.toml` - Added package data configuration
3. `astra-tools/src/astra_tools/converters/json_to_qmd.py` - Enhanced with CSL handling
4. `astra-tools/src/astra_tools/cli.py` - Added CLI option and updated output
5. `astra-tools/README.md` - Documented CSL file behavior
6. `astra-tools/.gitignore` - Excluded generated files

## Future Enhancements

Potential improvements:
- Bundle additional popular CSL files (Chicago, MLA, IEEE)
- Auto-download CSL files from Zotero repository by name
- Validate CSL file format before copying
- Support for CSL file search paths
