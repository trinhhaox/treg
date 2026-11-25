"""Phone number utilities for normalization, recognition, and candidate resolution."""

from __future__ import annotations

import re


def clean_phone(phone: str | None) -> str:
    """Strip all whitespace, dashes, dots, parentheses, keeping leading '+' and digits."""
    if not phone:
        return ""
    stripped = phone.strip()
    has_plus = stripped.startswith("+")
    digits = re.sub(r"\D", "", stripped)
    if not digits:
        return ""
    return f"+{digits}" if has_plus else digits


def is_probable_phone(val: str | None) -> bool:
    """Return True if val looks like a phone number rather than an email or username."""
    if not val or "@" in val:
        return False
    # Must only contain digits, plus, spaces, dashes, dots, parentheses
    clean = re.sub(r"[\s().-]", "", val.strip())
    if not clean:
        return False
    # Check if format is +digits or pure digits, length between 7 and 16
    return bool(re.fullmatch(r"\+?[0-9]{7,16}", clean))


def get_phone_candidates(val: str | None) -> list[str]:
    """Generate potential phone formats to match against database records.

    For example:
    - '0912345678' -> ['0912345678', '+84912345678', '84912345678']
    - '+84912345678' -> ['+84912345678', '0912345678', '84912345678']
    """
    if not val:
        return []
    cleaned = clean_phone(val)
    if not cleaned:
        return []

    candidates: list[str] = [cleaned]

    # If it's a Vietnamese phone number or starts with 0
    if cleaned.startswith("0") and len(cleaned) in (10, 11):
        vn_intl = f"+84{cleaned[1:]}"
        vn_no_plus = f"84{cleaned[1:]}"
        candidates.extend([vn_intl, vn_no_plus])
    elif cleaned.startswith("+84") and len(cleaned) in (11, 12):
        vn_local = f"0{cleaned[3:]}"
        vn_no_plus = cleaned[1:]
        candidates.extend([vn_local, vn_no_plus])
    elif cleaned.startswith("84") and len(cleaned) in (10, 11):
        vn_local = f"0{cleaned[2:]}"
        vn_intl = f"+{cleaned}"
        candidates.extend([vn_local, vn_intl])
    elif cleaned.startswith("+"):
        # Also try without the plus sign
        candidates.append(cleaned[1:])
    else:
        # Also try with the plus sign
        candidates.append(f"+{cleaned}")

    # Preserve order while deduplicating
    seen: set[str] = set()
    unique: list[str] = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            unique.append(c)

    return unique
