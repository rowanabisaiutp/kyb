import re

RFC_PATTERN = re.compile(r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$")


def is_valid_rfc(rfc: str) -> bool:
    return bool(RFC_PATTERN.match(rfc.upper().strip()))
