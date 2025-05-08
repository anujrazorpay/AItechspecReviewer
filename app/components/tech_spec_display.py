import streamlit as st
from typing import Union, List, Tuple, Dict
from docx import Document
import re

def break_content_by_template_sections(content: Union[str, List[Union[str, Dict]]], template_headings: List[Tuple[str, str]]) -> Dict[str, List[Union[str, Dict]]]:
    """
    Break content into sections based on template headings.
    Returns a dict: {heading_text: [content_lines]}
    """
    heading_texts = [h[1].strip() for h in template_headings]
    section_map = {h: [] for h in heading_texts}
    found_sections = set()
    # Flatten content to lines/blocks
    if isinstance(content, list):
        blocks = content
    else:
        blocks = content.split('\n')
    # Find all heading indices in the document
    indices = []
    for idx, block in enumerate(blocks):
        if isinstance(block, str):
            for h in heading_texts:
                if block.strip().lower() == h.lower():
                    indices.append((idx, h))
    indices.sort()
    for i, (start_idx, heading) in enumerate(indices):
        end_idx = indices[i+1][0] if i+1 < len(indices) else len(blocks)
        section_map[heading] = [b for b in blocks[start_idx+1:end_idx] if (isinstance(b, str) and b.strip()) or (isinstance(b, dict) and b.get('type') == 'table')]
        found_sections.add(heading)
    return section_map, found_sections

def extract_template_section_content(template_path: str, template_headings: List[Tuple[str, str]]) -> Dict[str, List[str]]:
    doc = Document(template_path)
    lines = [p.text for p in doc.paragraphs if isinstance(p.text, str) and p.text.strip()]
    heading_texts = [h[1].strip() for h in template_headings]
    section_map = {h: [] for h in heading_texts}
    indices = []
    for idx, line in enumerate(lines):
        if isinstance(line, str):
            for h in heading_texts:
                if line.strip().lower() == h.lower():
                    indices.append((idx, h))
    indices.sort()
    for i, (start_idx, heading) in enumerate(indices):
        end_idx = indices[i+1][0] if i+1 < len(indices) else len(lines)
        section_map[heading] = [l for l in lines[start_idx+1:end_idx] if isinstance(l, str) and l.strip()]
    return section_map

def is_content_missing_or_copied(section_content: List[Union[str, Dict]], template_content: List[str]) -> bool:
    # If no content, mark as missing
    if not section_content:
        return True
    # Flatten section content to text for comparison
    doc_text = ' '.join([
        b.strip().lower() if isinstance(b, str) else (b.get('text', '').strip().lower() if isinstance(b.get('text', ''), str) else '')
        for b in section_content if (isinstance(b, str) and b.strip()) or (isinstance(b, dict) and b.get('type') == 'table' and isinstance(b.get('text', ''), str) and b.get('text', '').strip())
    ])
    template_text = ' '.join([l.strip().lower() for l in template_content if isinstance(l, str) and l.strip()])
    # If content is very similar (e.g., >90% match), mark as missing
    if template_text and doc_text and (doc_text == template_text or (len(doc_text) > 20 and doc_text in template_text)):
        return True
    return False

def render_tech_spec_display(content: Union[str, List[Union[str, Dict]]], template_headings: List[Tuple[str, str]], template_path: str):
    """
    Display the document content broken into template sections, showing present/missing.
    """
    st.markdown("### Document Content by Template Sections")
    section_map, found_sections = break_content_by_template_sections(content, template_headings)
    template_section_map = extract_template_section_content(template_path, template_headings)
    for style, heading in template_headings:
        doc_section = section_map.get(heading, [])
        template_section = template_section_map.get(heading, [])
        if heading in found_sections:
            if is_content_missing_or_copied(doc_section, template_section):
                st.markdown(f"#### {heading} :red_circle: (Missing or Copy-Paste)")
                st.info("Section is empty or appears to be copy-pasted from the template.")
            else:
                st.markdown(f"#### {heading}")
                for block in doc_section:
                    if isinstance(block, str):
                        st.write(block)
                    elif isinstance(block, dict) and block.get('type') == 'table':
                        st.write("**Table:**")
                        st.table(block['data'])
                        st.caption("Table as text (for AI):")
                        st.code(block['text'])
        else:
            st.markdown(f"#### {heading} :red_circle: (Missing)")
            st.info("Section not found in uploaded document.")
        st.markdown("---") 