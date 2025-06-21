import requests
from urllib.parse import urljoin


def check_xss_vulnerability(url, payloads=None):
    """Check for XSS vulnerabilities."""
    if payloads is None:
        payloads = ["<script>alert('XSS')</script>", "javascript:alert('XSS')"]
    
    for payload in payloads:
        try:
            test_url = f"{url}?test={payload}"
            resp = requests.get(test_url, timeout=5)
            if payload in resp.text:
                return True
        except Exception:
            continue
    return False
