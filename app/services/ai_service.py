from typing import List, Dict
import openai
import json
from ..models.annotation import Annotation
from ..config import AI_MODEL

class AIService:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OpenAI API key is required")
        openai.api_key = api_key

    def review_document(self, prompt: str) -> Dict:
        """Send the structured prompt to the AI and return a structured response as a dict."""
        if not prompt:
            return {'overall_score': None, 'overall_comment': '', 'sections': []}
        try:
            system_prompt = (
                "You are a technical specification reviewer. "
                "Return ONLY a valid JSON object with the following structure. "
                "Do not include any explanation or extra text outside the JSON.\n"
                "Example:\n"
                "{\n"
                "  \"overall_score\": 8,\n"
                "  \"overall_comment\": \"The document is well-structured.\",\n"
                "  \"sections\": [\n"
                "    {\n"
                "      \"header\": \"Introduction\",\n"
                "      \"score\": 5,\n"
                "      \"comment\": \"Clear and complete.\",\n"
                "      \"suggestions\": \"\"\n"
                "    },\n"
                "    {\n"
                "      \"header\": \"System Requirements\",\n"
                "      \"score\": 3,\n"
                "      \"comment\": \"Missing details on memory requirements.\",\n"
                "      \"suggestions\": \"Add more details on hardware.\"\n"
                "    }\n"
                "  ]\n"
                "}\n"
            )
            response = openai.ChatCompletion.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            content = response.choices[0].message.content
            # Try to parse the response as JSON
            try:
                ai_response = json.loads(content)
            except Exception:
                # If the response is not valid JSON, try to extract JSON from the text
                import re
                match = re.search(r'\{.*\}', content, re.DOTALL)
                if match:
                    ai_response = json.loads(match.group(0))
                else:
                    ai_response = {'overall_score': None, 'overall_comment': content, 'sections': []}
            return ai_response
        except Exception as e:
            print(f"Error in document review: {str(e)}")
            return {'overall_score': None, 'overall_comment': f"Error during review: {str(e)}", 'sections': []}

    def _analyze_chunk(self, chunk: str, position: int) -> List[Annotation]:
        """Analyze a chunk of text and generate annotations."""
        try:
            response = openai.ChatCompletion.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a technical specification reviewer. Review the following text and provide annotations. Focus on clarity, completeness, and technical accuracy."},
                    {"role": "user", "content": chunk}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Process response and create annotations
            content = response.choices[0].message.content
            return [Annotation(
                position=position,
                comment=content,
                severity="info",
                category="review"
            )]
        except Exception as e:
            print(f"Error analyzing chunk: {str(e)}")
            return []

    def _generate_summary(self, text: str) -> str:
        """Generate a summary of the document."""
        try:
            response = openai.ChatCompletion.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": "Provide a concise summary of the technical specification, highlighting key points and potential areas of concern."},
                    {"role": "user", "content": text}
                ],
                temperature=0.7,
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            return "Error generating summary."

    def _split_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into manageable chunks."""
        if not text:
            return []
            
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) < chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks 