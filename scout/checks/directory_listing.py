import re

import requests


def check_directory_listing(url):
    """Check for directory listing vulnerability."""
    try:
        resp = requests.get(url + '/', timeout=5)
        if re.search(r'<title>Index of', resp.text, re.I):
            return True
    except Exception:
        pass
    return False
