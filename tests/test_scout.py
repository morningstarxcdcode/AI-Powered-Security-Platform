"""
Scout CLI Test Suite
Comprehensive tests for all Scout functionality.
"""
import pytest
import tempfile
import os
from unittest.mock import MagicMock, Mock, patch
from click.testing import CliRunner
from scout.cli import cli
from scout.vulnerability_db import Vulnerability, vuln_db
from scout.compliance import ComplianceFramework, compliance_checker
from scout.config import ScoutConfig
from scout.reporting import ReportGenerator, analyze_findings

    def estVulnerabilityDatabase:
    """
Test vulnerability database functionality."""

    def test_vulnerability_creation(self):
        """
Test vulnerability object creation."""
        vuln = Vulnerability(
            id='TEST - 001',
            name='Test Vulnerability',
            description='Test description',
            severity='high',
            category='test'
        )
        assert vuln.id == 'TEST - 001'
        assert vuln.severity == 'high'
        assert vuln.category == 'test'

    def test_analyze_finding_sql_injection(self):
        """
Test SQL injection detection."""
        finding = "Potential SQL Injection vulnerability detected"
        vuln = vuln_db.analyze_finding(finding)
        assert vuln is not None
        assert vuln.id == 'SCOUT - 004'
        assert vuln.name == 'SQL Injection Vulnerability'
        assert vuln.severity == 'critical'

    def test_analyze_finding_xss(self):
        """Test XSS detection."""
        finding = "Cross - Site Scripting (XSS) vulnerability found"
        vuln = vuln_db.analyze_finding(finding)
        assert vuln is not None
        assert vuln.id == 'SCOUT - 005'
        assert vuln.severity == 'high'

    def test_analyze_finding_missing_header(self):
        """Test missing header detection."""
        finding = "Missing X - Frame - Options header"
        vuln = vuln_db.analyze_finding(finding)
        assert vuln is not None
        assert vuln.id == 'SCOUT - 001'
        assert vuln.severity == 'medium'

    def test_analyze_finding_no_match(self):
        """Test unknown finding."""
        finding = "Unknown security issue"
        vuln = vuln_db.analyze_finding(finding)
        assert vuln is None

    def test_export_sarif(self):
        """Test SARIF export functionality."""
        findings = [
            {'finding': 'SQL injection vulnerability', 'target': 'example.com'},
            {'finding': 'Missing X - Frame - Options header', 'target': 'example.com'}
        ]
        sarif = vuln_db.export_sarif(findings)

        assert sarif['version'] == '2.1.0'
        assert 'runs' in sarif
        assert len(sarif['runs'][0]['results']) >= 1

    def test_generate_remediation_plan(self):
        """
Test remediation plan generation."""
        findings = [
            {'finding': 'SQL injection vulnerability', 'target': 'example.com'},
            {'finding': 'Missing X - Frame - Options header', 'target': 'example.com'}
        ]
        plan = vuln_db.generate_remediation_plan(findings)

        assert 'critical' in plan
        assert 'medium' in plan
        assert len(plan['critical']) >= 1
        assert len(plan['medium']) >= 1

    def estComplianceChecker:
    """
Test compliance checking functionality."""

    def test_check_compliance_owasp(self):
        """
Test OWASP Top 10 compliance checking."""
        findings = [
            {'finding': 'SQL injection vulnerability', 'target': 'example.com'},
            {'finding': 'Missing Content - Security - Policy header', 'target': 'example.com'}
        ]

        result = compliance_checker.check_compliance(findings, [ComplianceFramework.OWASP_TOP10])

        assert 'summary' in result
        assert 'violations' in result
        assert 'owasp_top10' in result['summary']
        assert result['summary']['owasp_top10']['violated_rules'] >= 1

    def test_compliance_matrix(self):
        """
Test compliance matrix generation."""
        findings = [
            {'finding': 'SQL injection vulnerability', 'target': 'example.com'}
        ]

        matrix = compliance_checker.generate_compliance_matrix(findings)

        assert 'owasp_top10' in matrix
        assert 'coverage' in matrix['owasp_top10']
        assert 'rules' in matrix['owasp_top10']

    def test_compliance_recommendations(self):
        """
Test compliance recommendations."""
        violations = {
            'owasp_top10': [
                {'severity': 'critical', 'rule_id': 'A03:2021'},
                {'severity': 'high', 'rule_id': 'A01:2021'}
            ]
        }

        recommendations = compliance_checker._generate_compliance_recommendations(violations)

        assert len(recommendations) > 0
        assert any('URGENT' in rec for rec in recommendations)

    def estReporting:
    """
Test reporting functionality."""

    def test_generate_json_report(self):
        """
Test JSON report generation."""
        generator = ReportGenerator()
        data = [{'target': 'example.com', 'finding': 'Test finding', 'severity': 'medium'}]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'test_report.json')
            result_file = generator.generate_json_report(data, output_file)

            assert os.path.exists(result_file)
            with open(result_file) as f:
                report = json.load(f)

            assert 'metadata' in report
            assert 'findings' in report
            assert report['metadata']['total_findings'] == 1

    def test_generate_html_report(self):
        """
Test HTML report generation."""
        generator = ReportGenerator()
        data = [{'target': 'example.com', 'finding': 'Test finding', 'severity': 'high'}]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'test_report.html')
            result_file = generator.generate_html_report(data, output_file)

            assert os.path.exists(result_file)
            with open(result_file) as f:
                content = f.read()

            assert 'Scout Security Assessment Report' in content
            assert 'Chart.js' in content
            assert 'Test finding' in content

    def test_analyze_findings(self):
        """
Test findings analysis."""
        data = [
            {'severity': 'critical'},
            {'severity': 'high'},
            {'severity': 'medium'}
        ]

        analysis = analyze_findings(data)

        assert analysis['total_findings'] == 3
        assert analysis['severity_breakdown']['critical'] == 1
        assert analysis['severity_breakdown']['high'] == 1
        assert analysis['risk_score'] > 0
        assert 'risk_level' in analysis

    def estConfig:
    """
Test configuration management."""

    def test_config_creation(self):
        """
Test config object creation."""
        config = ScoutConfig()
        assert config.get('scan.timeout') == 10
        assert config.get('scan.user_agent') == 'Scout / 1.0'

    def test_config_get_with_default(self):
        """
Test config get with default value."""
        config = ScoutConfig()
        value = config.get('nonexistent.key', 'default_value')
        assert value == 'default_value'

    def test_config_set_and_get(self):
        """
Test config set and get."""
        config = ScoutConfig()
        config.set('test.key', 'test_value')
        assert config.get('test.key') == 'test_value'

    def test_config_validation(self):
        """
Test config validation."""
        config = ScoutConfig()
        assert config.validate() is True

    @patch.dict(os.environ, {'SCOUT_SCAN_TIMEOUT': '30'})
    def test_environment_override(self):
        """
Test environment variable override."""
        config = ScoutConfig()
        assert config.get('scan.timeout') == 30

    def estCLICommands:
    """
Test CLI command functionality."""

    def setUp(self):
        """
Set up test environment."""
        self.runner = CliRunner()

    def test_help_command(self):
        """
Test help command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Scout: Advanced Security Reconnaissance CLI Tool' in result.output

    def test_vuln_info_command(self):
        """
