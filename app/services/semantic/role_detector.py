from typing import Optional

from ..ingestion.models import ContentBlock, BlockRole


# ============================================================
# PUBLIC API
# ============================================================

def detect_role(block: ContentBlock) -> BlockRole:
    """
    Detect a preliminary structural role for one ContentBlock.

    V1 principle:
        - Strong structural roles are detected here.
        - Semantic roles such as DEFINITION / EXPLANATION
          are NOT decided here.
        - UNKNOWN is allowed.
    """

    # --------------------------------------------------------
    # 1. Strong structural roles
    # --------------------------------------------------------

    role = _detect_strong_role(block)

    if role is not None:
        return role

    # --------------------------------------------------------
    # 2. Weak structural roles
    # --------------------------------------------------------

    role = _detect_structural_role(block)

    if role is not None:
        return role

    # --------------------------------------------------------
    # 3. Unknown
    # --------------------------------------------------------

    return BlockRole.UNKNOWN


# ============================================================
# STRONG ROLE DETECTION
# ============================================================

def _detect_strong_role(
    block: ContentBlock,
) -> Optional[BlockRole]:

    block_type = _get(block, "block_type")
    text = _get_text(block)

    # --------------------------------------------------------
    # FIGURE
    # --------------------------------------------------------

    if _is_figure(block, block_type):
        return BlockRole.FIGURE

    # --------------------------------------------------------
    # TABLE
    # --------------------------------------------------------

    if _is_table(block, block_type):
        return BlockRole.TECHNICAL_TABLE

    # --------------------------------------------------------
    # EQUATION
    # --------------------------------------------------------

    if _is_equation(block, block_type, text):
        return BlockRole.EQUATION

    # --------------------------------------------------------
    # FIGURE CAPTION
    # --------------------------------------------------------

    if _looks_like_figure_caption(block, text):
        return BlockRole.FIGURE_CAPTION

    # --------------------------------------------------------
    # TABLE CAPTION
    # --------------------------------------------------------

    if _looks_like_table_caption(block, text):
        return BlockRole.TABLE_CAPTION

    return None


# ============================================================
# STRUCTURAL ROLE DETECTION
# ============================================================

def _detect_structural_role(
    block: ContentBlock,
) -> Optional[BlockRole]:

    text = _get_text(block)

    # --------------------------------------------------------
    # SECTION HEADING
    # --------------------------------------------------------

    if _looks_like_heading(block, text):
        return BlockRole.SECTION_HEADING

    # --------------------------------------------------------
    # LIST
    # --------------------------------------------------------

    if _looks_like_list(block, text):
        return BlockRole.LIST

    # --------------------------------------------------------
    # FOOTNOTE
    # --------------------------------------------------------

    if _looks_like_footnote(block, text):
        return BlockRole.FOOTNOTE

    return None


# ============================================================
# FIGURE
# ============================================================

def _is_figure(
    block: ContentBlock,
    block_type,
) -> bool:

    value = _normalize_enum(block_type)

    if value in {
        "figure",
        "image",
        "picture",
        "graphic",
    }:
        return True

    # Some pipelines store image/vector information
    # in separate fields.

    if _truthy(_get(block, "is_image")):
        return True

    if _truthy(_get(block, "has_image")):
        return True

    return False


# ============================================================
# TABLE
# ============================================================

def _is_table(
    block: ContentBlock,
    block_type,
) -> bool:

    value = _normalize_enum(block_type)

    if value in {
        "table",
        "technical_table",
    }:
        return True

    if _truthy(_get(block, "is_table")):
        return True

    if _truthy(_get(block, "has_table")):
        return True

    return False


# ============================================================
# EQUATION
# ============================================================

def _is_equation(
    block: ContentBlock,
    block_type,
    text: str,
) -> bool:

    value = _normalize_enum(block_type)

    if value in {
        "equation",
        "formula",
        "math",
    }:
        return True

    if _truthy(_get(block, "is_equation")):
        return True

    # Text-only heuristic.
    # Keep conservative in V1.

    if not text:
        return False

    return _looks_like_equation_text(text)


# ============================================================
# HEADING
# ============================================================

def _looks_like_heading(
    block: ContentBlock,
    text: str,
) -> bool:

    if not text:
        return False

    # --------------------------------------------------------
    # Explicit heading information
    # --------------------------------------------------------

    block_type = _normalize_enum(
        _get(block, "block_type")
    )

    if block_type in {
        "heading",
        "title",
        "section_heading",
        "header",
    }:
        return True

    # --------------------------------------------------------
    # Font / layout evidence
    # --------------------------------------------------------
    ''' 
    # Không có font_size, nên không thể dùng font_size để xác định heading
    font_size = _get_font_size(block)

    if font_size is not None:
        if font_size >= 14:
            return True
    '''
    # --------------------------------------------------------
    # Text pattern
    # --------------------------------------------------------

    if _looks_like_numbered_heading(text):
        return True

    return False


