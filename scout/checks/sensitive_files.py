import requests
from urllib.parse import urljoin


def check_sensitive_files(base_url):
    """Check for sensitive files."""
    sensitive_files = [
        '/.env', '/.git/config', '/config.php', '/wp-config.php',
        '/database.yml', '/secrets.yml', '/.htaccess', '/robots.txt'
    ]
    
    found_files = []
    for file_path in sensitive_files:
        try:
            url = urljoin(base_url, file_path)
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                found_files.append(url)
        except Exception:
            continue
    
    return found_files
