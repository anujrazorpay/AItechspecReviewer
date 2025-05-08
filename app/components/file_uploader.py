import streamlit as st
from ..services.file_service import FileService
from ..config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE

def render_file_uploader():
    """Render the file uploader component."""
    st.markdown("### Upload Technical Specification")
    st.markdown("""
    Upload your technical specification document for AI review.
    - Supported formats: PDF, DOCX, TXT
    - Maximum file size: 10MB
    """)
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=[ext[1:] for ext in ALLOWED_EXTENSIONS],  # Remove the dot from extensions
        help="Supported formats: PDF, DOCX, TXT"
    )

    if uploaded_file is not None:
        try:
            if FileService.validate_file(uploaded_file):
                st.success(f"File '{uploaded_file.name}' uploaded successfully!")
                return uploaded_file
            else:
                if uploaded_file.size > MAX_FILE_SIZE:
                    st.error(f"File size exceeds the maximum limit of {MAX_FILE_SIZE/1024/1024}MB")
                else:
                    st.error(f"Invalid file type. Supported formats: {', '.join(ALLOWED_EXTENSIONS)}")
                return None
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            return None
    return None 