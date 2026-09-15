from dataclasses import dataclass
from typing import Optional


@dataclass
class SemanticContext:

    current_section: Optional[str] = None

    current_subsection: Optional[str] = None

    current_page: Optional[int] = None