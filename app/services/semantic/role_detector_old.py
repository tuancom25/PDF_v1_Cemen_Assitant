from app.services.group.unassigned_group_old_2 import UnassignedGroup
from app.services.ingestion.models import  ( 
    BlockRole,  
    ContentBlock,
    SemanticContentBlock,
    BlockType,
    SemanticGroup,
    
    )

def detect_role(block: ContentBlock) -> BlockRole:

    if block.content_type == "table":
      return BlockRole.TABLE_CAPTION

    if block.content_type == "figure":
       return BlockRole.FIGURE_CAPTION
    ''' 
    if block.type == BlockType.TABLE:
        return BlockRole.TABLE

    if block.type == BlockType.FIGURE:
        return BlockRole.FIGURE
    '''
    text = block.text.strip()

    if not text:
        return BlockRole.UNKNOWN

    if _is_caption(text):
        #return BlockRole.CAPTION 
        return BlockRole.FIGURE_CAPTION

    if _is_heading(block):
        #return BlockRole.HEADING
        return BlockRole.SECTION_HEADING

    return BlockRole.PARAGRAPH



def _is_caption(text: str) -> bool:

    text_lower = text.lower()

    prefixes = (
        "figure ",
        "fig. ",
        "fig ",
        "table ",
    )

    return text_lower.startswith(prefixes)


def _is_heading(block: ContentBlock) -> bool:

    text = block.text.strip()

    if len(text) > 150:
        return False

    if _looks_like_numbered_heading(text):
        return True

    if _looks_like_short_heading(text):
        return True

    return False


def _looks_like_numbered_heading(text: str) -> bool:

    import re

    pattern = r"^\d+(\.\d+)*\.?\s+\S+"

    return bool(re.match(pattern, text))


def _looks_like_short_heading(text: str) -> bool:

    words = text.split()

    if len(words) > 12:
        return False

    if text.endswith("."):
        return False

    return True
