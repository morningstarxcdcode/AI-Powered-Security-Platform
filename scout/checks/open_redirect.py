from urllib.parse import urlencode, urlparse

import requests


def is_open_redirect(url):
    # Try common open redirect parameters
    params = ['next', 'url', 'redirect', 'return', 'dest', 'destination']
    test_domain = 'evil.com'
    for param in params:
        if '?' in url:
            test_url = url + f'&{param}=http://{test_domain}'
        else:
            test_url = url + f'?{param}=http://{test_domain}'
        try:
            resp = requests.get(test_url, allow_redirects=False, timeout=5)
            loc = resp.headers.get('Location', '')
            if test_domain in loc:
                return True
        except Exception:
            continue
    return False
