import requests
from urllib.parse import urljoin


def check_sensitive_endpoints(base_url):
    """Check for sensitive endpoints."""
    sensitive_paths = [
        '/admin', '/administrator', '/wp-admin', '/phpmyadmin',
        '/config', '/backup', '/test', '/dev', '/debug'
    ]
    
    found_endpoints = []
    for path in sensitive_paths:
        try:
            url = urljoin(base_url, path)
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                found_endpoints.append(url)
        except Exception:
            continue
    
    return found_endpoints
