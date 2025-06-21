import socket
import ssl
from urllib.parse import urlparse


def check_https_implementation(url):
    """Check HTTPS implementation and SSL certificate."""
    parsed = urlparse(url)
    hostname = parsed.hostname
    context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
    try:
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                protocol = ssock.version()
                weak_protocols = ['SSLv2', 'SSLv3', 'TLSv1', 'TLSv1.1']
                if protocol in weak_protocols:
                    return True, cert, f"Weak protocol: {protocol}"
                return True, cert, None
    except Exception:
        return False, None, None
