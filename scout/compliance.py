"""
Scout Compliance Checker
Checks security findings against various compliance frameworks.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class ComplianceFramework(Enum):
    """Supported compliance frameworks."""
    OWASP_TOP10 = "owasp_top10"
    NIST_CSF = "nist_csf"
    ISO_27001 = "iso_27001"
    PCI_DSS = "pci_dss"
    SOC2 = "soc2"
    HIPAA = "hipaa"
    GDPR = "gdpr"


@dataclass
class ComplianceRule:
    """Represents a compliance rule."""
    framework: ComplianceFramework
    rule_id: str
    title: str
    description: str
    severity: str
    control_mappings: List[str]


class ComplianceChecker:
    """Advanced compliance checking against multiple frameworks."""

    def __init__(self):
        self.rules = self._load_compliance_rules()

    def _load_compliance_rules(self) -> Dict[str, ComplianceRule]:
        """Load compliance rules for all supported frameworks."""
        rules = {}

        # OWASP Top 10 2021
        rules['owasp_a01'] = ComplianceRule(
            framework=ComplianceFramework.OWASP_TOP10,
            rule_id='A01:2021',
            title='Broken Access Control',
            description='Failures related to access control enforcement',
            severity='high',
            control_mappings=[
                'directory_traversal',
                'open_redirect',
                'sensitive_files'
            ]
        )

        rules['owasp_a03'] = ComplianceRule(
            framework=ComplianceFramework.OWASP_TOP10,
            rule_id='A03:2021',
            title='Injection',
            description='SQL injection, XSS, and other injection flaws',
            severity='critical',
            control_mappings=[
                'sql_injection',
                'xss_vulnerability'
            ]
        )

        rules['owasp_a05'] = ComplianceRule(
            framework=ComplianceFramework.OWASP_TOP10,
            rule_id='A05:2021',
            title='Security Misconfiguration',
            description=(
                'Insecure default configurations and missing security headers'
            ),
            severity='medium',
            control_mappings=[
                'missing_xframe',
                'missing_csp',
                'missing_hsts',
                'directory_listing'
            ]
        )

        rules['owasp_a02'] = ComplianceRule(
            framework=ComplianceFramework.OWASP_TOP10,
            rule_id='A02:2021',
            title='Cryptographic Failures',
            description='Failures related to cryptography and data protection',
            severity='high',
            control_mappings=[
                'weak_ssl',
                'missing_hsts'
            ]
        )

        # NIST Cybersecurity Framework
        rules['nist_pr_ac'] = ComplianceRule(
            framework=ComplianceFramework.NIST_CSF,
            rule_id='PR.AC',
            title='Identity Management and Access Control',
            description=(
                'Access to physical and logical assets is limited to authorized users'
            ),
            severity='high',
            control_mappings=[
                'directory_traversal',
                'open_redirect',
                'sensitive_files'
            ]
        )

        rules['nist_pr_ds'] = ComplianceRule(
            framework=ComplianceFramework.NIST_CSF,
            rule_id='PR.DS',
            title='Data Security',
            description=(
                'Information and records are managed consistent with risk strategy'
            ),
            severity='high',
            control_mappings=[
                'weak_ssl',
                'missing_hsts',
                'sensitive_files'
            ]
        )

        rules['nist_pr_pt'] = ComplianceRule(
            framework=ComplianceFramework.NIST_CSF,
            rule_id='PR.PT',
            title='Protective Technology',
            description=(
                'Technical security solutions are managed to ensure protection'
            ),
            severity='medium',
            control_mappings=[
                'missing_xframe',
                'missing_csp',
                'directory_listing'
            ]
        )

        # PCI DSS
        rules['pci_req_6'] = ComplianceRule(
            framework=ComplianceFramework.PCI_DSS,
            rule_id='Requirement 6',
            title='Secure Application Development',
            description='Develop and maintain secure systems and applications',
            severity='critical',
            control_mappings=[
                'sql_injection',
                'xss_vulnerability',
                'missing_csp'
            ]
        )

        rules['pci_req_4'] = ComplianceRule(
            framework=ComplianceFramework.PCI_DSS,
            rule_id='Requirement 4',
            title='Encrypt Data Transmission',
            description=(
                'Encrypt transmission of cardholder data across open networks'
            ),
            severity='critical',
            control_mappings=[
                'weak_ssl',
                'missing_hsts'
            ]
        )

        # ISO 27001
        rules['iso_a12_6'] = ComplianceRule(
            framework=ComplianceFramework.ISO_27001,
            rule_id='A.12.6',
            title='Management of Technical Vulnerabilities',
            description=(
                'Information about technical vulnerabilities should be obtained'
            ),
            severity='medium',
            control_mappings=[
                'sql_injection',
                'xss_vulnerability',
                'directory_traversal'
            ]
        )

        rules['iso_a13_1'] = ComplianceRule(
            framework=ComplianceFramework.ISO_27001,
            rule_id='A.13.1',
            title='Network Controls',
            description='Networks should be managed and controlled',
            severity='medium',
            control_mappings=[
                'weak_ssl',
                'missing_hsts'
            ]
        )

        # SOC 2
        rules['soc2_cc6'] = ComplianceRule(
            framework=ComplianceFramework.SOC2,
            rule_id='CC6.1',
            title='Logical and Physical Access Controls',
            description='Restrict logical and physical access',
            severity='high',
            control_mappings=[
                'directory_traversal',
                'sensitive_files',
                'directory_listing'
            ]
        )

        rules['soc2_cc6_7'] = ComplianceRule(
            framework=ComplianceFramework.SOC2,
            rule_id='CC6.7',
            title='Data Transmission Controls',
            description='Protect data during transmission',
            severity='high',
            control_mappings=[
                'weak_ssl',
                'missing_hsts'
            ]
        )

        return rules

    def check_compliance(
        self,
        findings: List[Dict[str, Any]],
        frameworks: Optional[List[ComplianceFramework]] = None
    ) -> Dict[str, Any]:
        """
        Check findings against compliance frameworks.
        """
        if frameworks is None:
            frameworks = list(ComplianceFramework)

        compliance_report: Dict[str, Any] = {
            'summary': {},
            'violations': {},
            'recommendations': []
        }

        # Initialize framework summaries
        for framework in frameworks:
            compliance_report['summary'][framework.value] = {
                'total_rules': 0,
                'violated_rules': 0,
                'compliance_score': 0.0
            }
            compliance_report['violations'][framework.value] = []

        # Analyze each finding
        for finding in findings:
            finding_text = finding.get('finding', '').lower()

            for rule_id, rule in self.rules.items():
                if rule.framework not in frameworks:
                    continue

                # Check if finding matches this rule's control mappings
                if self._matches_control_mappings(
                    finding_text,
                    rule.control_mappings
                ):
                    violation = {
                        'rule_id': rule.rule_id,
                        'title': rule.title,
                        'finding': finding.get('finding'),
                        'target': finding.get('target'),
                        'severity': rule.severity,
                        'description': rule.description
                    }
                    compliance_report['violations'][rule.framework.value].append(
                        violation
                    )

        # Calculate compliance scores
        for framework in frameworks:
            framework_rules = [
                r for r in self.rules.values() if r.framework == framework
            ]
            total_rules = len(framework_rules)
            violated_rules = len(compliance_report['violations'][framework.value])

            compliance_report['summary'][framework.value]['total_rules'] = (
                total_rules
            )
            compliance_report['summary'][framework.value]['violated_rules'] = (
                violated_rules
            )

            if total_rules > 0:
                score = ((total_rules - violated_rules) / total_rules) * 100
                compliance_report['summary'][framework.value][
                    'compliance_score'
                ] = round(score, 2)

        # Generate recommendations
        compliance_report['recommendations'] = (
            self._generate_compliance_recommendations(
                compliance_report['violations']
            )
        )

        return compliance_report

    def _matches_control_mappings(
        self,
        finding_text: str,
        control_mappings: List[str]
    ) -> bool:
        """
        Check if finding matches any of the control mappings.
        """
        # Define mapping keywords for each control
        control_keywords = {
            'sql_injection': ['sql injection', 'sqli'],
            'xss_vulnerability': ['xss', 'cross-site scripting'],
            'directory_traversal': ['directory traversal', 'path traversal'],
            'open_redirect': ['open redirect'],
            'sensitive_files': ['sensitive files', 'exposed'],
            'missing_xframe': ['x-frame-options', 'missing'],
            'missing_csp': ['content-security-policy', 'missing'],
            'missing_hsts': ['strict-transport-security', 'missing'],
            'directory_listing': ['directory listing'],
            'weak_ssl': ['ssl', 'tls', 'weak protocol']
        }

        for control in control_mappings:
            keywords = control_keywords.get(control, [])
            if any(keyword in finding_text for keyword in keywords):
                return True

        return False

    def _generate_compliance_recommendations(
        self,
        violations: Dict[str, List[Dict[str, Any]]]
    ) -> List[str]:
        """
        Generate compliance recommendations based on violations.
        """
        recommendations = []

        # Count violations by severity across all frameworks
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}

        for framework_violations in violations.values():
            for violation in framework_violations:
                severity = violation.get('severity', 'medium')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Generate priority recommendations
        if severity_counts['critical'] > 0:
            critical_count = severity_counts['critical']
            recommendations.append(
                f"URGENT: Address {critical_count} critical compliance "
                f"violations immediately"
            )

        if severity_counts['high'] > 0:
            recommendations.append(
                f"HIGH PRIORITY: Remediate {severity_counts['high']} "
                f"high-severity violations within 7 days"
            )

        if severity_counts['medium'] > 0:
            recommendations.append(
                f"MEDIUM PRIORITY: Plan remediation for "
                f"{severity_counts['medium']} medium-severity violations"
            )

        # Framework-specific recommendations
        for framework, framework_violations in violations.items():
            if framework_violations:
                recommendations.append(
                    f"Review {framework.upper()} compliance requirements "
                    f"and implement missing controls"
                )

        return recommendations

    def generate_compliance_matrix(
        self,
        findings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate a compliance matrix showing coverage across frameworks."""
        matrix: Dict[str, Any] = {}

        for framework in ComplianceFramework:
            matrix[framework.value] = {
                'rules': [],
                'coverage': 0.0
            }

            framework_rules = [
                r for r in self.rules.values() if r.framework == framework
            ]
            for rule in framework_rules:
                rule_coverage = {
                    'rule_id': rule.rule_id,
                    'title': rule.title,
                    'covered': False,
                    'findings': []
                }

                # Check if any findings relate to this rule
                for finding in findings:
                    if self._matches_control_mappings(
                        finding.get('finding', '').lower(),
                        rule.control_mappings
                    ):
                        rule_coverage['covered'] = True
                        rule_coverage['findings'].append(finding.get('finding'))

                matrix[framework.value]['rules'].append(rule_coverage)

            # Calculate coverage percentage
            total_rules = len(framework_rules)
            covered_rules = sum(
                1 for r in matrix[framework.value]['rules'] if r['covered']
            )

            if total_rules > 0:
                matrix[framework.value]['coverage'] = (
                    covered_rules / total_rules
                ) * 100

        return matrix


# Global compliance checker instance
compliance_checker = ComplianceChecker()
