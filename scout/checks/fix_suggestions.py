def get_fix_suggestions(findings):
    fix_map = {
        'X - Frame - Options': 'Add X - Frame - Options: DENY or SAMEORIGIN to prevent clickjacking.',
        'Content - Security - Policy': 'Add a strong Content - Security - Policy header to mitigate XSS.',
        'Strict - Transport - Security': 'Add Strict - Transport - Security for HTTPS to enforce secure connections.',
        'X - Content - Type - Options': 'Add X - Content - Type - Options: nosniff to prevent MIME sniffing.',
        'HTTPS': 'Enable HTTPS with a valid certificate and redirect all HTTP traffic to HTTPS.',
        'Directory listing': 'Disable directory listing in your web server configuration.',
        'Sensitive files': 'Restrict access to sensitive files using server rules or .htaccess.',
        'HTTP methods': 'Disable risky HTTP methods (TRACE, PUT, DELETE, CONNECT) in your server config.',
    }
    suggestions = []
    for f in findings:
        for k, v in fix_map.items():
            if k.lower() in f.lower() and v not in suggestions:
                suggestions.append(v)
    return suggestions