Test vulnerability info command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['vuln - info'])
        assert result.exit_code == 0
        assert 'Vulnerability Database Information' in result.output

    def test_compliance_info_command(self):
        """
Test compliance info command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['compliance - info'])
        assert result.exit_code == 0
        assert 'Supported Compliance Frameworks' in result.output

    def test_plugins_command(self):
        """
Test plugins command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['plugins'])
        assert result.exit_code == 0
        assert 'Built - in Plugins' in result.output

    @patch('scout.commands.secrets.load_secrets')
    @patch('scout.commands.secrets.save_secrets')
    def test_secrets_command(self, mock_save, mock_load):
        """
Test secrets management command."""
        mock_load.return_value = {}
        runner = CliRunner()

        # Test setting a secret
        result = runner.invoke(cli, ['secrets', '--set', 'test_key=test_value'])
        assert result.exit_code == 0
        assert 'saved' in result.output

    def test_user_list_command(self):
        """
Test user list command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['user', 'list'])
        assert result.exit_code == 0

    def estSecurityChecks:
    """
Test individual security check modules."""

    @patch('requests.get')
    def test_headers_check(self, mock_get):
        """
Test headers security check."""
        from scout.checks.headers import check_headers

        mock_response = Mock()
        mock_response.headers = {}
        mock_response.cookies = []

        findings, recommended = check_headers(mock_response)

        assert 'Missing X - Frame - Options header' in findings
        assert 'Missing Content - Security - Policy header' in findings
        assert len(recommended) > 0

    @patch('requests.get')
    def test_sql_injection_check(self, mock_get):
        """
