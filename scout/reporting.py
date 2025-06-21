"""
Scout Reporting Module
Provides advanced reporting functionality with multiple output formats.
"""
import csv
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import yaml
from fpdf import FPDF


class ReportGenerator:
    """
    Advanced report generator with multiple output formats."""

    def __init__(self):
        self.timestamp = datetime.now()

    def generate_json_report(
        self, data: List[Dict[str, Any]], output_file: Optional[str] = None
    ) -> str:
        """
        Generate a JSON report."""
        if not output_file:
            output_file = (
                f'scout_report_{self.timestamp.strftime("%Y%m%d_%H%M%S")}.json'
            )

        report = {
            'metadata': {
                'tool': 'Scout CLI',
                'version': '1.0.0',
                'timestamp': self.timestamp.isoformat(),
                'total_findings': len(data) if isinstance(data, list) else 1
            },
            'findings': data
        }

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        return output_file

    def generate_html_report(
        self, data: List[Dict[str, Any]], output_file: Optional[str] = None
    ) -> str:
        """Generate an interactive HTML report with charts."""
        if not output_file:
            output_file = (
                f'scout_report_{self.timestamp.strftime("%Y%m%d_%H%M%S")}.html'
            )

        if isinstance(data, dict):
            data = [data]

        # Count findings by severity
        severity_counts: Dict[str, int] = {}
        for item in data:
            severity = item.get('severity', 'unknown')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Scout Security Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{
            background: #2c3e50; color: white; padding: 20px;
            border-radius: 8px;
        }}
        .summary {{
            background: #ecf0f1; padding: 15px; margin: 20px 0;
            border-radius: 8px;
        }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #3498db; color: white; }}
        .high {{ background-color: #e74c3c; color: white; }}
        .medium {{ background-color: #f39c12; color: white; }}
        .low {{ background-color: #27ae60; color: white; }}
        .chart-container {{ width: 500px; margin: 20px auto; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Scout Security Assessment Report</h1>
        <p>Generated on: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="summary">
        <h3>Executive Summary</h3>
        <p>Total Findings: {len(data)}</p>
        <p>High Severity: {severity_counts.get('high', 0)}</p>
        <p>Medium Severity: {severity_counts.get('medium', 0)}</p>
        <p>Low Severity: {severity_counts.get('low', 0)}</p>
    </div>

    <h2>Detailed Findings</h2>
    <table>
        <tr>
            <th>Target</th>
            <th>Finding</th>
            <th>Severity</th>
            <th>Risk Score</th>
        </tr>
"""

        for item in data:
            severity = item.get('severity', 'unknown')
            risk_score = {'high': 9, 'medium': 5, 'low': 2}.get(severity, 0)
            html_template += f"""
        <tr class="{severity}">
            <td>{item.get('target', 'N/A')}</td>
            <td>{item.get('finding', 'N/A')}</td>
            <td>{item.get('severity', 'N/A')}</td>
            <td>{risk_score}</td>
        </tr>
"""

        html_template += """
    </table>
    <div class="chart-container">
        <canvas id="severityChart"></canvas>
    </div>
    <script>
        const ctx = document.getElementById('severityChart').getContext('2d');
        new Chart(ctx, {{
            type: 'doughnut',
            data: {{
                labels: ['High', 'Medium', 'Low', 'Unknown'],
                datasets: [{{
                    label: 'Findings by Severity',
                    data: [
                        {severity_counts.get('high', 0)},
                        {severity_counts.get('medium', 0)},
                        {severity_counts.get('low', 0)},
                        {severity_counts.get('unknown', 0)}
                    ],
                    backgroundColor: [
                        '#e74c3c', '#f39c12', '#27ae60', '#95a5a6'
                    ]
                }}]
            }}
        }});
    </script>
</body>
</html>
"""

        with open(output_file, 'w') as f:
            f.write(html_template)
        return output_file

    def generate_csv_report(
        self, data: List[Dict[str, Any]], output_file: Optional[str] = None
    ) -> str:
        """Generate a CSV report."""
        if not output_file:
            output_file = (
                f'scout_report_{self.timestamp.strftime("%Y%m%d_%H%M%S")}.csv'
            )

        if isinstance(data, dict):
            data = [data]

        with open(output_file, 'w', newline='') as f:
            if not data:
                f.write("No data to report.")
                return output_file

            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        return output_file

    def generate_pdf_report(
        self, data: List[Dict[str, Any]], output_file: Optional[str] = None
    ) -> str:
        """Generate a PDF report."""
        if not output_file:
            output_file = (
                f'scout_report_{self.timestamp.strftime("%Y%m%d_%H%M%S")}.pdf'
            )

        if isinstance(data, dict):
            data = [data]

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)

        pdf.cell(0, 10, 'Scout Security Assessment Report', 0, 1, 'C')
        pdf.set_font('Arial', '', 10)
        pdf.cell(
            0, 8, f'Generated: {self.timestamp.strftime("%Y-%m-%d %H:%M:%S")}',
            ln=True
        )
        pdf.ln(10)

        # Summary
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'Executive Summary', ln=True)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 8, f'Total Findings: {len(data)}', ln=True)

        severity_counts: Dict[str, int] = {}
        for item in data:
            severity = item.get('severity', 'unknown')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        for severity, count in severity_counts.items():
            pdf.cell(
                0, 8, f'{severity.title()} Severity Issues: {count}', ln=True
            )
        pdf.ln(10)

        # Detailed Findings
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Detailed Findings', 0, 1)
        pdf.set_font('Arial', '', 8)

        for item in data:
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 8, f"Target: {item.get('target', 'N/A')}", ln=True)
            pdf.set_font('Arial', '', 8)
            for key, value in item.items():
                pdf.multi_cell(
                    0,
                    6,
                    f'{key.title()}: {str(value)[:80]}'
                    f'{"..." if len(str(value)) > 80 else ""}',
                )
            pdf.ln(5)

        pdf.output(output_file)
        return output_file

    def generate_yaml_report(
        self, data: List[Dict[str, Any]], output_file: Optional[str] = None
    ) -> str:
        """Generate a YAML report."""
        if not output_file:
            output_file = (
                f'scout_report_{self.timestamp.strftime("%Y%m%d_%H%M%S")}.yaml'
            )

        report = {
            'metadata': {
                'tool': 'Scout CLI',
                'version': '1.0.0',
                'timestamp': self.timestamp.isoformat(),
                'total_findings': len(data) if isinstance(data, list) else 1
            },
            'findings': data
        }

        with open(output_file, 'w') as f:
            yaml.dump(report, f, default_flow_style=False)
        return output_file


def generate_report(
    data: List[Dict[str, Any]], format_type: str, output_file: Optional[str] = None
) -> str:
    """Factory function to generate a report in the specified format."""
    generator = ReportGenerator()

    if format_type == 'json':
        return generator.generate_json_report(data, output_file)
    elif format_type == 'html':
        return generator.generate_html_report(data, output_file)
    elif format_type == 'csv':
        return generator.generate_csv_report(data, output_file)
    elif format_type == 'pdf':
        return generator.generate_pdf_report(data, output_file)
    elif format_type == 'yaml':
        return generator.generate_yaml_report(data, output_file)
    else:
        raise ValueError(f"Unsupported report format: {format_type}")
