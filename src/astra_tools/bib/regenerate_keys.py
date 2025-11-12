"""
Regenerate citation keys in a .bib file following a consistent naming convention:
FirstAuthorLastNameYearFirstThreeSubstantialTitleWords

Example: Yancosek2024BeaconBayesianEvolutionary
"""
import re
import os


# Common words to skip in titles
SKIP_WORDS = {
    'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
    'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'should', 'could', 'may', 'might', 'must', 'can', 'using', 'via',
    'through', 'into', 'onto', 'upon', 'about', 'over', 'under', 'between',
    'among', 'during', 'before', 'after', 'above', 'below', 'this', 'that',
    'these', 'those', 'our', 'their', 'its', 'his', 'her'
}


def extract_author_lastname(author_field):
    """Extract the last name of the first author"""
    if not author_field:
        return "Unknown"

    # Remove braces and extra whitespace
    author_field = re.sub(r'[{}]', '', author_field).strip()

    # Split by 'and' to get first author
    authors = re.split(r'\s+and\s+', author_field, flags=re.IGNORECASE)
    first_author = authors[0].strip()

    # Handle different formats:
    # "Last, First" or "First Last" or "Last, F."
    if ',' in first_author:
        # Format: "Last, First" - take the part before comma
        lastname = first_author.split(',')[0].strip()
    else:
        # Format: "First Last" - take the last word
        parts = first_author.split()
        lastname = parts[-1].strip()

    # Remove any remaining special characters and capitalize
    lastname = re.sub(r'[^\w]', '', lastname)
    return lastname.capitalize()


def extract_year(year_field):
    """Extract year from year field"""
    if not year_field:
        return "NoYear"

    # Extract 4-digit year
    match = re.search(r'\d{4}', year_field)
    if match:
        return match.group(0)

    return "NoYear"


def extract_title_words(title_field, n_words=3):
    """Extract first N substantial words from title"""
    if not title_field:
        return "NoTitle"

    # Remove braces, quotes, and other special characters
    title = re.sub(r'[{}"\'`]', '', title_field)

    # Split into words
    words = re.findall(r'\b[a-zA-Z]+\b', title)

    # Filter out skip words and short words, capitalize first letter
    substantial_words = []
    for word in words:
        if len(word) > 2 and word.lower() not in SKIP_WORDS:
            substantial_words.append(word.capitalize())
            if len(substantial_words) >= n_words:
                break

    if not substantial_words:
        # If no substantial words found, use first few words regardless
        substantial_words = [w.capitalize() for w in words[:n_words]]

    return ''.join(substantial_words[:n_words])


def generate_citation_key(entry_type, fields):
    """Generate citation key from entry fields"""
    author = extract_author_lastname(fields.get('author', ''))
    year = extract_year(fields.get('year', ''))
    title_words = extract_title_words(fields.get('title', ''))

    return f"{author}{year}{title_words}"


def parse_bib_entry(entry_text):
    """Parse a single BibTeX entry into components"""
    # Extract entry type and old key
    match = re.match(r'@(\w+)\s*\{\s*([^,]+)\s*,', entry_text)
    if not match:
        return None

    entry_type = match.group(1)
    old_key = match.group(2).strip()

    # Extract all fields
    fields = {}
    field_pattern = r'(\w+)\s*=\s*[{"]([^}"]*)["}\s]*'
    for field_match in re.finditer(field_pattern, entry_text):
        field_name = field_match.group(1).lower()
        field_value = field_match.group(2)
        fields[field_name] = field_value

    return {
        'type': entry_type,
        'old_key': old_key,
        'fields': fields,
        'full_text': entry_text
    }


def regenerate_bib_keys(bib_content):
    """
    Regenerate all citation keys in bib file content

    Args:
        bib_content: String content of .bib file

    Returns:
        Tuple of (new_content, key_mapping) where key_mapping is dict of old_key -> new_key
    """
    # Split into entries
    entries = re.split(r'(?=@\w+\s*\{)', bib_content)

    new_content = ""
    key_mapping = {}  # old_key -> new_key

    for entry in entries:
        entry = entry.strip()
        if not entry or not entry.startswith('@'):
            # Keep preamble or comments
            if entry:
                new_content += entry + "\n\n"
            continue

        parsed = parse_bib_entry(entry)
        if not parsed:
            # Keep unparseable entries as-is
            new_content += entry + "\n\n"
            continue

        # Generate new key
        new_key = generate_citation_key(parsed['type'], parsed['fields'])

        # Handle duplicate keys by adding a suffix
        base_key = new_key
        suffix = 1
        while new_key in key_mapping.values():
            new_key = f"{base_key}_{suffix}"
            suffix += 1

        # Store mapping
        key_mapping[parsed['old_key']] = new_key

        # Replace old key with new key in entry text
        new_entry = re.sub(
            r'(@\w+\s*\{\s*)' + re.escape(parsed['old_key']),
            r'\1' + new_key,
            parsed['full_text']
        )

        new_content += new_entry + "\n\n"

    return new_content, key_mapping
