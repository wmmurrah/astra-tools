"""
Convert JSON artifact to markdown format with inline citations and references
"""
import json
import os
import re


def extract_paper_info(text):
    """Extract paper references from XML-like tags in text"""
    paper_pattern = r'<Paper[^>]*paperTitle="([^"]*)"[^>]*></Paper>'
    papers = re.findall(paper_pattern, text)
    return papers


def convert_inline_citations(text):
    """Convert inline <Paper> tags to markdown citation format"""
    # Pattern to match Paper tags with attributes
    pattern = r'<Paper[^>]*paperTitle="([^"]*)"[^>]*></Paper>'

    # Replace with markdown citation format
    def replace_citation(match):
        paper_title = match.group(1)
        # Extract just the author-year from the title like "(Author et al., 2024)"
        return f"{paper_title}"

    return re.sub(pattern, replace_citation, text)


def convert_model_tags(text):
    """Remove Model tags that represent AI-generated content markers"""
    pattern = r'<Model[^>]*>\.?</Model>'
    return re.sub(pattern, '', text)


def build_references_section(sections):
    """Build a comprehensive references section from all citations"""
    all_citations = {}

    for section in sections:
        citations = section.get('citations', [])
        for citation in citations:
            citation_id = citation.get('id', '')
            if citation_id and citation_id not in all_citations:
                all_citations[citation_id] = citation

    if not all_citations:
        return ""

    md_content = "\n## References\n\n"

    for citation_id in sorted(all_citations.keys()):
        citation = all_citations[citation_id]
        paper = citation.get('paper', {})

        title = paper.get('title', 'Unknown Title')
        year = paper.get('year', 'Unknown Year')
        venue = paper.get('venue', '')
        corpus_id = paper.get('corpusId', '')
        n_citations = paper.get('nCitations', 0)

        authors = paper.get('authors', [])
        author_names = [author.get('name', '') for author in authors]
        author_str = ', '.join(author_names) if author_names else 'Unknown Authors'

        # Format reference entry
        md_content += f"### {citation_id}\n\n"
        md_content += f"{author_str} ({year}). *{title}*"

        if venue:
            md_content += f". {venue}"
        md_content += ".\n\n"

        if corpus_id:
            md_content += f"- **Corpus ID:** {corpus_id}\n"
        if n_citations:
            md_content += f"- **Citations:** {n_citations}\n"

        # Add key snippets if available
        snippets = citation.get('snippets', [])
        if snippets:
            md_content += "\n**Key Excerpts:**\n\n"
            for i, snippet in enumerate(snippets, 1):
                # Limit snippet length for readability
                if len(snippet) > 500:
                    snippet = snippet[:500] + "..."
                md_content += f"{i}. {snippet}\n\n"

        md_content += "---\n\n"

    return md_content


def convert_json_to_markdown(json_file_path):
    """
    Convert JSON artifact to markdown with inline citations and references

    Args:
        json_file_path: Path to ASTRA JSON file

    Returns:
        Tuple of (markdown_content, output_md_path)
    """

    # Read JSON file
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract title from query or use default
    query = data.get('query', '')
    report_type = data.get('type', 'Report')

    # Start building markdown content with YAML front matter
    md_content = "---\n"
    md_content += f"title: \"ASTRA {report_type}: {query if query else 'Research Report'}\"\n"
    md_content += "format: pdf\n"
    md_content += "---\n\n"

    # Add metadata
    md_content += f"**Report ID:** {data.get('id', 'Unknown')}\n\n"

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
            md_content += f"**TL;DR:** {tldr}\n\n"

        # Add main text with inline citations
        if text:
            # First remove Model tags
            clean_text = convert_model_tags(text)
            # Then convert inline citations
            clean_text = convert_inline_citations(clean_text)
            md_content += f"{clean_text}\n\n"

    # Add comprehensive references section at the end
    md_content += build_references_section(sections)

    # Generate output filename
    base_name = os.path.splitext(json_file_path)[0]
    markdown_file = f"{base_name}.md"

    return md_content, markdown_file
