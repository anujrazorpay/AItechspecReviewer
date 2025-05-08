from typing import List, Union, Dict, Optional

class SectionContent:
    def __init__(
        self,
        header: str,
        content_blocks: List[Union[str, Dict]],
        ai_score: Optional[int] = None,
        ai_comment: Optional[str] = None,
        ai_suggestions: Optional[str] = None
    ):
        self.header = header
        self.content_blocks = content_blocks  # paragraphs (str) or tables (dict)
        self.ai_score = ai_score
        self.ai_comment = ai_comment
        self.ai_suggestions = ai_suggestions

    def to_prompt_block(self) -> str:
        """Format this section as a prompt block for AI."""
        block = f"---\nSection: {self.header}\nContent:\n"
        for content in self.content_blocks:
            if isinstance(content, str):
                block += content + "\n"
            elif isinstance(content, dict) and content.get('type') == 'table':
                block += "Table:\n" + content.get('text', '') + "\n"
        block += "---\n"
        return block

class DocumentStructure:
    def __init__(
        self,
        sections: List[SectionContent],
        overall_score: Optional[int] = None,
        overall_comment: Optional[str] = None
    ):
        self.sections = sections
        self.overall_score = overall_score
        self.overall_comment = overall_comment

    def to_ai_prompt(self, context: str = None, rules: str = None) -> str:
        """
        Generate a structured prompt for AI review, including context, rules, and section data.
        """
        if context is None:
            context = (
                "You are an expert technical specification reviewer. "
                "You will review each section of a technical specification document for completeness, originality, and adherence to the provided template."
            )
        if rules is None:
            rules = (
                "- For each section:\n"
                "    - If the section is missing, say 'Section [Header] is missing.'\n"
                "    - If the section content is copy-pasted from the template, say 'Section [Header] appears to be boilerplate.'\n"
                "    - If the section is present and original, review for clarity, completeness, and technical accuracy.\n"
                "    - For tables, review the data as well as the context.\n"
                "- Provide a score (1-5) for each section based on quality and completeness.\n"
                "- Suggest improvements if needed."
            )
        prompt = f"Context:\n{context}\n\nRules:\n{rules}\n\nData:\n"
        for section in self.sections:
            prompt += section.to_prompt_block()
        return prompt

    def update_from_ai_response(self, ai_response: dict):
        """Update the structure with AI feedback (scores, comments, suggestions)."""
        self.overall_score = ai_response.get("overall_score")
        self.overall_comment = ai_response.get("overall_comment")
        section_feedback = {s["header"]: s for s in ai_response.get("sections", [])}
        for section in self.sections:
            feedback = section_feedback.get(section.header)
            if feedback:
                section.ai_score = feedback.get("score")
                section.ai_comment = feedback.get("comment")
                section.ai_suggestions = feedback.get("suggestions") 