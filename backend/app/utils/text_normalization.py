import re

from unidecode import unidecode

LEGAL_SUFFIX_PATTERNS = [
    (r"\bSOCIEDAD\s+ANONIMA\s+DE\s+CAPITAL\s+VARIABLE\b", "SA DE CV"),
    (r"\bSOCIEDAD\s+ANONIMA\b", "SA"),
    (r"\bSOCIEDAD\s+DE\s+RESPONSABILIDAD\s+LIMITADA\b", "S DE RL"),
    (r"\bSOCIEDAD\s+CIVIL\b", "SC"),
    (r"\bS\s*\.\s*A\s*\.\s*DE\s*C\s*\.\s*V\s*\.?\b", "SA DE CV"),
    (r"\bS\s*\.\s*A\s*\.?\b", "SA"),
    (r"\bS\s*\.\s*DE\s*R\s*\.\s*L\s*\.?\b", "S DE RL"),
    (r"\bS\s*\.\s*C\s*\.?\b", "SC"),
    (r"\bDE\s*C\s*\.\s*V\s*\.?\b", "DE CV"),
]


def normalize_text(text: str | None) -> str:
    if not text:
        return ""
    result = unidecode(text).upper().strip()
    result = re.sub(r"\s+", " ", result)
    return result


def normalize_business_name(name: str | None) -> str:
    if not name:
        return ""
    result = normalize_text(name)
    for pattern, replacement in LEGAL_SUFFIX_PATTERNS:
        result = re.sub(pattern, replacement, result)
    result = re.sub(r"[.,;:\"'()]+", " ", result)
    result = re.sub(r"\s+", " ", result).strip()
    return result


def normalize_address(address: str | None) -> str:
    if not address:
        return ""
    result = normalize_text(address)
    result = re.sub(r"\b(CALLE|C\.)\b", "", result)
    result = re.sub(r"\b(NUMERO|NUM\.?|NO\.?|#)\b", "NUM", result)
    result = re.sub(r"\b(COLONIA|COL\.?)\b", "COL", result)
    result = re.sub(r"\b(DELEGACION|DEL\.?|MUNICIPIO|MUN\.?)\b", "MUN", result)
    result = re.sub(r"[.,;:\"'()]+", " ", result)
    result = re.sub(r"\s+", " ", result).strip()
    return result


def similarity_ratio(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    set_a = set(a.split())
    set_b = set(b.split())
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union)


def texts_match(a: str | None, b: str | None, threshold: float = 0.85) -> bool:
    norm_a = normalize_text(a)
    norm_b = normalize_text(b)
    if norm_a == norm_b:
        return True
    return similarity_ratio(norm_a, norm_b) >= threshold


def business_names_match(a: str | None, b: str | None, threshold: float = 0.85) -> bool:
    norm_a = normalize_business_name(a)
    norm_b = normalize_business_name(b)
    if norm_a == norm_b:
        return True
    return similarity_ratio(norm_a, norm_b) >= threshold
