import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
STATIC_DIR = BASE_DIR / "static"

# Create necessary directories
UPLOAD_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)

# Application settings
APP_NAME = "AI TechSpec Reviewer"
APP_ICON = "📝"

# File settings
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# AI settings
AI_MODEL = "gpt-3.5-turbo"  # or your preferred model 