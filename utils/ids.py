"""Sequential IDs such as U001, P001, and T001."""


def next_id(existing_ids: list[str], prefix: str) -> str:
    """Return the next ID for a prefix, based on the highest existing number.

    Deleted IDs are not reused when a higher number is still present. That keeps
    old references from pointing at a new record.
    """
    highest = 0
    for record_id in existing_ids:
        if not record_id.startswith(prefix):
            continue
        suffix = record_id[len(prefix):]
        if suffix.isdigit():
            highest = max(highest, int(suffix))
    return f"{prefix}{highest + 1:03d}"
