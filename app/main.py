import streamlit as st
import os
from app.config import APP_NAME, APP_ICON
from app.services.file_service import FileService
from app.services.bedrock_service import BedrockService
from app.components.file_uploader import render_file_uploader
from app.components.tech_spec_display import render_tech_spec_display, break_content_by_template_sections
from app.components.doc_info_extractor import render_document_info
from app.components.template_headings_display import render_template_headings_display, extract_template_headings
from app.models.structured_doc import SectionContent, DocumentStructure

def get_aws_region() -> str:
    """Get AWS region from Streamlit secrets or environment variable."""
    return st.secrets.get("AWS_REGION") or os.getenv("AWS_REGION", "us-east-1")

def build_document_structure(text, template_headings) -> DocumentStructure:
    """Build a DocumentStructure object from extracted text and template headings."""
    section_map, _ = break_content_by_template_sections(text, template_headings)
    sections = [
        SectionContent(header=heading, content_blocks=section_map.get(heading, []))
        for _, heading in template_headings
    ]
    return DocumentStructure(sections=sections)

def get_ai_prompt(doc_struct: DocumentStructure) -> str:
    """Generate the AI review prompt."""
    context = (
        "You are an expert technical reviewer. You are reviewing a technical specification document. "
        "The document describes a solution to a specific problem or requirement."
    )
    rules = (
        "- For each section:\n"
        "    - Carefully read the content.\n"
        "    - Score the section from 1 to 5 based on clarity, completeness, and relevance to the technical solution.\n"
        "    - If the section is missing or irrelevant, score it as 1 and explain why.\n"
        "    - If the section is copy-pasted boilerplate, score it as 1 and explain why.\n"
        "    - Provide a brief justification for the score.\n"
        "- After reviewing all sections:\n"
        "    - Consider the overall solution described in the document.\n"
        "    - Score the entire technical specification from 1 to 10 based on the quality, feasibility, and completeness of the solution provided.\n"
        "    - Provide a summary justification for the overall score."
    )
    return doc_struct.to_ai_prompt(context=context, rules=rules)

def main():
    """Main entry point for the Streamlit app."""
    st.set_page_config(page_title=APP_NAME, page_icon=APP_ICON, layout="wide")
    st.title(APP_NAME)

    aws_region = get_aws_region()
    file_service = FileService()
    ai_service = BedrockService(region_name=aws_region)
    template_path = os.path.join("TechspecificationTemplate.docx")

    uploaded_file = render_file_uploader()
    if not uploaded_file:
        return

    text = file_service.extract_text(uploaded_file)
    if not text:
        st.error("Failed to extract text from the uploaded file.")
        return

    template_headings = extract_template_headings(template_path)
    doc_struct = build_document_structure(text, template_headings)
    ai_prompt = get_ai_prompt(doc_struct)
    bedrock_request, ai_response = ai_service.review_document(ai_prompt)
    doc_struct.update_from_ai_response(ai_response)

    tab1, tab2, tab3, tab4 = st.tabs(["Template Sections", "Document Info", "Content", "AI Review"])
    with tab1:
        render_template_headings_display(template_path)
    with tab2:
        render_document_info(text)
    with tab3:
        render_tech_spec_display(text, template_headings, template_path)
    with tab4:
        st.markdown("### AI Review Prompt (for scoring)")
        st.markdown("#### Complete Request to Claude")
        st.json(bedrock_request)
        st.markdown("### AI Review (Scores & Comments)")
        if doc_struct.overall_score is not None:
            st.write(f"**Overall Score:** {doc_struct.overall_score}")
        if doc_struct.overall_comment:
            st.write(f"**Overall Comment:** {doc_struct.overall_comment}")
        for section in doc_struct.sections:
            with st.expander(f"Section: {section.header}"):
                if section.ai_score is not None:
                    st.write(f"**Score:** {section.ai_score}")
                if section.ai_comment:
                    st.write(f"**Comment:** {section.ai_comment}")
                if section.ai_suggestions:
                    st.write(f"**Suggestions:** {section.ai_suggestions}")

if __name__ == "__main__":
    main() 