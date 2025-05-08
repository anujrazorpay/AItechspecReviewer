import streamlit as st
from docx import Document
from pathlib import Path

def extract_template_headings(template_path: str):
    headings = []
    try:
        doc = Document(template_path)
        for para in doc.paragraphs:
            if para.style.name.startswith('Heading') and para.text.strip():
                headings.append((para.style.name, para.text.strip()))
    except Exception as e:
        st.error(f"Error reading template: {e}")
    return headings

def render_template_headings_display(template_path: str):
    st.markdown("### Template Sections (Headings)")
    headings = extract_template_headings(template_path)
    if not headings:
        st.info("No headings found in the template.")
        return
    for style, text in headings:
        st.markdown(f"- **{style}**: {text}") 