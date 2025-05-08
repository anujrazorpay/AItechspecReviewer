import streamlit as st
from typing import Dict, List, Tuple, Set

def render_section_rules_config(template_headings: List[Tuple[str, str]]) -> Tuple[Dict[str, str], Set[str]]:
    """
    Render UI for configuring rules for each section.
    Returns a tuple of (section_rules_dict, mandatory_sections_set)
    """
    section_rules = {}
    mandatory_sections = set()
    
    # Default rules that apply to all sections
    with st.expander("Default Rules (apply to all sections)", expanded=True):
        default_rules = st.text_area(
            "Default Rules",
            value="Score from 1 to 5 based on:\n- Clarity and completeness\n- Technical accuracy\n- Relevance to solution",
            help="These rules will be applied to all sections unless overridden by section-specific rules."
        )
    
    # Section-specific rules
    st.markdown("### Template Sections")
    st.info("Configure which sections are mandatory and their specific review rules.")
    
    for style, heading in template_headings:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            is_mandatory = st.checkbox(
                "Mandatory",
                key=f"mandatory_{heading}",
                help=f"Mark {heading} as a mandatory section"
            )
            if is_mandatory:
                mandatory_sections.add(heading)
        
        with col2:
            st.markdown(f"**{style}**: {heading}")
        
        with col3:
            with st.expander("Rules", expanded=False):
                section_rules[heading] = st.text_area(
                    f"Rules for {heading}",
                    value=default_rules,
                    key=f"rules_{heading}",
                    help=f"Custom rules for evaluating the {heading} section. Leave empty to use default rules."
                )
        st.markdown("---")
    
    return section_rules, mandatory_sections 