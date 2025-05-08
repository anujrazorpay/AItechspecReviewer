import streamlit as st
import re
from typing import Dict, List, Union
from datetime import datetime

def extract_document_info(text: Union[str, List[Union[str, dict]]]) -> Dict:
    """Extract key information from the document. Accepts list (DOCX) or string (PDF/TXT)."""
    info = {
        'title': '',
        'version': '',
        'date': '',
        'authors': [],
        'status': '',
        'summary': '',
        'key_points': []
    }
    
    # If DOCX, text is a list of paragraphs/tables; if not, split into lines
    if isinstance(text, list):
        lines = [p.strip() for p in text if isinstance(p, str) and p.strip()]
    else:
        lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    # Extract title (first non-empty paragraph, not all uppercase, not too short)
    for line in lines[:10]:
        if line and len(line) > 3 and not line.isupper() and not any(char.isdigit() for char in line[:8]):
            info['title'] = line.strip()
            break
    
    # Extract version and date
    version_pattern = r'(?i)version\s*:?-?\s*(\d+\.\d+(\.\d+)?)'
    date_pattern = r'(?i)date\s*:?-?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\w+\s+\d{1,2},?\s+\d{4})'
    
    for line in lines:
        # Version
        version_match = re.search(version_pattern, line)
        if version_match:
            info['version'] = version_match.group(1)
        # Date
        date_match = re.search(date_pattern, line)
        if date_match:
            info['date'] = date_match.group(1)
        # Authors (look for patterns like "Author:", "By:", etc.)
        author_match = re.match(r'(?i)^(author|by|prepared by)\s*:?-?\s*(.+)', line)
        if author_match:
            authors = [a.strip() for a in author_match.group(2).split(',') if len(a.strip()) > 1]
            info['authors'].extend(authors)
        # Status
        status_match = re.match(r'(?i)^status\s*:?-?\s*(.+)', line)
        if status_match:
            info['status'] = status_match.group(1).strip()
    
    # Extract summary (look for a section header, then collect following paragraphs)
    summary_section = False
    for line in lines:
        if re.search(r'(?i)(executive summary|introduction|overview)', line):
            summary_section = True
            continue
        if summary_section:
            if re.match(r'^(\d+\.|[A-Z][a-z]+\s+\d+)', line):  # Stop at next section
                break
            info['summary'] += line.strip() + ' '
    
    # Extract key points (look for bullet points or numbered lists)
    for line in lines:
        if re.match(r'^[•\-\*]\s+', line) or re.match(r'^\d+\.\s+', line):
            point = re.sub(r'^[•\-\*]\s+', '', line).strip()
            point = re.sub(r'^\d+\.\s+', '', point).strip()
            if point and len(point) > 10:
                info['key_points'].append(point)
    
    return info

def render_document_info(text: Union[str, List[Union[str, dict]]]):
    """Render the extracted document information."""
    info = extract_document_info(text)
    
    with st.container():
        st.markdown("### Document Information")
        if info['title']:
            st.markdown(f"**Title:** {info['title']}")
        col1, col2 = st.columns(2)
        with col1:
            if info['version']:
                st.markdown(f"**Version:** {info['version']}")
        with col2:
            if info['date']:
                st.markdown(f"**Date:** {info['date']}")
        if info['authors']:
            st.markdown(f"**Authors:** {', '.join(info['authors'])}")
        if info['status']:
            st.markdown(f"**Status:** {info['status']}")
        if info['summary']:
            st.markdown("### Summary")
            st.write(info['summary'])
        if info['key_points']:
            st.markdown("### Key Points")
            for point in info['key_points']:
                st.markdown(f"• {point}")
        st.markdown("---") 