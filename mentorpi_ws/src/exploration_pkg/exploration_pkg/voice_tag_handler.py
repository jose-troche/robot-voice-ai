def parse_room_tag(text: str) -> str:
    lowered = text.strip().lower()
    prefix = "this is "
    if lowered.startswith(prefix):
        return lowered[len(prefix) :].strip()
    return lowered
