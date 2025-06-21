import requests


def check_http_methods(url):
    """Check allowed HTTP methods."""
    methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD', 'PATCH', 'TRACE']
    allowed_methods = []
    
    for method in methods:
        try:
            resp = requests.request(method, url, timeout=5)
            if resp.status_code != 405:  # Method not allowed
                allowed_methods.append(method)
        except Exception:
            continue
    
    return allowed_methods
