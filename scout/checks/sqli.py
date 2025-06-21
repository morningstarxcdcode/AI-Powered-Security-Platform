import requests


def check_sql_injection(url):
    """Check for SQL injection vulnerabilities."""
    payloads = ["'", "1' OR '1'='1", "'; DROP TABLE users; --"]
    
    for payload in payloads:
        try:
            test_url = f"{url}?id={payload}"
            resp = requests.get(test_url, timeout=5)
            
            # Look for SQL error indicators
            error_indicators = ["sql", "mysql", "postgres", "oracle", "sqlite", "syntax error"]
            if any(indicator in resp.text.lower() for indicator in error_indicators):
                return True
                
        except Exception:
            continue
    
    return False
