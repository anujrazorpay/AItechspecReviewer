from dataclasses import dataclass
from typing import Optional

@dataclass
class Annotation:
    position: int
    comment: str
    severity: Optional[str] = None
    category: Optional[str] = None 