import requests


def check_directory_traversal(url):
    """Check for directory traversal vulnerabilities."""
    payloads = ["../../../etc/passwd", "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts"]
    
    for payload in payloads:
        try:
            test_url = f"{url}?file={payload}"
            resp = requests.get(test_url, timeout=5)
            if "root:" in resp.text or "[drivers]" in resp.text:
                return True
        except Exception:
            continue
    return False
