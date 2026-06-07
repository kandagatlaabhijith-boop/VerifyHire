# ============================================================
#  TRUST LAYER — Domain Trust Verification
#  v2.0
# ============================================================

BRAND_DOMAINS = {
    "google": "google.com",
    "microsoft": "microsoft.com",
    "amazon": "amazon.jobs",
    "flipkart": "flipkart.com",
    "swiggy": "swiggy.com",
    "zomato": "zomato.com",
    "paytm": "paytm.com",
    "razorpay": "razorpay.com",
    "phonepe": "phonepe.com",
    "cred": "cred.club",
    "zepto": "zepto.life",
    "meesho": "meesho.com",
    "tcs": "tcs.com",
    "infosys": "infosys.com",
    "wipro": "wipro.com",
    "hcl": "hcltech.com",
    "accenture": "accenture.com",
    "deloitte": "deloitte.com",
    "ibm": "ibm.com",
    "linkedin": "linkedin.com",
    "naukri": "naukri.com",
    "internshala": "internshala.com",
    "unstop": "unstop.com"
}

TRUSTED_DOMAINS = list(BRAND_DOMAINS.values())

def get_domain_trust(domain: str) -> float:
    """
    Returns a trust score between 0.0 and 1.0.
    1.0/0.95 if it is an official trusted brand domain.
    0.3 otherwise.
    """
    domain = domain.lower().strip()
    if domain.startswith("www."):
        domain = domain[4:]

    for td in TRUSTED_DOMAINS:
        if domain == td or domain.endswith("." + td):
            return 0.95

    return 0.3