# ============================================================
#  URL CHECKER — Domain Intelligence Engine
#  v2.0
# ============================================================

import re
from urllib.parse import urlparse
from trust_layer import BRAND_DOMAINS

# Common URL shortener domains
SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "cutt.ly", "t.co", "lnkd.in", "rb.gy", "rebrand.ly", "is.gd", "v.gd"
}

# Suspicious keywords commonly found in internship scam domains
SCAM_DOMAIN_KEYWORDS = [
    "offer-letter", "processing-fee", "verification-payment", "joining-fee",
    "fee-required", "security-deposit", "caution-deposit", "payment",
    "verification", "deposit", "joining", "activation"
]

def levenshtein_distance(s1: str, s2: str) -> int:
    """Compute Levenshtein distance between s1 and s2."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def parse_hostname(hostname: str):
    """
    Split a hostname into (registered_domain, subdomain).
    Handles common double TLDs.
    """
    hostname = hostname.lower().strip()
    if ":" in hostname:
        hostname = hostname.split(":")[0]

    parts = hostname.split(".")
    if len(parts) <= 2:
        return hostname, ""

    double_tlds = {"co.in", "org.in", "net.in", "gov.in", "edu.in", "ac.in", "co.uk", "org.uk"}
    last_two = ".".join(parts[-2:])
    if last_two in double_tlds and len(parts) >= 3:
        registered_domain = ".".join(parts[-3:])
        subdomain = ".".join(parts[:-3])
    else:
        registered_domain = ".".join(parts[-2:])
        subdomain = ".".join(parts[:-2])

    return registered_domain, subdomain

def check_homograph(registered_domain: str) -> bool:
    """Detect homograph Unicode lookalike spoofing."""
    try:
        registered_domain.encode('ascii')
        return False
    except UnicodeEncodeError:
        pass

    # Unicode translation map for typical homoglyphs
    lookalikes = {
        'ο': 'o', 'о': 'o', 'ö': 'o', 'ó': 'o', 'ò': 'o', 'ô': 'o', 'õ': 'o', 'ø': 'o',
        'е': 'e', 'ê': 'e', 'é': 'e', 'è': 'e', 'ë': 'e',
        'а': 'a', 'ä': 'a', 'á': 'a', 'à': 'a', 'â': 'a', 'ã': 'a',
        'і': 'i', 'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
        'ѕ': 's', 'ś': 's', 'š': 's',
        'с': 'c', 'ç': 'c',
        'р': 'p', 'х': 'x', 'у': 'y', 'ԁ': 'd'
    }

    ascii_chars = [lookalikes.get(char, char) for char in registered_domain]
    ascii_domain = "".join(ascii_chars)

    # Check if this transliterated domain matches a brand's official domain
    for brand, official in BRAND_DOMAINS.items():
        if (brand in ascii_domain or ascii_domain == official) and registered_domain != official:
            return True

    return False

def check_typosquatting(registered_domain: str) -> bool:
    """Detect typosquatting of protected brand names."""
    # Remove TLD to isolate domain name
    parts = registered_domain.split(".")
    double_tlds = {"co.in", "org.in", "net.in", "gov.in", "edu.in", "ac.in", "co.uk", "org.uk"}
    last_two = ".".join(parts[-2:])
    if last_two in double_tlds and len(parts) >= 3:
        domain_name = ".".join(parts[:-2])
    else:
        domain_name = ".".join(parts[:-1])

    # Split domain name by hyphens, numbers, or other non-alphanumeric chars
    tokens = re.split(r'[^a-zA-Z0-9]', domain_name)

    for token in tokens:
        if not token:
            continue
        token_lower = token.lower()

        # Map typical characters to handle numeric/symbolic obfuscation within domain name
        # (e.g. g00gle -> google)
        char_map = {'0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', '7': 't', '8': 'b', '9': 'g'}
        normalized_token = token_lower
        for k, v in char_map.items():
            normalized_token = normalized_token.replace(k, v)

        for brand, official in BRAND_DOMAINS.items():
            # If normalized matches the brand but original token is different -> Typosquatting
            if normalized_token == brand and token_lower != brand:
                return True

            # If Levenshtein distance is small (1 or 2 edits)
            dist = levenshtein_distance(token_lower, brand)
            if dist > 0 and dist <= 2:
                max_len = max(len(token_lower), len(brand))
                ratio = 1.0 - (dist / max_len)
                if ratio >= 0.75:
                    return True

    return False

def check_brand_abuse(registered_domain: str) -> bool:
    """Detect if brand name is embedded in registered domain (e.g. paytm-secure-login.xyz)."""
    registered_domain_lower = registered_domain.lower()
    for brand, official in BRAND_DOMAINS.items():
        if brand in registered_domain_lower:
            # If it contains brand but is not the official brand domain
            if registered_domain_lower != official and not registered_domain_lower.endswith("." + official):
                return True
    return False

def check_subdomain_abuse(registered_domain: str, subdomain: str) -> bool:
    """Detect brand keywords in subdomain of untrusted registered domains (e.g. google.com.verify-login.xyz)."""
    if not subdomain:
        return False

    # Check if registered domain is official brand domain
    registered_domain_lower = registered_domain.lower()
    is_official = False
    for brand, official in BRAND_DOMAINS.items():
        if registered_domain_lower == official or registered_domain_lower.endswith("." + official):
            is_official = True
            break

    if is_official:
        return False

    # If registered domain is not official, check if any brand is in the subdomain
    subdomain_lower = subdomain.lower()
    for brand in BRAND_DOMAINS.keys():
        # Check if the brand name is present as a standalone part of the subdomain
        # E.g. "google" in "google.com" or "careers-google"
        if brand in subdomain_lower:
            return True

    return False

def analyze_url(url: str) -> dict:
    """
    Perform deep domain intelligence on the given URL.
    Returns:
        dict:
            - domain (str)
            - score (int: 0 to 100)
            - risk (str: "Safe" / "Suspicious")
            - triggered_rules (list of str)
    """
    if not url:
        return {"domain": "", "score": 0, "risk": "Safe", "triggered_rules": []}

    # Clean URL and parse domain
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        parsed = urlparse(url)
        hostname = parsed.netloc.lower()
    except Exception:
        return {"domain": "", "score": 0, "risk": "Safe", "triggered_rules": []}

    registered_domain, subdomain = parse_hostname(hostname)

    # 0. Domain Trust Signals Override
    is_trusted = False
    if hostname.endswith(".gov.in") or hostname.endswith(".nic.in") or hostname.endswith(".gov") or hostname.endswith(".nic"):
        is_trusted = True
    else:
        for brand, official in BRAND_DOMAINS.items():
            if registered_domain == official or hostname.endswith("." + official):
                is_trusted = True
                break

    if is_trusted:
        return {
            "domain": hostname,
            "score": 5,
            "risk": "Safe",
            "triggered_rules": []
        }

    score = 0
    triggered_rules = []

    # 1. Typosquatting (+50)
    if check_typosquatting(registered_domain):
        score += 50
        triggered_rules.append("Typosquatting")

    # 2. Homograph Detection (+40)
    if check_homograph(registered_domain):
        score += 40
        triggered_rules.append("Homograph Spoofing")

    # 3. Subdomain Abuse (+60)
    if check_subdomain_abuse(registered_domain, subdomain):
        score += 60
        triggered_rules.append("Subdomain Abuse")

    # 4. URL Shortener (+30)
    if registered_domain in SHORTENER_DOMAINS:
        score += 30
        triggered_rules.append("URL Shortener")

    # 5. Brand Abuse (+50)
    if check_brand_abuse(registered_domain):
        score += 50
        triggered_rules.append("Brand Abuse")

    # 6. Internship Scam Domain (+50)
    # Check if registered domain contains scam keywords
    domain_name = registered_domain.split(".")[0]
    for kw in SCAM_DOMAIN_KEYWORDS:
        if kw in domain_name:
            score += 50
            triggered_rules.append("Scam Domain Pattern")
            break

    # 7. Suspicious TLD Detection (+30)
    SUSPICIOUS_TLDS = {".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".click", ".top", ".win", ".loan", ".site"}
    has_suspicious_tld = False
    for tld in SUSPICIOUS_TLDS:
        if registered_domain.endswith(tld):
            has_suspicious_tld = True
            break
    if has_suspicious_tld:
        score += 30
        triggered_rules.append("Suspicious TLD")

    # 8. Job Scam Keywords (+20)
    SCAM_KEYWORDS = {"job", "jobs", "career", "careers", "internship", "offer", "placement", "government", "govt", "recruitment"}
    has_scam_keyword = False
    for kw in SCAM_KEYWORDS:
        if kw in registered_domain or (subdomain and kw in subdomain):
            has_scam_keyword = True
            break
    if has_scam_keyword:
        score += 20
        triggered_rules.append("Job Scam Keyword")

    # 9. Fake Government Pattern Detection (+20)
    is_gov_tld = (
        hostname.endswith(".gov.in") or 
        hostname.endswith(".nic.in") or 
        hostname.endswith(".gov") or 
        hostname.endswith(".nic")
    )
    has_gov_keyword = any(kw in registered_domain or (subdomain and kw in subdomain) for kw in ["govt", "government", "sarkari"])
    if has_gov_keyword and not is_gov_tld:
        score += 20
        triggered_rules.append("Fake Government Pattern")

    # Clamp score to 100
    score = min(score, 100)

    # Determine risk label
    risk = "Suspicious" if score >= 30 else "Safe"

    return {
        "domain": hostname,
        "score": score,
        "risk": risk,
        "triggered_rules": triggered_rules
    }

if __name__ == "__main__":
    # Test cases
    test_urls = [
        "https://g00gle.com",
        "http://paytm-secure-login.xyz",
        "https://linkedln-careers.com",
        "https://gοogle.com", # greek omicron
        "https://google.com.verify-login.xyz",
        "https://linkedin.com.jobs-update.xyz",
        "https://bit.ly/3xyz",
        "https://offer-letter-processing-fee.com",
        "https://google.com",
        "https://careers.google.com",
    ]
    print("Running URL Checker Tests:")
    for url in test_urls:
        res = analyze_url(url)
        # print using ascii-safe encoding for the windows terminal
        safe_url = url.encode('ascii', errors='replace').decode('ascii')
        print(f"URL: {safe_url:<45} -> Score: {res['score']:<3} Risk: {res['risk']:<11} Rules: {res['triggered_rules']}")