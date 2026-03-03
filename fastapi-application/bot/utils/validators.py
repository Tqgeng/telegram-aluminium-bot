import re

PHONE_RE = re.compile(r"^\+?[1-9]\d{9,14}$")


def normalize_phone(raw: str) -> str | None:
    if not raw:
        return None
    phone = re.sub(r"[^\d+]", "", raw)
    if phone.startswith("8") and len(phone) == 11:
        phone = "+7" + phone[1:]
    if not phone.startswith("+"):
        phone = "+" + phone
    return phone


def is_valid_phone(raw: str) -> bool:
    phone = normalize_phone(raw)
    if not phone:
        return False
    return bool(PHONE_RE.match(phone))
