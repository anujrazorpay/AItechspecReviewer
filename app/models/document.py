from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from .annotation import Annotation

@dataclass
class Document:
    name: str
    content: str
    file_type: str
    size: int
    created_at: datetime = datetime.now()
    annotations: Optional[list] = None 