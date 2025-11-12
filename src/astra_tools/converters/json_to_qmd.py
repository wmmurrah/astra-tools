"""
Convert JSON artifact to Quarto markdown (.qmd) format with proper bibliography citations
"""
import json
import os
import re
import glob
import shutil
from pathlib import Path
try:
    from importlib.resources import files
except ImportError:
    # Fallback for Python < 3.9
    from importlib_resources import files


def get_bundled_csl_file():
    """Get path to bundled APA CSL file"""
    try:
        # Python 3.9+
        package_files = files('astra_tools')
        csl_file = package_files / 'data' / 'apa.csl'
        return str(csl_file)
    except Exception:
        # Fallback: look for CSL in package directory
        package_dir = Path(__file__).parent.parent
        csl_file = package_dir / 'data' / 'apa.csl'
        if csl_file.exists():
            return str(csl_file)
        return None


def copy_csl_file(target_dir, csl_file_path=None):
    """
    Copy CSL file to target directory

    Args:
        target_dir: Directory where the .qmd file will be created
        csl_file_path: Optional custom CSL file path. If None, uses bundled apa.csl

    Returns:
        Name of the CSL file that was copied, or None if copy failed
    """
    if csl_file_path is None:
        # Use bundled CSL file
        bundled_csl = get_bundled_csl_file()
        if bundled_csl is None:
            print("⚠️  Warning: Could not find bundled apa.csl file")
            return None
        csl_file_path = bundled_csl

    if not os.path.exists(csl_file_path):
        print(f"⚠️  Warning: CSL file not found: {csl_file_path}")
        return None

    # Get target filename
    csl_filename = os.path.basename(csl_file_path)
    target_path = os.path.join(target_dir, csl_filename)

    # Check if file already exists and is identical
    if os.path.exists(target_path):
        # File exists, check if it's the same
        try:
            with open(csl_file_path, 'rb') as src, open(target_path, 'rb') as dst:
                if src.read() == dst.read():
                    # Files are identical, no need to copy
                    return csl_filename
        except Exception:
            pass  # If comparison fails, proceed with copy

    # Copy the CSL file
    try:
        shutil.copy2(csl_file_path, target_path)
        print(f"✅ Copied CSL file: {csl_filename}")
        return csl_filename
    except Exception as e:
        print(f"⚠️  Warning: Could not copy CSL file: {e}")
        return None


def check_bib_file(json_file_path):
    """Check if corresponding .bib file exists"""
    # Try exact match first
    bib_file = os.path.splitext(json_file_path)[0] + '.bib'

    if os.path.exists(bib_file):
        return bib_file

    # Try alternate naming patterns (e.g., - vs _ before extension)
    # Extract directory and base name
    json_dir = os.path.dirname(json_file_path)
    json_base = os.path.basename(json_file_path)
    json_name_no_ext = os.path.splitext(json_base)[0]

    # Try replacing last - with _ (common ASTRA pattern)
    if '-' in json_name_no_ext:
        # Replace last hyphen before underscore with underscore
        parts = json_name_no_ext.rsplit('-', 1)
        if len(parts) == 2:
            alt_name = parts[0] + '_' + parts[1] + '.bib'
            alt_path = os.path.join(json_dir, alt_name)
            if os.path.exists(alt_path):
                return alt_path

    # Try looking for any .bib file in the same directory
    if json_dir:
        bib_files = glob.glob(os.path.join(json_dir, '*.bib'))
        if bib_files:
            # Filter out backup and mapping files
            bib_files = [f for f in bib_files if not f.endswith(('.backup', '.new.bib'))]
            # If there's only one, use it
            if len(bib_files) == 1:
                print(f"Found bibliography file: {os.path.basename(bib_files[0])}")
                return bib_files[0]
            # If multiple, look for one with similar name
            json_prefix = json_name_no_ext.split('_')[0].split('-')[0]
            for bib in bib_files:
                if json_prefix in os.path.basename(bib):
                    print(f"Found bibliography file: {os.path.basename(bib)}")
                    return bib

    print(f"\n⚠️  WARNING: Bibliography file not found!")
    print(f"Expected: {bib_file}")
    print(f"\nPlease download the .bib file from ASTRA (astra.allen.ai)")
    print(f"and save it with the same name as your JSON file:")
    print(f"  {os.path.basename(bib_file)}")
    print(f"\nThe .bib file should be in the same directory as the JSON file.")
    return None


