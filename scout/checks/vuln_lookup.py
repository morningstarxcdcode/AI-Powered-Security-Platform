import requests


def lookup_vulnerability(cve_id):
    """Look up vulnerability information by CVE ID."""
    try:
        url = f"https://cve.mitre.org/cgi-bin/cvename.cgi?name={cve_id}"
        resp = requests.get(url, timeout=10)
        return resp.status_code == 200
    except Exception:
        return False
