def build_plan(intent_payload: dict) -> dict:
    intent = intent_payload.get("intent")
    if intent == "navigate":
        return {"type": "navigate", "goal": intent_payload.get("target", "")}
    if intent == "search_object":
        return {"type": "search_object", "query": intent_payload.get("query", "")}
    if intent == "tag_room":
        return {"type": "tag_room", "name": intent_payload.get("target", "")}
    return {"type": "noop", "reason": "unrecognized intent"}