def extract_citation_mapping_from_bib(bib_file_path):
    """
    Extract citation keys and build mapping from JSON citation IDs to bib keys.
    Returns: dict mapping normalized citation IDs to actual bib keys
    """
    citation_mapping = {}

    try:
        with open(bib_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split into entries
        entries = re.split(r'(?=@\w+\s*\{)', content)

        for entry in entries:
            if not entry.strip() or not entry.startswith('@'):
                continue

            # Extract citation key
            key_match = re.match(r'@\w+\s*\{\s*([^,\s]+)\s*,', entry)
            if not key_match:
                continue

            cite_key = key_match.group(1).strip()

            # Extract author and year for matching
            author_match = re.search(r'author\s*=\s*[{"]([^}"]*)["}]', entry, re.IGNORECASE)
            year_match = re.search(r'year\s*=\s*[{"]?(\d{4})["}]?', entry)

            if not author_match or not year_match:
                continue

            author_field = author_match.group(1)
            year = year_match.group(1)

            # Extract first author last name
            authors = re.split(r'\s+and\s+', author_field, flags=re.IGNORECASE)
            first_author_field = authors[0].strip()

            # Handle "Last, First" or "First Last"
            if ',' in first_author_field:
                first_author_last = first_author_field.split(',')[0].strip()
            else:
                parts = first_author_field.split()
                first_author_last = parts[-1].strip() if parts else ""

            # Remove special characters
            first_author_last = re.sub(r'[^\w]', '', first_author_last)

            if not first_author_last:
                continue

            # Create various possible JSON citation ID formats
            variations = [
                f"{first_author_last}{year}",  # Yancosek2024
                f"{first_author_last}etal{year}",  # Yancoseketal2024
                f"({first_author_last} et al., {year})",  # (Yancosek et al., 2024)
                f"({first_author_last}, {year})",  # (Yancosek, 2024)
                f"{first_author_last} et al., {year}",  # Yancosek et al., 2024
                f"{first_author_last}, {year}",  # Yancosek, 2024
            ]

            # Store all variations mapping to the actual bib key
            for variation in variations:
                citation_mapping[variation.lower().strip()] = cite_key

    except Exception as e:
        print(f"Warning: Could not parse .bib file: {e}")

    return citation_mapping


def convert_inline_citations(text, citation_mapping=None):
    """
    Convert inline <Paper> tags to Quarto citation format [@key]
    """
    # Pattern to match Paper tags with paperTitle attribute
    pattern = r'<Paper[^>]*paperTitle="([^"]*)"[^>]*></Paper>'

    def replace_citation(match):
        paper_title = match.group(1).strip()

        if citation_mapping:
            # Try to find match in mapping
            lookup_key = paper_title.lower().strip()
            if lookup_key in citation_mapping:
                return f"[@{citation_mapping[lookup_key]}]"

            # Try removing parentheses
            lookup_key_no_parens = paper_title.strip('()').lower().strip()
            if lookup_key_no_parens in citation_mapping:
                return f"[@{citation_mapping[lookup_key_no_parens]}]"

        # Fallback: extract author and year for a basic key
        match = re.match(r'(?:\()?([A-Za-z]+)(?:\s+et\s+al\.)?,?\s+(\d{4})(?:\))?', paper_title)
        if match:
            author = match.group(1)
            year = match.group(2)
            return f"[@{author}{year}]"

        # Last resort: create safe key
        safe_key = re.sub(r'[^\w]', '', paper_title)
        return f"[@{safe_key}]"

    return re.sub(pattern, replace_citation, text)


def convert_model_tags(text):
    """Remove Model tags that represent AI-generated content markers"""
    # Remove Model tags (both self-closing and with content)
    pattern = r'<Model[^>]*>.*?</Model>'
    text = re.sub(pattern, '', text)

    # Also handle self-closing tags if any
    pattern2 = r'<Model[^>]*/?>'
    text = re.sub(pattern2, '', text)

    # Clean up any double spaces that result (but preserve newlines)
    text = re.sub(r'[ \t]{2,}', ' ', text)

    # Clean up space before punctuation
    text = re.sub(r'\s+([.,;:!?])', r'\1', text)

    return text.strip()


def build_bib_entries_summary(sections, citation_mapping=None):
    """Build a summary table of references cited in the document"""
    all_citations = {}

    for section in sections:
        citations = section.get('citations', [])
        for citation in citations:
            citation_id = citation.get('id', '')
            if citation_id and citation_id not in all_citations:
                all_citations[citation_id] = citation

    if not all_citations:
        return ""

    # Build a simple table
    md_content = "\n## References Summary\n\n"
    md_content += "The following sources are cited in this report and detailed in the accompanying `.bib` file:\n\n"

    md_content += "| Citation | Title | Year | Venue |\n"
    md_content += "|----------|-------|------|-------|\n"

    for citation_id in sorted(all_citations.keys()):
        citation = all_citations[citation_id]
        paper = citation.get('paper', {})

        title = paper.get('title', 'Unknown Title')
        year = paper.get('year', 'Unknown')
        venue = paper.get('venue', 'N/A')

        # Truncate long titles
        if len(title) > 60:
            title = title[:57] + "..."

        # Get actual bib key if we have mapping
        if citation_mapping:
            lookup_key = citation_id.lower().strip()
            cite_key = citation_mapping.get(lookup_key, citation_id)
        else:
            # Fallback normalization
            match = re.match(r'(?:\()?([A-Za-z]+)(?:\s+et\s+al\.)?,?\s+(\d{4})(?:\))?', citation_id)
            if match:
                author = match.group(1)
                year_val = match.group(2)
                cite_key = f"{author}{year_val}"
            else:
                cite_key = re.sub(r'[^\w]', '', citation_id)

        md_content += f"| `@{cite_key}` | {title} | {year} | {venue} |\n"

    return md_content


def convert_json_to_qmd(json_file_path, bib_file_path=None, csl_file_path=None):
    """
    Convert JSON artifact to Quarto markdown with bibliography citations

    Args:
        json_file_path: Path to ASTRA JSON file
        bib_file_path: Optional path to .bib file (auto-detected if None)
        csl_file_path: Optional path to custom CSL file (uses bundled apa.csl if None)

    Returns:
        Tuple of (markdown_content, output_qmd_path, csl_filename)
    """
    # Auto-detect bib file if not provided
    if bib_file_path is None:
        bib_file_path = check_bib_file(json_file_path)

    # Get output directory for CSL file
    output_dir = os.path.dirname(json_file_path) or '.'

    # Copy CSL file to output directory
    csl_filename = copy_csl_file(output_dir, csl_file_path)
    if csl_filename is None:
        csl_filename = "apa.csl"  # Use default name even if copy failed

    # Read JSON file
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract citation mapping from .bib file if available
    citation_mapping = {}
    if bib_file_path:
        citation_mapping = extract_citation_mapping_from_bib(bib_file_path)
        print(f"Found {len(set(citation_mapping.values()))} unique citation keys in bibliography")
        print(f"Built {len(citation_mapping)} citation mappings")

    # Extract metadata
    query = data.get('query', '')
    report_type = data.get('type', 'Report')

    # Get relative path to bib file for the YAML header
    bib_basename = os.path.basename(bib_file_path) if bib_file_path else "references.bib"

    # Start building markdown content with Quarto YAML front matter
    md_content = "---\n"
    md_content += f'title: "ASTRA {report_type}: {query if query else "Research Report"}"\n'
    md_content += "format:\n"
    md_content += "  pdf:\n"
    md_content += "    toc: true\n"
    md_content += "    number-sections: true\n"

    if bib_file_path:
        md_content += f"bibliography: {bib_basename}\n"
        md_content += f"csl: {csl_filename}\n"
        md_content += "link-citations: true\n"

    md_content += "---\n\n"

    # Add metadata section
    md_content += "## Document Information\n\n"
    md_content += f"**Report ID:** `{data.get('id', 'Unknown')}`\n\n"

    filename_parts = os.path.basename(json_file_path).split('-')
    if len(filename_parts) >= 3:
        date_str = f"{filename_parts[0]}-{filename_parts[1]}-{filename_parts[2]}"
        md_content += f"**Generated:** {date_str}\n\n"

    if query:
        md_content += f"**Research Question:** {query}\n\n"

    md_content += "---\n\n"

    # Process sections
    sections = data.get('sections', [])

    for section in sections:
        section_title = section.get('title', 'Untitled Section')
        tldr = section.get('tldr', '')
        text = section.get('text', '')

        # Add section header
        md_content += f"## {section_title}\n\n"

        # Add TLDR if available
        if tldr:
            md_content += f"::: {{.callout-note}}\n"
            md_content += f"## TL;DR\n{tldr}\n"
            md_content += f":::\n\n"

        # Add main text with inline citations
        if text:
            # First remove Model tags
            clean_text = convert_model_tags(text)
            # Then convert inline citations to Quarto format
            clean_text = convert_inline_citations(clean_text, citation_mapping)
            md_content += f"{clean_text}\n\n"

    # Add references summary table
    if bib_file_path:
        md_content += build_bib_entries_summary(sections, citation_mapping)
        md_content += "\n## References\n\n"
        md_content += "::: {#refs}\n:::\n"
    else:
        md_content += "\n**Note:** Bibliography file not found. Citations may not render correctly.\n"

    # Generate output filename
    base_name = os.path.splitext(json_file_path)[0]
    qmd_file = f"{base_name}.qmd"

    return md_content, qmd_file, csl_filename
