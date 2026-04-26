import re


ROOM_TAG_PATTERNS = (
    re.compile(r"^\s*this\s+is\s+the\s+room[\s,:\-]+(.+?)\s*[.!?]*\s*$"),
    re.compile(r"^\s*this\s+room\s+is\s+the[\s,:\-]+(.+?)\s*[.!?]*\s*$"),
)


def parse_room_tag(text: str) -> str:
    lowered = text.strip().lower()
    for pattern in ROOM_TAG_PATTERNS:
        match = pattern.match(lowered)
        if match:
            return match.group(1).strip()
    return ""


def is_clear_polygon_command(text: str) -> bool:
    lowered = text.strip().lower()
    return lowered in {"clear room polygon", "reset room polygon", "clear polygon"}
