import requests


def check_security_headers(url):
    """Check for security headers."""
    try:
        resp = requests.get(url, timeout=5)
        headers = resp.headers
        
        security_headers = {
            'X-Frame-Options': headers.get('X-Frame-Options'),
            'X-Content-Type-Options': headers.get('X-Content-Type-Options'),
            'X-XSS-Protection': headers.get('X-XSS-Protection'),
            'Strict-Transport-Security': headers.get('Strict-Transport-Security'),
            'Content-Security-Policy': headers.get('Content-Security-Policy')
        }
        
        return security_headers
    except Exception:
        return {}
