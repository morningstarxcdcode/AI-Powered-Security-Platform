"""
Test Scout Compliance functionality
"""
from scout.compliance import (
    ComplianceChecker,
    ComplianceFramework,
    ComplianceRule,
    compliance_checker,
)


class TestCompliance:
    """Test compliance functionality."""

    def test_compliance_checker_initialization(self):
        """Test compliance checker initialization."""
        checker = ComplianceChecker()
        assert len(checker.rules) > 0
        assert any('owasp' in rule_id for rule_id in checker.rules.keys())

    def test_compliance_frameworks(self):
        """Test compliance frameworks enum."""
        assert ComplianceFramework.OWASP_TOP10.value == "owasp_top10"
        assert ComplianceFramework.NIST_CSF.value == "nist_csf"
        assert ComplianceFramework.PCI_DSS.value == "pci_dss"

    def test_check_compliance_sql_injection(self):
        """Test compliance checking for SQL injection."""
        findings = [
            {
                'finding': 'SQL injection vulnerability detected',
                'target': 'https://example.com/login'
            }
        ]
        
        result = compliance_checker.check_compliance(findings)
        
        assert 'summary' in result
        assert 'violations' in result
        assert 'recommendations' in result

    def test_check_compliance_xss(self):
        """Test compliance checking for XSS."""
        findings = [
            {
                'finding': 'Cross-site scripting vulnerability found',
                'target': 'https://example.com/search'
            }
        ]
        
        result = compliance_checker.check_compliance(findings)
        
        # Should detect OWASP violations
        owasp_violations = result['violations'].get('owasp_top10', [])
        assert len(owasp_violations) > 0

    def test_compliance_matrix_generation(self):
        """Test compliance matrix generation."""
        findings = [
            {
                'finding': 'SQL injection detected',
                'target': 'https://example.com'
            }
        ]
        
        matrix = compliance_checker.generate_compliance_matrix(findings)
        
        assert 'owasp_top10' in matrix
        assert 'nist_csf' in matrix
        assert 'rules' in matrix['owasp_top10']
        assert 'coverage' in matrix['owasp_top10']

    def test_compliance_rule_creation(self):
        """Test compliance rule creation."""
        rule = ComplianceRule(
            framework=ComplianceFramework.OWASP_TOP10,
            rule_id='A01:2021',
            title='Broken Access Control',
            description='Test description',
            severity='high',
            control_mappings=['directory_traversal']
        )
        
        assert rule.framework == ComplianceFramework.OWASP_TOP10
        assert rule.rule_id == 'A01:2021'
        assert rule.severity == 'high'
        assert 'directory_traversal' in rule.control_mappings
