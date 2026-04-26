def parse_room_tag(text: str) -> str:
    lowered = text.strip().lower()
    prefix = "this room is the "
    if lowered.startswith(prefix):
        return lowered[len(prefix) :].strip()
    return lowered
