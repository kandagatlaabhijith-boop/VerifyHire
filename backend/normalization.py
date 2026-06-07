import re
import unicodedata

# Mapping of common symbols/homoglyphs to their ASCII equivalents
CHAR_MAP = {
    '€': 'e', '3': 'e', '£': 'e', 'ê': 'e', 'é': 'e', 'è': 'e', 'ë': 'e',
    '¥': 'y', 'ÿ': 'y',
    '0': 'o', 'ο': 'o', 'о': 'o', 'ö': 'o', 'ó': 'o', 'ò': 'o', 'ô': 'o',
    '1': 'i', '¡': 'i', 'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
    '@': 'a', '4': 'a', 'ä': 'a', 'á': 'a', 'à': 'a', 'â': 'a', 'ã': 'a', 'å': 'a',
    '$': 's', '5': 's', '§': 's',
    '8': 'b', '9': 'g', '7': 't',
    'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
    '¢': 'c', 'ç': 'c',
    'ñ': 'n',
}

def normalize_text(text: str) -> str:
    """
    Convert adversarial text into a canonical clean form.
    Handles homoglyphs, spacing, punctuation, and case normalization.
    """
    if not text:
        return ""

    # 1. Lowercase and Unicode decomposition
    text = text.lower()
    text = unicodedata.normalize('NFKD', text)

    # 2. Collapse punctuation between alphanumeric characters to space (handles u_p_i -> u p i, f.e.e -> f e e)
    text = re.sub(r'(?<=[a-z0-9])[\s\.\-_]+(?=[a-z0-9])', ' ', text)

    # 3. Collapse repeated punctuation
    text = re.sub(r'([!?,.:;_\-\*])\1+', r'\1', text)

    # 4. Map characters safely (avoiding translating pure numbers like 1200 -> i2oo)
    words = text.split()
    normalized_words = []
    
    for w in words:
        has_letter = any(c.isalpha() for c in w)
        if has_letter:
            # Check if it has any digits or symbols typically used for obfuscation
            has_obfuscation = any(c.isdigit() or c in ['€', '¥', '$', '@', '§', '¢', '£', '_'] for c in w)
            if has_obfuscation:
                translated = [CHAR_MAP.get(char, char) for char in w]
                normalized_words.append("".join(translated))
            else:
                normalized_words.append(w)
        else:
            # Single character symbols like € -> e
            if len(w) == 1 and w in CHAR_MAP:
                normalized_words.append(CHAR_MAP[w])
            else:
                normalized_words.append(w)
                
    text = " ".join(normalized_words)

    # 5. Collapse consecutive single character words (f e e -> fee)
    words = text.split()
    new_words = []
    i = 0
    while i < len(words):
        if len(words[i]) == 1 and words[i].isalnum():
            seq = []
            while i < len(words) and len(words[i]) == 1 and words[i].isalnum():
                seq.append(words[i])
                i += 1
            if len(seq) >= 2:
                new_words.append("".join(seq))
            else:
                new_words.append(seq[0])
        else:
            new_words.append(words[i])
            i += 1

    text = " ".join(new_words)

    # 6. Final whitespace collapse
    text = re.sub(r'\s+', ' ', text).strip()
    return text

if __name__ == "__main__":
    # Test cases
    test_cases = [
        "f€e",
        "f3e",
        "fr33",
        "pa¥ment",
        "n0t",
        "n.o.t",
        "f e e",
        "registration f€e",
        "registration f3e",
        "registration f.e.e",
        "pa¥ment",
        "n0 payment",
        "fr33 internship",
        "urgent!!! registration f e e required",
    ]
    print("Running Normalizer Tests:")
    for tc in test_cases:
        print(f"Original: {tc:<40} -> Normalized: {normalize_text(tc)}")
