import re


ROOM_TAG_PATTERNS = (
    re.compile(r"^\s*this\s+is\s+the\s+room[\s,:\-]+(.+?)\s*[.!?]*\s*$"),
    re.compile(r"^\s*this\s+room\s+is\s+the[\s,:\-]+(.+?)\s*[.!?]*\s*$"),
)


def parse_intent(text: str) -> dict:
    lowered = text.strip().lower()
    if lowered.startswith("go to "):
        return {"intent": "navigate", "target": lowered.replace("go to ", "", 1).strip()}
    if lowered.startswith("navigate to "):
        return {
            "intent": "navigate",
            "target": lowered.replace("navigate to ", "", 1).strip(),
        }
    if lowered.startswith("find "):
        return {"intent": "search_object", "query": lowered}
    for pattern in ROOM_TAG_PATTERNS:
        match = pattern.match(lowered)
        if match:
            return {"intent": "tag_room", "target": match.group(1).strip()}
    return {"intent": "unknown", "raw_text": text}
