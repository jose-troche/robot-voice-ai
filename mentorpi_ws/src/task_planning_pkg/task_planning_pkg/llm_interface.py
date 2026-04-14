def build_plan(intent_payload) -> dict:
    intent = intent_payload.intent
    if intent == "navigate":
        return {"type": "navigate", "goal": intent_payload.target}
    if intent == "search_object":
        return {"type": "search_object", "query": intent_payload.query}
    if intent == "tag_room":
        return {"type": "tag_room", "name": intent_payload.target}
    return {"type": "noop", "reason": "unrecognized intent"}