# ============================================================
# LIST
# ============================================================

def _looks_like_list(
    block: ContentBlock,
    text: str,
) -> bool:

    if not text:
        return False

    block_type = _normalize_enum(
        _get(block, "block_type")
    )

    if block_type in {
        "list",
        "list_item",
        "bullet",
        "numbered_list",
    }:
        return True

    first = text.lstrip()

    # Bullet characters

    bullet_prefixes = (
        "• ",
        "● ",
        "▪ ",
        "‣ ",
        "- ",
        "* ",
    )

    if first.startswith(bullet_prefixes):
        return True

    # Numbered list

    if _starts_with_numbered_item(first):
        return True

    return False


# ============================================================
# FIGURE CAPTION
# ============================================================

def _looks_like_figure_caption(
    block: ContentBlock,
    text: str,
) -> bool:

    if not text:
        return False

    lower = text.lower().strip()

    prefixes = (
        "figure ",
        "fig. ",
        "fig ",
    )

    if lower.startswith(prefixes):
        return True

    return False


# ============================================================
# TABLE CAPTION
# ============================================================

def _looks_like_table_caption(
    block: ContentBlock,
    text: str,
) -> bool:

    if not text:
        return False

    lower = text.lower().strip()

    prefixes = (
        "table ",
        "tab. ",
        "tab ",
    )

    if lower.startswith(prefixes):
        return True

    return False


# ============================================================
# FOOTNOTE
# ============================================================

def _looks_like_footnote(
    block: ContentBlock,
    text: str,
) -> bool:

    if not text:
        return False

    # Explicit metadata is preferred.

    if _truthy(_get(block, "is_footnote")):
        return True

    block_type = _normalize_enum(
        _get(block, "block_type")
    )

    if block_type == "footnote":
        return True

    # V1 conservative heuristic:
    # footnotes are usually short and begin with a marker.

    stripped = text.strip()

    if len(stripped) > 300:
        return False

    if stripped.startswith(("*", "†", "‡")):
        return True

    if _starts_with_numeric_marker(stripped):
        return True

    return False


# ============================================================
# EQUATION TEXT HEURISTIC
# ============================================================

def _looks_like_equation_text(text: str) -> bool:

    stripped = text.strip()

    if not stripped:
        return False

    # Too short to safely classify

    if len(stripped) < 3:
        return False

    math_symbols = (
        "=",
        "≈",
        "≠",
        "≤",
        "≥",
        "∑",
        "∫",
        "√",
        "∞",
        "±",
    )

    symbol_count = sum(
        stripped.count(symbol)
        for symbol in math_symbols
    )

    # Conservative threshold

    if symbol_count >= 2:
        return True

    return False


# ============================================================
# TEXT HELPERS
# ============================================================

def _get_text(block: ContentBlock) -> str:

    text = _get(block, "text")

    if text is None:
        text = _get(block, "content")

    if text is None:
        return ""

    return str(text).strip()

''' 
def _get_font_size(
    block: ContentBlock,
) -> Optional[float]:

    value = _get(block, "font_size")

    if value is None:
        value = _get(block, "avg_font_size")

    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None

'''
def _normalize_enum(value) -> str:

    if value is None:
        return ""

    if hasattr(value, "value"):
        value = value.value

    return str(value).lower().strip()


def _truthy(value) -> bool:

    return bool(value)


def _get(obj, name: str):

    return getattr(obj, name, None)


# ============================================================
# TEXT PATTERNS
# ============================================================

def _looks_like_numbered_heading(text: str) -> bool:

    parts = text.strip().split(maxsplit=1)

    if not parts:
        return False

    token = parts[0].rstrip(".")

    # Examples:
    # 1
    # 1.1
    # 1.2.3
    # 2. Cement Chemistry

    if not token:
        return False

    components = token.split(".")

    return all(
        component.isdigit()
        for component in components
        if component
    )


def _starts_with_numbered_item(text: str) -> bool:

    if not text:
        return False

    parts = text.split(maxsplit=1)

    if not parts:
        return False

    token = parts[0]

    # 1.
    # 2)
    # 10.
    # 10)

    if token.endswith(".") or token.endswith(")"):
        number = token[:-1]

        return number.isdigit()

    return False


def _starts_with_numeric_marker(text: str) -> bool:

    if not text:
        return False

    first = text[0]

    return first.isdigit()