Test SQL injection check."""
        from scout.checks.sqli import check_sqli

        # Mock vulnerable response
        mock_response = Mock()
        mock_response.text = 'mysql syntax error'
        mock_get.return_value = mock_response

        result = check_sqli('http://example.com')
        assert result is True

    @patch('requests.get')
    def test_xss_check(self, mock_get):
        """
Test XSS check."""
        from scout.checks.xss import check_xss

        # Mock vulnerable response
        mock_response = Mock()
        mock_response.text = '<script > alert(1)</script>'
        mock_get.return_value = mock_response

        result = check_xss('http://example.com')
        assert result is True

    def estIntegrationTests:
    """
Integration tests for complete workflows."""

    @patch('requests.get')
    def test_full_webscan_workflow(self, mock_get):
        """
Test complete webscan workflow."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Server': 'Apache / 2.4.41'}
        mock_response.cookies = []
        mock_response.text = 'Normal page content'
        mock_get.return_value = mock_response

        runner = CliRunner()
        result = runner.invoke(cli, ['webscan', 'http://example.com'])

        assert result.exit_code == 0
        assert 'Scanning http://example.com' in result.output

    @patch('requests.get')
    def test_assess_command_workflow(self, mock_get):
        """
Test assess command workflow."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.cookies = []
        mock_response.text = 'Normal page content'
        mock_get.return_value = mock_response

        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'assessment.json')
            result = runner.invoke(cli, [
                'assess',
                '--target', 'http://example.com',
                '--format', 'json',
                '--output', output_file
            ])

            assert result.exit_code == 0
            assert 'Assessment completed successfully' in result.output

    def estErrorHandling:
    """
Test error handling and edge cases."""

    def test_invalid_target_handling(self):
        """
Test handling of invalid targets."""
        runner = CliRunner()
        result = runner.invoke(cli, ['webscan', 'invalid - url'])
        # Should handle gracefully without crashing
        assert result.exit_code == 0

    def test_network_error_handling(self):
        """
Test network error handling."""
        runner = CliRunner()
        result = runner.invoke(cli, ['webscan', 'http://nonexistent - domain - 12345.com'])
        # Should handle network errors gracefully
        assert result.exit_code == 0

    def test_config_file_missing(self):
        """
Test behavior when config file is missing."""
        config = ScoutConfig('nonexistent_config.yaml')
        # Should still work with defaults
        assert config.get('scan.timeout') == 10

# Performance tests

    def estPerformance:
    """
Test performance characteristics."""

    def test_vulnerability_database_performance(self):
        """
Test vulnerability database lookup performance."""
        import time

        findings = ['SQL injection vulnerability'] * 1000

        start_time = time.time()
        for finding in findings:
            vuln_db.analyze_finding(finding)
        end_time = time.time()

        # Should process 1000 findings in under 1 second
        assert (end_time - start_time) < 1.0

    def test_compliance_checking_performance(self):
        """
Test compliance checking performance."""
        import time

        findings = [
            {'finding': 'SQL injection vulnerability', 'target': 'example.com'}
        ] * 100

        start_time = time.time()
        compliance_checker.check_compliance(findings, [ComplianceFramework.OWASP_TOP10])
        end_time = time.time()

        # Should process 100 findings in under 0.5 seconds
        assert (end_time - start_time) < 0.5

    if __name__ == '__main__':
    pytest.main([__file__, '-v'])
