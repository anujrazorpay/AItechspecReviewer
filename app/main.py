import streamlit as st
import os
from typing import Dict, Set
from app.config import APP_NAME, APP_ICON
from app.services.file_service import FileService
from app.services.bedrock_service import BedrockService
from app.components.file_uploader import render_file_uploader
from app.components.tech_spec_display import render_tech_spec_display, break_content_by_template_sections
from app.components.doc_info_extractor import render_document_info
from app.components.template_headings_display import render_template_headings_display, extract_template_headings
from app.components.section_rules_config import render_section_rules_config
from app.models.structured_doc import SectionContent, DocumentStructure

def get_aws_region() -> str:
    """Get AWS region from Streamlit secrets or environment variable."""
    try:
        return st.secrets.get("AWS_REGION") or os.getenv("AWS_REGION", "us-east-1")
    except Exception as e:
        st.warning(f"Could not load AWS region from secrets: {str(e)}. Using default region.")
        return os.getenv("AWS_REGION", "us-east-1")

def build_document_structure(text, template_headings) -> DocumentStructure:
    """Build a DocumentStructure object from extracted text and template headings."""
    section_map, _ = break_content_by_template_sections(text, template_headings)
    sections = [
        SectionContent(header=heading, content_blocks=section_map.get(heading, []))
        for _, heading in template_headings
    ]
    return DocumentStructure(sections=sections)

def get_ai_prompt(doc_struct: DocumentStructure, section_rules: Dict[str, str], mandatory_sections: Set[str]) -> str:
    """Generate the AI review prompt with custom section rules."""
    context = (
        "You are an expert technical reviewer. You are reviewing a technical specification document. "
        "The document describes a solution to a specific problem or requirement."
    )
    
    # Build rules section with custom rules for each section
    rules = ["General Rules:"]
    rules.extend([
        "- For each section:",
        "    - Carefully read the content.",
        "    - If the section is missing or irrelevant, score it as 1 and explain why.",
        "    - If the section is copy-pasted boilerplate, score it as 1 and explain why.",
        "    - Provide a brief justification for the score.",
        "- After reviewing all sections:",
        "    - Consider the overall solution described in the document.",
        "    - Score the entire technical specification from 1 to 10 based on the quality, feasibility, and completeness of the solution provided.",
        "    - Provide a summary justification for the overall score.",
        "",
        "Section-Specific Rules:"
    ])
    
    # Add section-specific rules
    for section in doc_struct.sections:
        if section.header in section_rules and section_rules[section.header]:
            rules.append(f"\n{section.header}:")
            if section.header in mandatory_sections:
                rules.append("    [MANDATORY SECTION]")
            rules.extend([f"    {rule}" for rule in section_rules[section.header].split('\n') if rule.strip()])
    
    return doc_struct.to_ai_prompt(context=context, rules='\n'.join(rules))

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
    
    # Create document structure before tabs
    doc_struct = build_document_structure(text, template_headings)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Template Sections", "Document Info", "Content", "AI Review"])
    
    with tab1:
        section_rules, mandatory_sections = render_section_rules_config(template_headings)
    
    with tab2:
        render_document_info(text)
    
    with tab3:
        # Convert doc_struct sections to the format expected by render_tech_spec_display
        content = []
        for section in doc_struct.sections:
            content.append(section.header)
            content.extend(section.content_blocks)
        render_tech_spec_display(content, template_headings, template_path)
    
    with tab4:
        st.markdown("### AI Review")
        
        # Initialize session state for AI review if not exists
        if 'ai_review_done' not in st.session_state:
            st.session_state.ai_review_done = False
            st.session_state.bedrock_request = None
            st.session_state.ai_response = None
        
        # Get AI Score button
        if st.button("Get AI Score", type="primary"):
            with st.spinner("Generating AI review..."):
                ai_prompt = get_ai_prompt(doc_struct, section_rules, mandatory_sections)
                st.session_state.bedrock_request, st.session_state.ai_response = ai_service.review_document(ai_prompt)
                doc_struct.update_from_ai_response(st.session_state.ai_response)
                st.session_state.ai_review_done = True
            st.success("AI review completed!")
        
        # Display AI review if available
        if st.session_state.ai_review_done:
            st.markdown("#### Review Prompt")
            st.markdown("##### Complete Request to Claude")
            st.json(st.session_state.bedrock_request)
            st.markdown("##### AI Review (Scores & Comments)")
            if doc_struct.overall_score is not None:
                st.write(f"**Overall Score:** {doc_struct.overall_score}")
            if doc_struct.overall_comment:
                st.write(f"**Overall Comment:** {doc_struct.overall_comment}")
            for section in doc_struct.sections:
                with st.expander(f"Section: {section.header}"):
                    if section.header in mandatory_sections:
                        st.warning("This is a mandatory section")
                    if section.ai_score is not None:
                        st.write(f"**Score:** {section.ai_score}")
                    if section.ai_comment:
                        st.write(f"**Comment:** {section.ai_comment}")
                    if section.ai_suggestions:
                        st.write(f"**Suggestions:** {section.ai_suggestions}")
        else:
            st.info("Click 'Get AI Score' to generate the AI review.")

if __name__ == "__main__":
    main() 