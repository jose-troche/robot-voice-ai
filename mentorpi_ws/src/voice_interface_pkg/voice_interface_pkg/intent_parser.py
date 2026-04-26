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
    if lowered.startswith("this room is the "):
        return {
            "intent": "tag_room",
            "target": lowered.replace("this room is the ", "", 1).strip(),
        }
    return {"intent": "unknown", "raw_text": text}
